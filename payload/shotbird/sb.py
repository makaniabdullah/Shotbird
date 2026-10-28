#!/usr/bin/env python3
"""Shotbird state CLI: the only writer of a project's state.json (the board reads it).

Every Shotbird agent updates the board through this script so writes are locked and atomic.
Projects live in ~/Shotbird/<slug>/ (shortcut: ~/Shotbird).

  sb.py init <slug> --title T [--client C] [--aspect 16:9] [--mode ask|autopilot] [--brief-file F]
  sb.py agent <slug> <agent> <idle|working|waiting|done|error> [task text]
  sb.py log <slug> <agent> <text>
  sb.py merge <slug> <key> (--json J | --file F)       # shallow-merge an object into state[key]
  sb.py put <slug> <key> (--json J | --file F)         # replace state[key]
  sb.py cast <slug> (--json J | --file F)              # upsert cast item(s) by id; "resolves": "..." closes change requests
                                                        # (a new "image" keeps the old one in the item's history)
  sb.py shot <slug> (--json J | --file F)              # upsert shot(s) by id (versions kept)
  sb.py version <slug> <shot_id> (--json J | --file F) # append a frame version to a shot
  sb.py qc <slug> <shot_id> <v> <approved|rejected|pending> [--notes N] [--checks J] [--by hawk|abdullah] [--resolves HOW]
                                                        # {{NAME}}'s approval picks that version for the shot
  sb.py review <slug> --cast ID --image P <approved|rejected> [--notes N]   # {{NAME}}'s verdict on one cast variation;
                                                        # approving it makes it the item's image
  sb.py change <slug> (<shot_id> <v> | --cast ID [--image P]) --text T [--edit J]   # {{NAME}}'s change request:
                                                        # blocking until resolved; --edit carries an area edit (mask)
  sb.py gate <slug> [--shot S##]                        # what blocks Lore/Cue (exit 1 if blocked)
  sb.py prompt <slug> (--json J | --file F)            # upsert video prompt(s) by shot (gated; NO MUSIC, SFX only)
  sb.py credits <slug> [--estimated N] [--spent N] [--add N]
  sb.py fetch <url> <dest>                              # download a generated image/video
  sb.py feedback <slug> [--since N]                     # read board feedback (approve/reject clicks)
  sb.py show <slug> [key]                               # print state (or one key)
  sb.py path <slug>                                     # print the project folder
"""
import argparse
import datetime as dt
import fcntl
import json
import os
import re
import sys
import tempfile
import urllib.request

ROOT = os.environ.get("SHOTBIRD_ROOT", os.path.expanduser("~/Shotbird"))  # ~/Shotbird is a symlink to this (Desktop is privacy-protected)
AGENTS = ["scout", "hatch", "slate", "hawk", "lore", "cue"]
ROLES = {
    "scout": "Brief & brand",
    "hatch": "Characters & locations",
    "slate": "Storyboard frames",
    "hawk": "Quality control",
    "lore": "Film bible",
    "cue": "Video prompts",
}


def now():
    return dt.datetime.now().isoformat(timespec="seconds")


def pdir(slug):
    if not re.match(r"^[a-z0-9][a-z0-9-]{0,80}$", slug):
        sys.exit("bad slug %r (use lowercase letters, digits, hyphens)" % slug)
    return os.path.join(ROOT, slug)


def blank(slug, title):
    return {
        "project": {"slug": slug, "title": title, "client": "", "aspect": "16:9", "mode": "ask",
                    "status": "running", "created": now(), "updated": now()},
        "brief": {},
        "brand": {},
        "agents": {a: {"name": a.capitalize(), "role": ROLES[a], "status": "idle", "task": "", "updated": now()}
                   for a in AGENTS},
        "cast": [],
        "shots": [],
        "qc": {"rounds": 0, "approved": 0, "rejected": 0, "pending": 0},
        "bible": {},
        "prompts": [],
        "credits": {"estimated": 0, "spent": 0},
        "events": [],
    }


class State:
    """Context manager: lock, load, mutate, atomically save."""

    def __init__(self, slug, create=False):
        self.slug, self.dir = slug, pdir(slug)
        self.path = os.path.join(self.dir, "state.json")
        if not create and not os.path.exists(self.path):
            sys.exit("no Shotbird project %r at %s (run init first)" % (slug, self.dir))

    def __enter__(self):
        os.makedirs(self.dir, exist_ok=True)
        self.lockf = open(os.path.join(self.dir, ".state.lock"), "w")
        fcntl.flock(self.lockf, fcntl.LOCK_EX)
        self.s = json.load(open(self.path, encoding="utf-8")) if os.path.exists(self.path) else None
        return self

    def save(self):
        self.s["project"]["updated"] = now()
        self._recount()
        fd, tmp = tempfile.mkstemp(dir=self.dir, prefix=".state.", suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(self.s, f, ensure_ascii=False, indent=1)
        os.replace(tmp, self.path)

    def _recount(self):
        c = {"approved": 0, "rejected": 0, "pending": 0}
        for sh in self.s.get("shots", []):
            v = chosen(sh)
            if v:
                verdict = (v.get("qc") or {}).get("verdict", "pending")
                c[verdict if verdict in c else "pending"] += 1
        self.s.setdefault("qc", {}).update(c)

    def event(self, agent, text, kind="info"):
        ev = self.s.setdefault("events", [])
        ev.append({"t": now(), "agent": agent, "type": kind, "text": text[:600]})
        del ev[:-400]

    def __exit__(self, *a):
        fcntl.flock(self.lockf, fcntl.LOCK_UN)
        self.lockf.close()


def payload(args):
    if getattr(args, "file", None):
        return json.load(open(args.file, encoding="utf-8"))
    if getattr(args, "json", None):
        return json.loads(args.json)
    sys.exit("need --json or --file")


def upsert(lst, item, key):
    for i, x in enumerate(lst):
        if x.get(key) == item.get(key):
            merged = dict(x)
            merged.update(item)
            lst[i] = merged
            return merged
    lst.append(item)
    return item


def rel(st, p):
    """Store project-relative paths so the board can serve them."""
    if isinstance(p, str) and p.startswith(st.dir + "/"):
        return p[len(st.dir) + 1:]
    return p


def open_requests(item):
    return [r for r in item.get("change_requests") or [] if r.get("status") == "open"]


def chosen(sh):
    """The shot's version in use: the one {{NAME}} picked on the board, else the latest."""
    vs = sh.get("versions") or []
    return next((x for x in vs if x.get("v") == sh.get("selected")), vs[-1] if vs else None)


def keep_history(item, image):
    """Remember a cast item's earlier image, so the board still shows that variation."""
    if not image:
        return
    hist = item.setdefault("history", [])
    if not any(h.get("image") == image for h in hist):
        hist.append({"image": image, "t": now(), "model": item.get("model", ""), "job_id": item.get("job_id", "")})


def blockers(s, shot=None):
    """Everything that must be fixed before Lore writes the bible or Cue writes a shot's prompt."""
    out = []
    for c in s.get("cast", []):
        for r in open_requests(c):
            out.append("cast %s: open change request — %s" % (c.get("id"), r.get("text", "")))
    for sh in s.get("shots", []):
        if shot and sh.get("id") != shot:
            continue
        v = chosen(sh)
        if not v:
            out.append("%s: no frame yet" % sh.get("id"))
            continue
        verdict = (v.get("qc") or {}).get("verdict", "pending")
        if verdict != "approved":
            out.append("%s v%s: %s" % (sh.get("id"), v.get("v"), verdict))
        for r in open_requests(sh):
            out.append("%s: open change request — %s" % (sh.get("id"), r.get("text", "")))
    return out


# {{NAME}}'s rule for every video prompt: NO MUSIC, JUST SFX.
MUSIC = re.compile(r"\b(music|musical|soundtrack|score|bgm|song|songs|singing|melody|melodic|choir|beat drop)\b", re.I)
NEGATION = re.compile(r"\b(no|not|never|without|zero|none|nor|avoid|ban(?:ned)?|forbid(?:den)?)\b|\bNO\b", re.I)


def audio_rule_errors(text):
    t = text or ""
    errs = []
    if not re.search(r"\bno (background )?music\b|\bno bgm\b", t, re.I):
        errs.append("missing the line 'NO music' ({{NAME}}'s rule: NO MUSIC, JUST SFX)")
    if not re.search(r"\bsfx\b|sound effects?|diegetic", t, re.I):
        errs.append("missing an SFX-only audio block (name the diegetic sound effects)")
    for m in MUSIC.finditer(t):
        before = t[max(0, m.start() - 48):m.start()]
        clause = re.split(r"[.;\n]", before)[-1]
        if not NEGATION.search(clause):
            errs.append("music word %r is not negated near: ...%s%s..." % (m.group(0), clause[-30:], m.group(0)))
    return errs


def main():
    ap = argparse.ArgumentParser(description="Shotbird state CLI")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def jp(p):
        p.add_argument("--json")
        p.add_argument("--file")
        return p

    p = sub.add_parser("init"); p.add_argument("slug"); p.add_argument("--title", required=True)
    p.add_argument("--client", default=""); p.add_argument("--aspect", default="16:9")
    p.add_argument("--mode", default="ask", choices=["ask", "autopilot"]); p.add_argument("--brief-file")
    p = sub.add_parser("agent"); p.add_argument("slug"); p.add_argument("agent", choices=AGENTS)
    p.add_argument("status", choices=["idle", "working", "waiting", "done", "error"]); p.add_argument("task", nargs="*")
    p = sub.add_parser("log"); p.add_argument("slug"); p.add_argument("agent"); p.add_argument("text", nargs="+")
    jp(sub.add_parser("merge")).add_argument("slug"); sub.choices["merge"].add_argument("key")
    jp(sub.add_parser("put")).add_argument("slug"); sub.choices["put"].add_argument("key")
    jp(sub.add_parser("cast")).add_argument("slug")
    jp(sub.add_parser("shot")).add_argument("slug")
    p = jp(sub.add_parser("version")); p.add_argument("slug"); p.add_argument("shot_id")
    p = sub.add_parser("qc"); p.add_argument("slug"); p.add_argument("shot_id"); p.add_argument("v", type=int)
    p.add_argument("verdict", choices=["approved", "rejected", "pending"]); p.add_argument("--notes", default="")
    p.add_argument("--checks"); p.add_argument("--by", default="hawk"); p.add_argument("--resolves")
    p = sub.add_parser("review"); p.add_argument("slug"); p.add_argument("--cast", required=True); p.add_argument("--image", required=True)
    p.add_argument("verdict", choices=["approved", "rejected"]); p.add_argument("--notes", default="")
    p = sub.add_parser("change"); p.add_argument("slug"); p.add_argument("shot_id", nargs="?"); p.add_argument("v", nargs="?", type=int)
    p.add_argument("--cast"); p.add_argument("--image"); p.add_argument("--text", required=True); p.add_argument("--edit")
    p = sub.add_parser("gate"); p.add_argument("slug"); p.add_argument("--shot")
    jp(sub.add_parser("prompt")).add_argument("slug")
    p = sub.add_parser("credits"); p.add_argument("slug"); p.add_argument("--estimated", type=float)
    p.add_argument("--spent", type=float); p.add_argument("--add", type=float)
    p = sub.add_parser("fetch"); p.add_argument("url"); p.add_argument("dest")
    p = sub.add_parser("feedback"); p.add_argument("slug"); p.add_argument("--since", type=int, default=0)
    p = sub.add_parser("show"); p.add_argument("slug"); p.add_argument("key", nargs="?")
    p = sub.add_parser("path"); p.add_argument("slug")
    a = ap.parse_args()

    if a.cmd == "fetch":
        if not a.url.startswith("https://"):
            sys.exit("fetch only takes https:// URLs")
        os.makedirs(os.path.dirname(os.path.abspath(a.dest)), exist_ok=True)
        req = urllib.request.Request(a.url, headers={"User-Agent": "Shotbird/1.0"})
        with urllib.request.urlopen(req, timeout=120) as r, open(a.dest, "wb") as f:
            f.write(r.read())
        print(a.dest)
        return
    if a.cmd == "path":
        print(pdir(a.slug))
        return
    if a.cmd == "feedback":
        fp = os.path.join(pdir(a.slug), "feedback.jsonl")
        rows = [json.loads(l) for l in open(fp, encoding="utf-8")] if os.path.exists(fp) else []
        for i, r in enumerate(rows[a.since:], a.since):
            print(json.dumps(dict(r, n=i), ensure_ascii=False))
        return
    if a.cmd == "gate":
        s = json.load(open(os.path.join(pdir(a.slug), "state.json"), encoding="utf-8"))
        b = blockers(s, a.shot)
        print(json.dumps({"ok": not b, "blocking": b}, ensure_ascii=False, indent=1))
        sys.exit(1 if b else 0)
    if a.cmd == "show":
        s = json.load(open(os.path.join(pdir(a.slug), "state.json"), encoding="utf-8"))
        print(json.dumps(s.get(a.key) if a.key else s, ensure_ascii=False, indent=1))
        return

    with State(a.slug, create=(a.cmd == "init")) as st:
        if a.cmd == "init":
            if st.s:
                sys.exit("project %r already exists at %s" % (a.slug, st.dir))
            st.s = blank(a.slug, a.title)
            st.s["project"].update(client=a.client, aspect=a.aspect, mode=a.mode)
            for d in ["01-scout/brand-refs", "02-hatch/refs", "02-hatch/sheets", "03-slate/frames",
                      "04-hawk", "05-lore", "06-cue"]:
                os.makedirs(os.path.join(st.dir, d), exist_ok=True)
            if a.brief_file:
                txt = open(a.brief_file, encoding="utf-8").read()
                open(os.path.join(st.dir, "brief.md"), "w", encoding="utf-8").write(txt)
                st.s["brief"]["text"] = txt
            st.event("shotbird", "Project created: %s" % a.title, "start")
        elif a.cmd == "agent":
            task = " ".join(a.task)
            ag = st.s["agents"][a.agent]
            ag.update(status=a.status, task=task or ag.get("task", ""), updated=now())
            st.event(a.agent, ("%s — %s" % (a.status, task)) if task else a.status, "status")
        elif a.cmd == "log":
            st.event(a.agent, " ".join(a.text))
        elif a.cmd in ("merge", "put"):
            data = payload(a)
            if a.key == "bible" and isinstance(data, dict) and data.get("path"):
                b = blockers(st.s)
                if b:
                    sys.exit("The board isn't ready for the film bible: %s" % "; ".join(b))
            if a.cmd == "merge" and isinstance(st.s.get(a.key), dict) and isinstance(data, dict):
                st.s[a.key].update(data)
            else:
                st.s[a.key] = data
        elif a.cmd == "cast":
            for it in (lambda d: d if isinstance(d, list) else [d])(payload(a)):
                if "image" in it:
                    it["image"] = rel(st, it.get("image"))
                how = it.pop("resolves", None)  # Hatch (or {{NAME}}'s approval) closes open change requests
                old = next((x for x in st.s["cast"] if x.get("id") == it.get("id")), None)
                if old and it.get("image") and old.get("image") and old["image"] != it["image"]:
                    keep_history(old, old["image"])
                merged = upsert(st.s["cast"], it, "id")
                if how:
                    for r in open_requests(merged):
                        r.update(status="resolved", how=how, resolved_t=now())
                    if merged.get("status") == "changes_requested":
                        merged["status"] = "pending_review"
        elif a.cmd == "shot":
            for it in (lambda d: d if isinstance(d, list) else [d])(payload(a)):
                it.pop("versions", None)
                upsert(st.s["shots"], it, "id")
            st.s["shots"].sort(key=lambda x: x.get("n", 0))
        elif a.cmd == "version":
            v = payload(a)
            v["image"] = rel(st, v.get("image"))
            sh = next((x for x in st.s["shots"] if x["id"] == a.shot_id), None)
            if sh is None:
                sys.exit("no shot %s" % a.shot_id)
            vs = sh.setdefault("versions", [])
            v.setdefault("v", len(vs) + 1)
            v.setdefault("t", now())
            v.setdefault("qc", {"verdict": "pending"})
            vs.append(v)
            sh.pop("selected", None)  # a new version is the one in use until {{NAME}} picks another
            sh["status"] = "generated"
        elif a.cmd == "qc":
            sh = next((x for x in st.s["shots"] if x["id"] == a.shot_id), None)
            if sh is None:
                sys.exit("no shot %s" % a.shot_id)
            v = next((x for x in sh.get("versions", []) if x.get("v") == a.v), None)
            if v is None:
                sys.exit("no version %d of %s" % (a.v, a.shot_id))
            opened = open_requests(sh)
            if a.verdict == "approved" and opened:
                if not a.resolves:
                    sys.exit("%s has open change requests from {{NAME}}: %s\nVerify each change is visible in v%d, "
                             "then approve with --resolves \"<what you checked>\"; otherwise reject."
                             % (a.shot_id, " | ".join(r.get("text", "") for r in opened), a.v))
                if a.by != "abdullah" and not any(r.get("v") is None or a.v > r.get("v", 0) for r in opened):
                    sys.exit("v%d is the frame {{NAME}} asked to change; approve a NEW version that applies the change." % a.v)
                for r in opened:
                    r.update(status="resolved", resolved_in=a.v, resolved_by=a.by, how=a.resolves, resolved_t=now())
            v["qc"] = {"verdict": a.verdict, "notes": a.notes, "t": now(), "by": a.by,
                       "checks": json.loads(a.checks) if a.checks else {}}
            if a.by == "abdullah" and a.verdict == "approved":
                sh["selected"] = a.v  # their pick: this version is the shot from now on
            sh["status"] = "changes_requested" if open_requests(sh) else (chosen(sh).get("qc") or {}).get("verdict", "pending")
            st.event("hawk" if a.by != "abdullah" else "shotbird",
                     "%s v%d %s%s%s" % (a.shot_id, a.v, a.verdict.upper(), " by {{NAME}}" if a.by == "abdullah" else "",
                                        (" — " + a.notes) if a.notes else ""), "qc")
        elif a.cmd == "review":
            item = next((x for x in st.s["cast"] if x.get("id") == a.cast), None)
            if item is None:
                sys.exit("no cast item %s" % a.cast)
            img = rel(st, a.image)
            if not os.path.isfile(os.path.join(st.dir, img)):
                sys.exit("no image %s in the project" % img)
            item.setdefault("reviews", {})[img] = {"verdict": a.verdict, "by": "abdullah", "t": now(), "notes": a.notes}
            if a.verdict == "approved":
                if item.get("image") and item["image"] != img:
                    keep_history(item, item["image"])
                item.update(image=img, status="approved")
                for r in open_requests(item):
                    r.update(status="resolved", how="{{NAME}} approved %s on the board" % os.path.basename(img), resolved_t=now())
                st.event("shotbird", "%s: {{NAME}} approved %s (now the image in use)" % (a.cast, os.path.basename(img)), "qc")
            else:
                if item.get("image") == img:
                    item["status"] = "rejected"
                st.event("shotbird", "%s: {{NAME}} disapproved %s%s" % (a.cast, os.path.basename(img),
                                                                       (" — " + a.notes) if a.notes else ""), "qc")
        elif a.cmd == "change":
            req = {"id": "cr-%s" % dt.datetime.now().strftime("%m%d%H%M%S"), "t": now(), "text": a.text.strip(),
                   "status": "open", "by": "abdullah"}
            if a.edit:
                req["edit"] = json.loads(a.edit)  # area edit: mask, marked copy, crop suggestion (see SKILL.md)
            if a.cast:
                item = next((x for x in st.s["cast"] if x.get("id") == a.cast), None)
                if item is None:
                    sys.exit("no cast item %s" % a.cast)
                if a.image:
                    req["image"] = rel(st, a.image)  # the variation {{NAME}} wants changed
                    item.setdefault("reviews", {})[req["image"]] = {
                        "verdict": "rejected" if req["text"].startswith("Disapproved") else "changes",
                        "by": "abdullah", "t": now(), "notes": req["text"]}
                item.setdefault("change_requests", []).append(req)
                item["status"] = "changes_requested"
                st.event("shotbird", "Change request on %s%s: %s" % (
                    a.cast, " (%s)" % os.path.basename(req["image"]) if req.get("image") else "", req["text"]), "change")
            else:
                sh = next((x for x in st.s["shots"] if x["id"] == a.shot_id), None)
                if sh is None:
                    sys.exit("no shot %s" % a.shot_id)
                vs = sh.get("versions") or []
                v = next((x for x in vs if x.get("v") == a.v), vs[-1] if vs else None)
                req["v"] = v.get("v") if v else None
                sh.setdefault("change_requests", []).append(req)
                if v:  # the frame {{NAME}} asked to change can never stand as approved
                    v["qc"] = {"verdict": "rejected", "by": "abdullah", "t": now(), "checks": (v.get("qc") or {}).get("checks", {}),
                               "notes": "CHANGE REQUEST ({{NAME}}): %s" % req["text"]}
                sh["status"] = "changes_requested"
                st.event("shotbird", "Change request on %s v%s: %s" % (a.shot_id, req["v"], req["text"]), "change")
        elif a.cmd == "prompt":
            problems = []
            for it in (lambda d: d if isinstance(d, list) else [d])(payload(a)):
                b = blockers(st.s, it.get("shot"))
                if b:
                    problems.append("%s is not ready for a video prompt: %s" % (it.get("shot"), "; ".join(b)))
                errs = audio_rule_errors((it.get("prompt") or "") + "\n" + (it.get("audio") or ""))
                if errs:
                    problems.append("%s breaks the audio rule (NO MUSIC, JUST SFX): %s" % (it.get("shot"), "; ".join(errs)))
                if not problems:
                    upsert(st.s["prompts"], it, "shot")
            if problems:
                sys.exit("\n".join(problems))
            st.s["prompts"].sort(key=lambda x: x.get("shot", ""))
        elif a.cmd == "credits":
            c = st.s.setdefault("credits", {"estimated": 0, "spent": 0})
            if a.estimated is not None:
                c["estimated"] = a.estimated
            if a.spent is not None:
                c["spent"] = a.spent
            if a.add is not None:
                c["spent"] = round(c.get("spent", 0) + a.add, 2)
        st.save()
    print("ok")


if __name__ == "__main__":
    main()
