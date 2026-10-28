#!/usr/bin/env python3
"""Shotbird board server (localhost only).

  /                      -> board UI (projects home, or ?p=<slug> for one project)
  /board/<file>          -> board assets from this skill's board/ folder
  /p/<slug>/<path>       -> files inside a project (state.json, frames, sheets, bible)
  /api/projects          -> list of projects with a state.json
  /api/crew              -> each agent's skills and preflight skill card
  /api/status            -> whether the headless Claude Code login is ready
  GET  /api/p/<slug>/chat?since=N   -> chat rows from N, plus whether the orchestrator is running
  GET  /api/p/<slug>/gallery        -> every variation of every cast item (state history + files on disk), with verdicts
  POST /api/p/<slug>/chat {text}    -> send a message to the orchestrator (queued if it is busy)
  POST /api/p/<slug>/stop           -> stop the running orchestrator turn
  POST /api/p/<slug>/feedback       -> a board click on one gen: approve / disapprove / changes (shot+v, or cast id+image)
  POST /api/p/<slug>/edit {kind, id, v|image, prompt, mask} -> area edit: the marked area changes, nothing else
  POST /api/p/<slug>/models|mode    -> save the model picker / switch Always ask <-> Autopilot
  POST /api/p/<slug>/upload?name=F  -> raw file body (brief .md/.txt/.pdf/.docx, reference .mp4/.mov, images) -> 00-inbox/
  POST /api/p/<slug>/export {doc}   -> film bible -> 05-lore/film-bible.pdf (headless Chrome prints /print?p=<slug>)
  POST /api/p/<slug>/open {path, reveal} -> open a project file in its Mac app, or show it in Finder
  GET  /print?p=<slug>              -> print layout of the film bible
  POST /api/new {text, models, mode, aspect} -> create a project from a brief and hand it to the orchestrator
  GET  /login · POST /api/login {name, password} · GET /logout · GET /api/me -> office-network sign-in (see below)

The orchestrator is the `shotbird-producer` agent, run as a headless Claude Code session (one per project,
resumed on every message) with the user's own Claude login.

Office-network sharing (`launch.sh share`): the server listens on every interface instead of localhost only, and
teammates sign in with their name and a shared password (~/Shotbird/.share.json holds its PBKDF2 hash and a cookie
secret). Requests from this Mac never need to sign in. Teammates' messages are tagged with their name, their turns
run without the Obsidian vault, and files they "open" download to their browser instead of opening on this Mac.
"""
import argparse
import base64
import datetime as dt
import glob
import hashlib
import hmac
import json
import mimetypes
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import uuid
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, quote, unquote, urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
BOARD = os.path.join(HERE, "board")
ROOT = os.environ.get("SHOTBIRD_ROOT", os.path.expanduser("~/Shotbird"))  # ~/Shotbird is a symlink to this (Desktop is privacy-protected)
# Who the crew works for, and their Obsidian vault (optional). ~/Shotbird/.config.json overrides these defaults;
# the team installer writes it, e.g. {"name": "Sara", "vault": ""}.
try:
    _CFG = json.load(open(os.path.join(ROOT, ".config.json"), encoding="utf-8"))
except (OSError, ValueError):
    _CFG = {}
NAME = _CFG.get("name") or "{{NAME}}"
VAULT = _CFG["vault"] if "vault" in _CFG else "{{VAULT}}"
SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{0,80}$")
CREW = ["scout", "hatch", "slate", "hawk", "lore", "cue"]
AGENTS_DIR = os.path.expanduser("~/.claude/agents")
ORCHESTRATOR = "shotbird-producer"
# Model picker: Claude models for the orchestrator ("brain") and the crew; Higgsfield image model; Cue's video engine.
MODEL_CHOICES = {
    "brain": ["sonnet", "opus", "haiku"],
    "crew": ["sonnet", "opus", "haiku"],
    "image": ["seedream_v5_pro", "nano_banana_2_1", "nano_banana_2", "nano_banana_pro", "gpt_image_2_5"],
    "resolution": ["2k", "4k"],
    "video": ["auto", "seedance_2_0", "seedance_2_5", "kling_3_0", "veo_3_1", "wan_3_0"],
}
DEFAULT_MODELS = {"brain": "sonnet", "crew": "sonnet", "image": "seedream_v5_pro", "resolution": "2k", "video": "seedance_2_5"}
MAX_RES = {"seedream_v5_pro": "2k"}  # Seedream 5 Pro tops out at 2K on Higgsfield
UPLOAD_KINDS = {".md": "brief", ".txt": "brief", ".pdf": "pdf", ".docx": "doc", ".mp4": "video", ".mov": "video",
                ".m4v": "video", ".png": "image", ".jpg": "image", ".jpeg": "image", ".webp": "image"}
MAX_UPLOAD = 2 * 1024 ** 3
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SBIMG = os.path.join(HERE, "bin", "sbimg")
IMAGE_EXT = (".png", ".jpg", ".jpeg", ".webp")
MAX_EDIT = 40 * 1024 ** 2  # an area edit's mask arrives as a PNG data URL
PORT = 8777
ASPECTS = ["16:9", "9:16", "1:1", "4:5", "21:9"]


def now():
    return dt.datetime.now().isoformat(timespec="seconds")


# ----------------------------------------------------------------------------------------------
# Office-network sharing: teammates sign in with their name and a shared password
# ----------------------------------------------------------------------------------------------

SHARE_FILE = os.path.join(ROOT, ".share.json")  # written by `launch.sh share`
LOCAL = ("127.0.0.1", "::1", "::ffff:127.0.0.1")
FAILS, FAILS_LOCK = {}, threading.Lock()  # ip -> [failed sign-ins, locked until]


def share_cfg():
    """The sharing settings when sharing is on, else None."""
    try:
        c = json.load(open(SHARE_FILE, encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return c if c.get("enabled") and c.get("password") and c.get("secret") else None


def password_ok(cfg, pw):
    try:
        _, iters, salt, digest = cfg["password"].split("$")
        calc = hashlib.pbkdf2_hmac("sha256", pw.encode("utf-8"), bytes.fromhex(salt), int(iters)).hex()
    except (ValueError, KeyError):
        return False
    return hmac.compare_digest(calc, digest)


def sign(cfg, payload):
    return hmac.new(bytes.fromhex(cfg["secret"]), payload.encode(), hashlib.sha256).hexdigest()


def make_token(cfg, name, days=30):
    """A signed sign-in cookie: the teammate's name and an expiry. Setting a new password changes the secret,
    which signs everyone out."""
    p = base64.urlsafe_b64encode(json.dumps({"n": name, "e": int(time.time()) + days * 86400}).encode()).decode().rstrip("=")
    return p + "." + sign(cfg, p)


def token_name(cfg, tok):
    try:
        p, sig = tok.split(".")
        if not hmac.compare_digest(sig, sign(cfg, p)):
            return None
        d = json.loads(base64.urlsafe_b64decode(p + "=" * (-len(p) % 4)))
        return str(d["n"])[:40] if d["e"] > time.time() else None
    except (ValueError, KeyError, TypeError):
        return None


def lan_urls(port):
    """Addresses teammates can open: this Mac's network name (Bonjour) and its current IP."""
    out = []
    host = subprocess.run(["/usr/sbin/scutil", "--get", "LocalHostName"], capture_output=True, text=True).stdout.strip()
    if host:
        out.append("http://%s.local:%d" % (host, port))
    for iface in ("en0", "en1"):
        ip = subprocess.run(["/usr/sbin/ipconfig", "getifaddr", iface], capture_output=True, text=True).stdout.strip()
        if ip:
            out.append("http://%s:%d" % (ip, port))
    return out


def crew():
    """Each agent's skills (core skills and on-demand from its Skill pack) and its preflight skill card."""
    out = []
    for a in CREW:
        item = {"id": a, "preloaded": [], "on_demand": [], "own": [], "card": None, "card_updated": None}
        p = os.path.join(AGENTS_DIR, a + ".md")
        if os.path.isfile(p):
            t = open(p, encoding="utf-8").read()
            fm = re.match(r"^---\n(.*?)\n---\n", t, re.S)
            if fm:
                item["preloaded"] = re.findall(r"^  - (\S+)$", fm.group(1), re.M)
            pack = re.search(r"## Skill pack.*?(?=\n## )", t, re.S)
            body = pack.group(0) if pack else ""
            core = re.search(r"\*\*Core skills\*\*.*?(?=\n- \*\*On demand)", body, re.S)
            if core and not item["preloaded"]:
                item["preloaded"] = sorted(set(re.findall(r"`(sb-[a-z0-9]+(?:-[a-z0-9]+)*)`", core.group(0))))
            item["on_demand"] = sorted(set(re.findall(r"(?<![\w-])(sb-[a-z0-9]+(?:-[a-z0-9]+)*)", body)) - set(item["preloaded"]))
            item["own"] = sorted(set(re.findall(r"`anthropic-skills:([a-z0-9-]+)`", body)))
        c = os.path.join(ROOT, "_crew", a + ".md")
        if os.path.isfile(c):
            item["card"] = open(c, encoding="utf-8").read()[:60000]
            item["card_updated"] = dt.datetime.fromtimestamp(os.path.getmtime(c)).isoformat(timespec="minutes")
        out.append(item)
    return out


def safe_join(base, relpath):
    p = os.path.realpath(os.path.join(base, relpath))
    return p if p == base or p.startswith(os.path.realpath(base) + os.sep) else None


# ----------------------------------------------------------------------------------------------
# Orchestrator: headless Claude Code, one resumable session per project
# ----------------------------------------------------------------------------------------------

def claude_bin():
    """Newest Claude Code binary bundled with the desktop app (the path changes with each update)."""
    found = glob.glob(os.path.expanduser(
        "~/Library/Application Support/Claude/claude-code/*/*/claude.app/Contents/MacOS/claude"))
    def ver(p):
        v = p.split("/claude-code/")[1].split("/")[0]
        return tuple(int(x) if x.isdigit() else 0 for x in re.split(r"[.\-]", v))
    return sorted(found, key=ver)[-1] if found else None


def clean_env():
    env = {k: os.environ[k] for k in ("HOME", "USER", "LOGNAME", "LANG", "TMPDIR") if k in os.environ}
    env.setdefault("HOME", os.path.expanduser("~"))
    env["PATH"] = "/usr/bin:/bin:/usr/sbin:/sbin"
    return env


def auth_status():
    b = claude_bin()
    if not b:
        return {"ready": False, "reason": "Claude Code binary not found in the desktop app"}
    try:
        out = subprocess.run([b, "auth", "status"], capture_output=True, text=True, timeout=30,
                             env=clean_env(), stdin=subprocess.DEVNULL).stdout
        s = json.loads(out)
        return {"ready": bool(s.get("loggedIn")), "method": s.get("authMethod"), "bin": b}
    except Exception as e:  # noqa: BLE001 - surface any failure to the UI
        return {"ready": False, "reason": type(e).__name__, "bin": b}


class Runner:
    """Serialises orchestrator turns for one project and records the chat."""

    def __init__(self, slug):
        self.slug, self.dir = slug, os.path.join(ROOT, slug)
        self.lock = threading.Lock()
        self.queue, self.board_notes = [], []
        self.proc, self.running = None, False
        self.remote_pending = False  # a queued message came from a teammate on the network

    # chat log -------------------------------------------------------------------------------
    def chat_file(self):
        return os.path.join(self.dir, "chat.jsonl")

    def append(self, role, text, **extra):
        row = dict(t=now(), role=role, text=text, **extra)
        with self.lock:
            with open(self.chat_file(), "a", encoding="utf-8") as f:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")

    def rows(self, since=0):
        p = self.chat_file()
        if not os.path.exists(p):
            return [], 0
        with self.lock:
            lines = open(p, encoding="utf-8").read().splitlines()
        out = []
        for ln in lines[since:]:
            try:
                out.append(json.loads(ln))
            except ValueError:
                pass
        return out, len(lines)

    # session --------------------------------------------------------------------------------
    def session(self):
        p = os.path.join(self.dir, ".chat_session.json")
        return json.load(open(p)).get("session_id") if os.path.exists(p) else None

    def save_session(self, sid):
        json.dump({"session_id": sid, "updated": now()}, open(os.path.join(self.dir, ".chat_session.json"), "w"))

    # turns ----------------------------------------------------------------------------------
    def send(self, text, role="user", files=None, by=None, remote=False):
        """Queue a message for the orchestrator. `by` is who sent it; `remote` marks a teammate on the network."""
        extra = dict({"files": files} if files else {}, **({"by": by} if by else {}))
        self.append(role, text, **extra)
        msg = ("[Board] " if role == "board" else "") + (
            "[From %s, a teammate on the office network] " % by if remote else "") + text
        if files:
            msg += "\n[Attached by %s, saved in the project folder]\n" % (by or NAME) + "\n".join(
                "- %s (%s, %s)%s" % (f["path"], f["kind"], human(f["size"]),
                                     " · plain-text copy: %s" % f["text"] if f.get("text") else "") for f in files)
        with self.lock:
            self.queue.append(msg)
            self.remote_pending = self.remote_pending or remote
            start = not self.running
            if start:
                self.running = True
        if start:
            threading.Thread(target=self.loop, daemon=True).start()

    def note(self, text):
        """Board events the orchestrator should know about on its next turn (no turn of their own)."""
        self.append("board", text)
        with self.lock:
            self.board_notes.append(text)

    def stop(self):
        p = self.proc
        if p and p.poll() is None:
            p.terminate()
            self.append("system", "Stopped.")

    def loop(self):
        try:
            while True:
                with self.lock:
                    if not self.queue:
                        self.running = False
                        return
                    msgs, self.queue = self.queue, []
                    notes, self.board_notes = self.board_notes, []
                    remote, self.remote_pending = self.remote_pending, False
                self.settle()  # a status left over from an earlier turn (or a crash) isn't real
                try:
                    self.turn(msgs, notes, remote)
                finally:
                    self.settle()  # finished, stopped or crashed: nobody is working once the turn is over
        except Exception as e:  # noqa: BLE001
            self.append("error", "Orchestrator crashed: %s" % e)
            with self.lock:
                self.running = False

    def settle(self):
        """Between turns no crew agent runs, so reset any agent still marked 'working' to idle (keeping its task)."""
        try:
            agents = json.load(open(os.path.join(self.dir, "state.json"), encoding="utf-8")).get("agents") or {}
        except (OSError, ValueError):
            return
        for a, ag in agents.items():
            if a in CREW and ag.get("status") == "working":
                task = ag.get("task") or ""
                sb("agent", self.slug, a, "idle", "Not running · last task: %s" % task if task else "Not running")

    def mode(self):
        try:
            return json.load(open(os.path.join(self.dir, "state.json"), encoding="utf-8")).get("project", {}).get("mode") or "ask"
        except (OSError, ValueError):
            return "ask"

    def models(self):
        try:
            p = json.load(open(os.path.join(self.dir, "state.json"), encoding="utf-8")).get("project", {})
        except (OSError, ValueError):
            p = {}
        m = dict(DEFAULT_MODELS)
        m.update({k: v for k, v in (p.get("models") or {}).items() if k in MODEL_CHOICES and v in MODEL_CHOICES[k]})
        return m

    def turn(self, msgs, notes, remote=False):
        b = claude_bin()
        if not b:
            return self.append("error", "Claude Code was not found in the desktop app.")
        m = self.models()
        header = ("[Shotbird board] project slug=%s · folder=%s · board=http://localhost:8777/?p=%s\n"
                  "[Model choices from %s] crew=%s · image=%s · resolution=%s · video=%s (pass `model: %s` on every Agent call; "
                  "give Hatch/Slate the image model and resolution, and Cue the video engine unless it is 'auto')\n"
                  "[Mode] %s\n"
                  % (self.slug, self.dir, self.slug, NAME, m["crew"], m["image"], m["resolution"], m["video"], m["crew"],
                     "Autopilot: proceed within the approved credit cap" if self.mode() == "autopilot"
                     else "Always ask: ask before spending credits"))
        if remote:
            header += ("[Shared on the office network] Messages tagged [From <name>, a teammate…] come from teammates "
                       "using %s's Mac. For this turn: work only inside this project's folder; don't read or change %s's "
                       "Obsidian vault, memory, other projects, Shotbird itself, its skills, or anything else on this Mac; "
                       "never run commands unrelated to this project. Credits are %s's: the usual credit rules apply.\n"
                       % (NAME, NAME, NAME))
        body = "\n".join(["[Board] " + n for n in notes] + msgs)
        sid = self.session()
        cmd = [b, "-p", header + "\n" + body, "--agent", ORCHESTRATOR, "--model", m["brain"],
               "--output-format", "stream-json", "--verbose",
               "--permission-mode", "auto",
               "--add-dir", ROOT, "--add-dir", os.path.expanduser("~/.claude/skills")]
        if VAULT and os.path.isdir(VAULT) and not remote:  # teammates' turns never get the vault
            cmd += ["--add-dir", VAULT]
        if sid:
            cmd += ["--resume", sid]
        else:
            cmd += ["--session-id", str(uuid.uuid4())]  # saved only once Claude reports the session started
        log = open(os.path.join(self.dir, ".chat_stderr.log"), "a", encoding="utf-8")
        self.proc = subprocess.Popen(cmd, cwd=self.dir, env=clean_env(), stdin=subprocess.DEVNULL,
                                     stdout=subprocess.PIPE, stderr=log, text=True, bufsize=1)
        for line in self.proc.stdout:
            try:
                ev = json.loads(line)
            except ValueError:
                continue
            self.handle(ev)
        self.proc.wait()
        log.close()

    def handle(self, ev):
        t = ev.get("type")
        if t == "system" and ev.get("subtype") == "init" and ev.get("session_id"):
            self.save_session(ev["session_id"])
        elif t == "assistant" and not ev.get("parent_tool_use_id"):
            for blk in (ev.get("message") or {}).get("content") or []:
                if blk.get("type") == "text" and blk.get("text", "").strip():
                    if blk["text"].strip().startswith("Not logged in"):
                        continue  # the result handler explains the one-time login instead
                    self.append("shotbird", blk["text"].strip())
                elif blk.get("type") == "tool_use" and blk.get("name") in ("Agent", "Task"):
                    inp = blk.get("input") or {}
                    self.append("route", inp.get("description") or "", agent=inp.get("subagent_type") or "agent")
        elif t == "result":
            if ev.get("session_id") and not ev.get("is_error"):
                self.save_session(ev["session_id"])
            if ev.get("is_error"):
                msg = ev.get("result") or ev.get("terminal_reason") or "error"
                if "No conversation found" in msg:
                    sp = os.path.join(self.dir, ".chat_session.json")
                    if os.path.exists(sp):
                        os.remove(sp)
                    msg = "The previous chat session couldn't be resumed, so I've reset it. Please send your message again."
                elif "Not logged in" in msg or "/login" in msg:
                    msg = ("Shotbird's orchestrator isn't logged in yet. One-time setup: run "
                           "`sh ~/.claude/skills/shotbird/login.sh` in Terminal, sign in with your Claude account, then send your message again.")
                self.append("error", msg)


RUNNERS, RUNNERS_LOCK = {}, threading.Lock()


def runner(slug):
    with RUNNERS_LOCK:
        if slug not in RUNNERS:
            RUNNERS[slug] = Runner(slug)
        return RUNNERS[slug]


def set_models(slug, picks):
    """Validate the picker values and store them in the project's state (via sb.py, which locks writes)."""
    m = dict(DEFAULT_MODELS)
    try:
        cur = json.load(open(os.path.join(ROOT, slug, "state.json"), encoding="utf-8")).get("project", {}).get("models") or {}
        m.update({k: v for k, v in cur.items() if k in MODEL_CHOICES and v in MODEL_CHOICES[k]})
    except (OSError, ValueError):
        pass
    m.update({k: v for k, v in picks.items() if k in MODEL_CHOICES and v in MODEL_CHOICES[k]})
    if MAX_RES.get(m["image"]) == "2k":
        m["resolution"] = "2k"
    subprocess.run(["/usr/bin/python3", "-I", os.path.join(HERE, "sb.py"), "merge", slug, "project",
                    "--json", json.dumps({"models": m})], check=True, capture_output=True, text=True)
    return m


def human(n):
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return ("%d %s" if unit == "B" else "%.1f %s") % (n, unit)
        n /= 1024.0


def sb(*args):
    return subprocess.run(["/usr/bin/python3", "-I", os.path.join(HERE, "sb.py")] + [str(x) for x in args],
                          capture_output=True, text=True)


def save_upload(slug, name, rfile, length):
    """Stream an upload into <project>/00-inbox/ (never loads the whole file in memory)."""
    base = os.path.basename(name or "file")
    stem, ext = os.path.splitext(base)
    ext = ext.lower()
    if ext not in UPLOAD_KINDS:
        raise ValueError("Shotbird takes briefs (.md .txt .pdf .docx), reference videos (.mp4 .mov) and images.")
    if length <= 0 or length > MAX_UPLOAD:
        raise ValueError("Files up to 2 GB.")
    d = os.path.join(ROOT, slug, "00-inbox")
    os.makedirs(d, exist_ok=True)
    safe = re.sub(r"[^A-Za-z0-9._-]+", "-", stem).strip("-.")[:60] or "file"
    fn, i = "%s-%s%s" % (dt.datetime.now().strftime("%m%d-%H%M%S"), safe, ext), 2
    while os.path.exists(os.path.join(d, fn)):
        fn, i = "%s-%s-%d%s" % (dt.datetime.now().strftime("%m%d-%H%M%S"), safe, i, ext), i + 1
    path, left = os.path.join(d, fn), length
    with open(path + ".part", "wb") as f:
        while left > 0:
            chunk = rfile.read(min(1 << 20, left))
            if not chunk:
                break
            f.write(chunk)
            left -= len(chunk)
    if left:
        os.unlink(path + ".part")
        raise ValueError("The upload was interrupted.")
    os.replace(path + ".part", path)
    info = {"path": "00-inbox/" + fn, "name": base[:120], "size": length, "kind": UPLOAD_KINDS[ext]}
    if ext == ".docx":  # agents can't read .docx, so keep a plain-text copy beside it
        txt = path[:-5] + ".txt"
        subprocess.run(["/usr/bin/textutil", "-convert", "txt", "-output", txt, path], capture_output=True)
        if os.path.exists(txt):
            info["text"] = "00-inbox/" + os.path.basename(txt)
    return info


def checked_files(slug, files):
    """Attachments named in a chat message must be uploads in this project's 00-inbox."""
    out = []
    for f in (files or [])[:12]:
        rp = str((f or {}).get("path", ""))
        full = safe_join(os.path.join(ROOT, slug), rp) if re.match(r"^00-inbox/[^/]+$", rp) else None
        if full and os.path.isfile(full):
            ext = os.path.splitext(rp)[1].lower()
            item = {"path": rp, "name": str(f.get("name") or os.path.basename(rp))[:120], "size": os.path.getsize(full),
                    "kind": UPLOAD_KINDS.get(ext, "file")}
            if f.get("text") and os.path.isfile(os.path.join(ROOT, slug, str(f["text"]))):
                item["text"] = str(f["text"])
            out.append(item)
    return out


def scaled(full, slug, width):
    """Cached JPEG copy of a project image, at most `width` px wide (keeps exported PDFs small)."""
    if not os.path.isfile(full):
        return full
    cache = os.path.join(ROOT, slug, ".cache", "w%d" % width)
    os.makedirs(cache, exist_ok=True)
    out = os.path.join(cache, re.sub(r"[^A-Za-z0-9._-]", "_", os.path.relpath(full, os.path.join(ROOT, slug))) + ".jpg")
    if not os.path.exists(out) or os.path.getmtime(out) < os.path.getmtime(full):
        subprocess.run(["/usr/bin/sips", "-s", "format", "jpeg", "-s", "formatOptions", "82", "-Z", str(width),
                        full, "--out", out], capture_output=True)
    return out if os.path.exists(out) else full


def export_pdf(slug):
    """Print the film bible to PDF with headless Chrome (the print layout is /print?p=<slug>)."""
    st = json.load(open(os.path.join(ROOT, slug, "state.json"), encoding="utf-8"))
    if not (st.get("bible") or {}).get("path"):
        raise ValueError("Lore hasn't written the film bible yet.")
    if not os.path.exists(CHROME):
        raise ValueError("PDF export uses Google Chrome, which isn't installed.")
    out = os.path.join(ROOT, slug, "05-lore", "film-bible.pdf")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    tmp, prof = out + ".tmp.pdf", tempfile.mkdtemp(prefix="sb-chrome-")
    try:
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
                        "--user-data-dir=" + prof, "--no-pdf-header-footer", "--run-all-compositor-stages-before-draw",
                        "--virtual-time-budget=20000", "--print-to-pdf=" + tmp,
                        "http://127.0.0.1:%d/print?p=%s" % (PORT, slug)], capture_output=True, timeout=150)
    finally:
        shutil.rmtree(prof, ignore_errors=True)
    if not os.path.exists(tmp) or os.path.getsize(tmp) < 2000:
        raise ValueError("Chrome didn't produce the PDF. Try again in a moment.")
    os.replace(tmp, out)
    sb("merge", slug, "bible", "--json", json.dumps({"pdf": "05-lore/film-bible.pdf", "pdf_updated": now()}))
    return "05-lore/film-bible.pdf"


def load_state(slug):
    return json.load(open(os.path.join(ROOT, slug, "state.json"), encoding="utf-8"))


def chosen(sh):
    """The shot's version in use: the one picked on the board, else the latest (same rule as sb.py)."""
    vs = sh.get("versions") or []
    return next((x for x in vs if x.get("v") == sh.get("selected")), vs[-1] if vs else None)


def project_image(slug, rp):
    """A project-relative image path that exists inside the project, else ''."""
    rp = str(rp or "")
    if not rp or rp.startswith("/") or os.path.splitext(rp)[1].lower() not in IMAGE_EXT:
        return ""
    full = safe_join(os.path.join(ROOT, slug), rp)
    return rp if full and os.path.isfile(full) else ""


def tracked_images(item):
    """Images a cast item records in state: its image, earlier ones (history) and named alternates."""
    out = [item.get("image")]
    for v in item.values():
        if isinstance(v, dict):
            out.append(v.get("image"))
        elif isinstance(v, list):
            out += [x.get("image") for x in v if isinstance(x, dict)]
    return [x for x in out if isinstance(x, str) and x]


def gallery(slug):
    """Every variation of every cast item, oldest first. The crew keeps earlier generations as files named after
    the item (`<id>-v2-rejected.png`, `<id>-style1.png`…), so files on disk count as well as what state records."""
    pdir = os.path.join(ROOT, slug)
    s = load_state(slug)
    cast = [c for c in s.get("cast") or [] if c.get("id")]
    ids = sorted((c["id"] for c in cast), key=len, reverse=True)
    rows, owner = {c["id"]: {} for c in cast}, {}
    for c in cast:
        for rp in tracked_images(c):
            if project_image(slug, rp):
                owner.setdefault(rp, c["id"])
    for root, dirs, files in os.walk(os.path.join(pdir, "02-hatch")):
        dirs[:] = [d for d in dirs if d not in ("refs", "brand-refs") and not d.startswith(".")]
        for f in files:
            stem, ext = os.path.splitext(f)
            rp = os.path.relpath(os.path.join(root, f), pdir)
            if ext.lower() in IMAGE_EXT and rp not in owner:
                cid = next((i for i in ids if stem == i or stem.startswith(i + "-") or stem.startswith(i + "_")), None)
                if cid:
                    owner[rp] = cid
    for rp, cid in owner.items():
        t = dt.datetime.fromtimestamp(os.path.getmtime(os.path.join(pdir, rp))).isoformat(timespec="seconds")
        stem = os.path.splitext(os.path.basename(rp))[0]
        label = stem[len(cid):].strip("-_").replace("-", " ").replace("_", " ") if stem.startswith(cid) else stem
        rows[cid][rp] = {"path": rp, "t": t, "label": label or "main"}
    out = {}
    for c in cast:
        reviews, status = c.get("reviews") or {}, c.get("status") or ""
        items = sorted(rows[c["id"]].values(), key=lambda r: r["t"])
        for r in items:
            r["current"] = r["path"] == c.get("image")
            rv = reviews.get(r["path"])
            if rv:
                r.update(verdict=rv.get("verdict"), by=rv.get("by", NAME.lower()), notes=rv.get("notes", ""))
            elif r["current"]:
                r["verdict"] = ("changes" if any(q.get("status") == "open" for q in c.get("change_requests") or [])
                                else "approved" if re.search(r"approved|locked", status)
                                else "rejected" if "reject" in status else "pending" if re.search(r"review|pending", status) else "")
            elif re.search(r"reject", r["label"]):
                r.update(verdict="rejected", by="crew")
        out[c["id"]] = items
    return out


def area_edit(slug, body, r, who=None, remote=False):
    """Save an area edit: the mask, a copy of the image with the area tinted red, and the request; then a blocking
    change request and a message to the crew. sbimg composite later keeps every pixel outside the mask."""
    pdir = os.path.join(ROOT, slug)
    kind, cid, prompt = body.get("kind"), str(body.get("id", ""))[:60], str(body.get("prompt", "")).strip()[:4000]
    image = project_image(slug, body.get("image"))
    if not prompt:
        raise ValueError("Say what should change in the marked area.")
    if not image:
        raise ValueError("That image isn't in this project.")
    s = load_state(slug)
    if kind == "shot":
        sh = next((x for x in s.get("shots") or [] if x.get("id") == cid), None)
        v = next((x for x in (sh or {}).get("versions") or [] if str(x.get("v")) == str(body.get("v"))), None)
        if not v or v.get("image") != image:
            raise ValueError("That frame version isn't on the board any more.")
        what, crew = "%s v%s" % (cid, v["v"]), "Slate"
    elif kind == "cast":
        item = next((x for x in s.get("cast") or [] if x.get("id") == cid), None)
        if not item:
            raise ValueError("That cast item isn't on the board any more.")
        what, crew = "%s (%s)" % (item.get("name") or cid, os.path.basename(image)), "Hatch"
    else:
        raise ValueError("Unknown edit target.")
    m = re.match(r"^data:image/png;base64,([A-Za-z0-9+/=]+)$", str(body.get("mask", "")))
    data = base64.b64decode(m.group(1)) if m else b""
    if not data.startswith(b"\x89PNG"):
        raise ValueError("The marked area didn't come through. Mark it again.")
    stem = os.path.splitext(os.path.basename(image))[0]
    n = 1
    while os.path.exists(os.path.join(pdir, "07-edits", "%s-e%d" % (stem, n))):
        n += 1
    edir = os.path.join(pdir, "07-edits", "%s-e%d" % (stem, n))
    os.makedirs(edir)
    rel = lambda p: os.path.relpath(p, pdir)
    mask, marked = os.path.join(edir, "mask.png"), os.path.join(edir, "marked.png")
    open(mask, "wb").write(data)
    info = subprocess.run([SBIMG, "maskinfo", mask], capture_output=True, text=True)
    if info.returncode != 0:
        shutil.rmtree(edir, ignore_errors=True)
        raise ValueError("Mark the area to change first." if "empty" in info.stderr else "Couldn't read the marked area.")
    mi = json.loads(info.stdout)
    subprocess.run([SBIMG, "mark", os.path.join(pdir, image), mask, marked], capture_output=True)
    req = {"kind": kind, "id": cid, "v": body.get("v") if kind == "shot" else None, "image": image, "prompt": prompt,
           "mask": rel(mask), "marked": rel(marked), "folder": rel(edir), "area": mi["area"], "bbox": mi["bbox"],
           "suggest": mi["suggest"], "crop": mi["crop"], "crop_aspect": mi["crop_aspect"], "crop_scale": mi["crop_scale"],
           "t": now()}
    json.dump(req, open(os.path.join(edir, "request.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    edit = {k: req[k] for k in ("mask", "marked", "folder", "suggest", "crop", "crop_aspect", "area")}
    edit["request"] = rel(os.path.join(edir, "request.json"))
    args = ([cid, str(req["v"])] if kind == "shot" else ["--cast", cid, "--image", image])
    res = sb("change", slug, *args, "--text", "AREA EDIT: " + prompt, "--edit", json.dumps(edit))
    if res.returncode != 0:
        raise ValueError(res.stderr.strip() or "Couldn't record the edit.")
    crop = (" Suggested: crop mode, rect %s at %s, upscale %s." % (",".join(str(x) for x in mi["crop"]), mi["crop_aspect"], mi["crop_scale"])
            if mi["suggest"] == "crop" else " Suggested: whole-frame edit.")
    r.send("AREA EDIT on %s (blocking): %s\nOnly the area %s marked may change. Original: %s · mask: %s · marked copy (area "
           "tinted red): %s · request: %s. The marked area is %.1f%% of the frame.%s\nFollow **Area edits** in the "
           "shotbird SKILL.md: %s edits with a reference-edit model, `sbimg composite` pastes only the marked area onto "
           "the original (check seam_risk), saves it as a NEW %s, then Hawk checks the change inside the mark and "
           "approves with --resolves. Nothing downstream until `sb gate %s` passes."
           % (what, prompt, who or NAME, image, rel(mask), rel(marked), edit["request"], 100 * float(mi["area"]), crop, crew,
              "version" if kind == "shot" else "file (keep the original)", slug), role="board", by=who, remote=remote)
    return req


def new_project(text, aspect="16:9", mode="ask"):
    words = re.findall(r"[a-z0-9]+", text.lower())[:5] or ["project"]
    base = "-".join(words)[:40].strip("-") + "-" + dt.date.today().strftime("%m%d")
    slug, i = base, 2
    while os.path.exists(os.path.join(ROOT, slug)):
        slug, i = "%s-%d" % (base, i), i + 1
    title = text.strip().split("\n")[0][:70] or "New project"
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(text)
        brief = f.name
    subprocess.run(["/usr/bin/python3", "-I", os.path.join(HERE, "sb.py"), "init", slug, "--title", title,
                    "--aspect", aspect, "--mode", mode, "--brief-file", brief], check=True, capture_output=True, text=True)
    os.unlink(brief)
    return slug


# ----------------------------------------------------------------------------------------------
# HTTP
# ----------------------------------------------------------------------------------------------

class H(BaseHTTPRequestHandler):
    server_version = "Shotbird/2.0"

    def log_message(self, fmt, *a):
        pass

    def send(self, code, body, ctype="application/json; charset=utf-8"):
        if isinstance(body, (dict, list)):
            body = json.dumps(body, ensure_ascii=False)
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def file(self, path):
        if not path or not os.path.isfile(path):
            return self.send(404, {"error": "not found"})
        ctype = mimetypes.guess_type(path)[0] or "application/octet-stream"
        if ctype.startswith("text/") or ctype in ("application/json", "application/javascript"):
            ctype += "; charset=utf-8"
        with open(path, "rb") as f:
            self.send(200, f.read(), ctype)

    def body(self, limit=50000):
        n = min(int(self.headers.get("Content-Length") or 0), limit)
        try:
            return json.loads(self.rfile.read(n) or b"{}")
        except ValueError:
            return None

    # who is asking -------------------------------------------------------------------------
    def local(self):
        """True for requests from this Mac (the Shotbird app, a browser here, headless Chrome printing a PDF)."""
        return self.client_address[0] in LOCAL

    def who(self):
        """This Mac's owner, a signed-in teammate's name, or None."""
        if self.local():
            return NAME
        cfg = share_cfg()
        if not cfg:
            return None
        c = SimpleCookie(self.headers.get("Cookie") or "")
        return token_name(cfg, c["sb_auth"].value) if "sb_auth" in c else None

    def gate(self, path, u):
        """Teammates on the network sign in first; this Mac never has to. False means the request was answered."""
        if self.local() or path in ("/login", "/api/login", "/logout", "/board/icon.svg") or self.who():
            return True
        if self.command == "GET" and not path.startswith(("/api/", "/p/")):
            nxt = path + ("?" + u.query if u.query else "")
            self.send_response(302)
            self.send_header("Location", "/login?next=" + quote(nxt, safe=""))
            self.send_header("Content-Length", "0")
            self.end_headers()
        else:
            self.send(401, {"error": "Sign in to Shotbird first."})
        return False

    def cookie(self, code, body, value, max_age):
        payload = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Set-Cookie", "sb_auth=%s; Path=/; HttpOnly; SameSite=Lax; Max-Age=%d" % (value, max_age))
        self.end_headers()
        self.wfile.write(payload)

    def login(self, body):
        cfg, ip = share_cfg(), self.client_address[0]
        if not cfg:
            return self.send(403, {"error": "Sharing is off on this Mac."})
        with FAILS_LOCK:
            fails, until = FAILS.get(ip, [0, 0])
            if until > time.time():
                return self.send(429, {"error": "Too many tries. Wait a minute and try again."})
        name = re.sub(r"\s+", " ", str(body.get("name", ""))).strip()[:40]
        if not name:
            return self.send(400, {"error": "Type your name, so the chat shows who's asking."})
        if not password_ok(cfg, str(body.get("password", ""))):
            with FAILS_LOCK:
                fails += 1
                FAILS[ip] = [0, time.time() + 60] if fails >= 5 else [fails, 0]
            time.sleep(0.6)
            return self.send(401, {"error": "That password isn't right."})
        with FAILS_LOCK:
            FAILS.pop(ip, None)
        return self.cookie(200, {"ok": True, "name": name}, make_token(cfg, name), 30 * 86400)

    def do_GET(self):
        u = urlparse(self.path)
        path = unquote(u.path)
        if not self.gate(path, u):
            return
        if path == "/login":
            return self.file(os.path.join(BOARD, "login.html"))
        if path == "/logout":
            self.send_response(302)
            self.send_header("Location", "/login")
            self.send_header("Set-Cookie", "sb_auth=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        if path == "/api/me":
            return self.send(200, {"name": self.who(), "local": self.local(), "sharing": bool(share_cfg())})
        if path in ("/", "/index.html"):
            return self.file(os.path.join(BOARD, "index.html"))
        if path == "/print":
            return self.file(os.path.join(BOARD, "print.html"))
        if path.startswith("/board/"):
            return self.file(safe_join(BOARD, path[len("/board/"):]))
        if path == "/api/projects":
            out = []
            if os.path.isdir(ROOT):
                for slug in sorted(os.listdir(ROOT)):
                    sp = os.path.join(ROOT, slug, "state.json")
                    if SLUG.match(slug) and os.path.isfile(sp):
                        try:
                            s = json.load(open(sp, encoding="utf-8"))
                        except ValueError:
                            continue
                        shots = s.get("shots", [])
                        thumb = None
                        for sh in shots:
                            vs = sh.get("versions") or []
                            if vs and vs[-1].get("image"):
                                thumb = "/p/%s/%s" % (slug, vs[-1]["image"])
                                break
                        out.append(dict(s.get("project", {}), shots=len(shots), qc=s.get("qc", {}), thumb=thumb))
            out.sort(key=lambda x: x.get("updated", ""), reverse=True)
            return self.send(200, out)
        if path == "/api/crew":
            return self.send(200, crew())
        if path == "/api/status":
            return self.send(200, auth_status())
        m = re.match(r"^/api/p/([^/]+)/chat$", path)
        if m and SLUG.match(m.group(1)) and os.path.isdir(os.path.join(ROOT, m.group(1))):
            since = int((parse_qs(u.query).get("since") or ["0"])[0] or 0)
            r = runner(m.group(1))
            rows, n = r.rows(since)
            return self.send(200, {"messages": rows, "n": n, "running": r.running, "queued": len(r.queue)})
        m = re.match(r"^/api/p/([^/]+)/gallery$", path)
        if m and SLUG.match(m.group(1)) and os.path.isfile(os.path.join(ROOT, m.group(1), "state.json")):
            try:
                return self.send(200, gallery(m.group(1)))
            except (OSError, ValueError) as e:
                return self.send(500, {"error": str(e)})
        m = re.match(r"^/p/([^/]+)/(.+)$", path)
        if m and SLUG.match(m.group(1)):
            full = safe_join(os.path.join(ROOT, m.group(1)), m.group(2))
            w = (parse_qs(u.query).get("w") or [""])[0]
            if w.isdigit() and full and os.path.splitext(full)[1].lower() in (".png", ".jpg", ".jpeg", ".webp"):
                full = scaled(full, m.group(1), min(int(w), 3000))  # print/PDF: a resized JPEG instead of the 2K/4K original
            return self.file(full)
        return self.send(404, {"error": "not found"})

    def do_POST(self):
        u = urlparse(self.path)
        path = u.path
        if not self.gate(path, u):
            return
        who, remote = self.who(), not self.local()
        tag = (lambda t: t) if not remote else (lambda t: "%s: %s" % (who, t))  # board notes say which teammate acted
        m = re.match(r"^/api/p/([^/]+)/upload$", path)
        if m:  # raw body, streamed to disk; handled before the JSON body is read
            slug = m.group(1)
            if not (SLUG.match(slug) and os.path.isdir(os.path.join(ROOT, slug))):
                return self.send(404, {"error": "no project"})
            try:
                info = save_upload(slug, (parse_qs(u.query).get("name") or ["file"])[0], self.rfile,
                                   int(self.headers.get("Content-Length") or 0))
            except ValueError as e:
                self.close_connection = True
                return self.send(400, {"error": str(e)})
            return self.send(200, info)
        is_edit = bool(re.match(r"^/api/p/[^/]+/edit$", path))
        if is_edit and int(self.headers.get("Content-Length") or 0) > MAX_EDIT:
            self.close_connection = True
            return self.send(413, {"error": "The marked area is too large to send."})
        body = self.body(MAX_EDIT if is_edit else 50000)
        if body is None:
            return self.send(400, {"error": "bad json"})
        if path == "/api/login":
            return self.login(body)
        if path == "/api/new":
            text = str(body.get("text", "")).strip()[:20000]
            start = body.get("start", True) is not False
            if not text and start:
                return self.send(400, {"error": "empty brief"})
            aspect = body.get("aspect") if body.get("aspect") in ASPECTS else "16:9"
            mode = "autopilot" if body.get("mode") == "autopilot" else "ask"
            slug = new_project(text, aspect, mode)
            if isinstance(body.get("models"), dict):
                set_models(slug, body["models"])
            if start:  # start=false: the board uploads attachments first, then sends the brief as a chat message
                runner(slug).send(text, by=who, remote=remote)
            return self.send(200, {"slug": slug})
        m = re.match(r"^/api/p/([^/]+)/(chat|stop|feedback|models|mode|export|open|edit)$", path)
        if not (m and SLUG.match(m.group(1))):
            return self.send(404, {"error": "not found"})
        slug, action = m.group(1), m.group(2)
        pdir = os.path.join(ROOT, slug)
        if not os.path.isdir(pdir):
            return self.send(404, {"error": "no project"})
        r = runner(slug)
        if action == "chat":
            text = str(body.get("text", "")).strip()[:20000]
            files = checked_files(slug, body.get("files"))
            if not text and not files:
                return self.send(400, {"error": "empty"})
            r.send(text or "Here are the files.", files=files, by=who, remote=remote)
            return self.send(200, {"ok": True})
        if action == "export":
            try:
                return self.send(200, {"ok": True, "pdf": export_pdf(slug)})
            except (ValueError, OSError, subprocess.TimeoutExpired) as e:
                return self.send(400, {"error": str(e)})
        if action == "open":
            if remote:  # it would open on this Mac's screen; the board downloads the file instead
                return self.send(403, {"error": "remote"})
            rp = str(body.get("path", ""))
            full = safe_join(pdir, rp) if rp and not rp.startswith("/") else None
            if not (full and os.path.exists(full)):
                return self.send(404, {"error": "no such file"})
            subprocess.run(["/usr/bin/open"] + (["-R"] if body.get("reveal") else []) + [full])
            return self.send(200, {"ok": True})
        if action == "stop":
            r.stop()
            return self.send(200, {"ok": True})
        if action == "edit":
            try:
                req = area_edit(slug, body, r, who=who, remote=remote)
            except (ValueError, OSError, KeyError) as e:
                return self.send(400, {"error": str(e)})
            return self.send(200, {"ok": True, "folder": req["folder"], "suggest": req["suggest"]})
        if action == "models":
            m = set_models(slug, body.get("models") or {})
            r.note(tag("Model choices updated: brain %s · crew %s · image %s · resolution %s · video %s"
                       % (m["brain"], m["crew"], m["image"], m["resolution"], m["video"])))
            return self.send(200, {"ok": True, "models": m})
        if action == "mode":
            mode = "autopilot" if body.get("mode") == "autopilot" else "ask"
            subprocess.run(["/usr/bin/python3", "-I", os.path.join(HERE, "sb.py"), "merge", slug, "project",
                            "--json", json.dumps({"mode": mode})], check=True, capture_output=True, text=True)
            r.note(tag("Mode set to %s" % ("Autopilot (proceed within the approved credit cap)" if mode == "autopilot"
                                           else "Always ask (ask before spending credits)")))
            return self.send(200, {"ok": True, "mode": mode})
        row = {"t": now(),
               "action": str(body.get("action", "note"))[:40],
               "shot": str(body.get("shot", ""))[:20],
               "target": str(body.get("target", ""))[:60],
               "image": project_image(slug, body.get("image")),  # one cast variation
               "v": body.get("v"),
               "text": str(body.get("text", ""))[:2000],
               "by": who}
        with open(os.path.join(pdir, "feedback.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
        vnum = str(int(row["v"])) if str(row["v"] or "").isdigit() else None
        img, text, act = row["image"], row["text"], row["action"]
        s = load_state(slug)
        item = next((c for c in s.get("cast") or [] if c.get("id") == row["target"]), None) if row["target"] else None
        sh = next((x for x in s.get("shots") or [] if x.get("id") == row["shot"]), None) if row["shot"] else None
        what = (row["shot"] + (" v%s" % vnum if vnum else "")) if row["shot"] else (
            "%s%s" % (row["target"], " (%s)" % os.path.basename(img) if img else ""))
        in_use = (sh and vnum and str((chosen(sh) or {}).get("v")) == vnum) or (item and img and item.get("image") == img)
        if act == "approve":
            # {{NAME}}'s click is a decision, recorded in state: it picks that gen and closes their open change requests
            if sh and vnum:
                sb("qc", slug, row["shot"], vnum, "approved", "--by", "abdullah",
                   "--notes", "Approved by %s on the board" % who, "--resolves", "%s approved this frame on the board" % who)
            elif item and img:
                sb("review", slug, "--cast", row["target"], "--image", img, "approved", "--notes", "Approved by %s on the board" % who)
            elif item:
                sb("cast", slug, "--json", json.dumps({"id": row["target"], "status": "approved",
                                                       "resolves": "%s approved on the board" % who}))
            r.note(tag("Approved %s%s" % (what, "" if in_use or not (vnum or img) else ": it is now the one in use")))
        elif act == "disapprove" and not in_use:
            # an alternate that isn't in use: recorded, nothing to redo
            if sh and vnum:
                sb("qc", slug, row["shot"], vnum, "rejected", "--by", "abdullah",
                   "--notes", "Disapproved by %s%s" % (who, (": " + text) if text else ""))
            elif item and img:
                sb("review", slug, "--cast", row["target"], "--image", img, "rejected", "--notes", text)
            r.note(tag("Disapproved %s%s (an alternate, not in use)" % (what, (": " + text) if text else "")))
        elif sh:
            # changes, or disapproving the frame in use: blocking until a new version fixes it
            ask = ("Disapproved: " + (text or "make a new version")) if act == "disapprove" else (text or "Re-do this frame")
            sb("change", slug, row["shot"], *([vnum] if vnum else []), "--text", ask)
            r.send("%s on %s (blocking): %s\nRe-shoot %s with exactly this change (Slate), then Hawk must "
                   "verify the change is visible and approve the NEW version with --resolves. Nothing downstream "
                   "(Lore, Cue) until `sb gate %s` passes; if Lore or Cue already ran, update them for %s afterwards."
                   % ("DISAPPROVED" if act == "disapprove" else "CHANGE REQUEST", what, ask, row["shot"], slug, row["shot"]),
                   role="board", by=who, remote=remote)
        elif item:
            ask = ("Disapproved: " + (text or "make a new one")) if act == "disapprove" else (text or "Re-do this cast item")
            if act == "disapprove" and img:
                sb("review", slug, "--cast", row["target"], "--image", img, "rejected", "--notes", text)
            sb("change", slug, "--cast", row["target"], *(["--image", img] if img else []), "--text", ask)
            r.send("%s on cast %s (blocking): %s\nHatch makes a NEW variation (a new file; every earlier one stays on the "
                   "board), registers it with `sb cast` and closes the request with \"resolves\"; then Slate re-shoots every "
                   "shot featuring it and Hawk re-checks. Lore and Cue wait for `sb gate %s`."
                   % ("DISAPPROVED" if act == "disapprove" else "CHANGE REQUEST", what, ask, slug), role="board", by=who, remote=remote)
        else:
            r.send("Note on %s%s" % (what, (": " + text) if text else ""), role="board", by=who, remote=remote)
        return self.send(200, {"ok": True})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8777)
    ap.add_argument("--host", help="default: every interface when sharing is on (launch.sh share), else this Mac only")
    a = ap.parse_args()
    global PORT
    PORT = a.port
    os.makedirs(ROOT, exist_ok=True)
    host = a.host or ("0.0.0.0" if share_cfg() else "127.0.0.1")
    try:
        srv = ThreadingHTTPServer((host, a.port), H)
    except OSError:
        # Already running (e.g. started by Shotbird.app): keep that one and idle, so a preview launcher still attaches.
        import time
        import urllib.request
        try:
            urllib.request.urlopen("http://127.0.0.1:%d/api/status" % a.port, timeout=2).read()
        except Exception:  # noqa: BLE001
            raise SystemExit("Port %d is taken by something that isn't Shotbird." % a.port)
        print("Shotbird board already running on http://localhost:%d" % a.port, flush=True)
        while True:
            time.sleep(3600)
    print("Shotbird board on http://localhost:%d" % a.port, flush=True)
    if host != "127.0.0.1":
        print("Shared on the office network: %s (teammates sign in with the shared password)"
              % " or ".join(lan_urls(a.port)), flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
