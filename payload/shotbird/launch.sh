#!/bin/sh
# Shotbird launcher. ~/Applications/Shotbird.app (native window) calls `serve`; the login agent opens the app.
#   sh ~/.claude/skills/shotbird/launch.sh             start the server (if needed) and open the Shotbird app
#   sh ~/.claude/skills/shotbird/launch.sh serve       start the server (if needed) and wait until it answers; no window
#   sh ~/.claude/skills/shotbird/launch.sh stop        stop the server
#   sh ~/.claude/skills/shotbird/launch.sh share       share it on the office network: set the team password, restart
#   sh ~/.claude/skills/shotbird/launch.sh share off   back to this Mac only (also closes the internet link)
#   sh ~/.claude/skills/shotbird/launch.sh tunnel      a public https link to this Mac (Cloudflare Quick Tunnel, free):
#                                                      teammates anywhere sign in with the team password. It starts with
#                                                      Shotbird from now on; the link changes when the tunnel restarts.
#   sh ~/.claude/skills/shotbird/launch.sh tunnel off  close the internet link
#   sh ~/.claude/skills/shotbird/launch.sh tunnel restart  a fresh internet link now (a watcher also does this by
#                                                      itself when Cloudflare drops the tunnel, after sleep for example)
#   sh ~/.claude/skills/shotbird/launch.sh pages      a fixed team link on GitHub Pages that always forwards to the
#                                                      current tunnel link (settings: ~/Shotbird/.pages.json; pages.sh)
#   sh ~/.claude/skills/shotbird/launch.sh pages off   stop updating it (the page then says Shotbird is offline)
HERE="$HOME/.claude/skills/shotbird"
APP="$HOME/Applications/Shotbird.app"
BASE="http://localhost:8777"
LOG="$HOME/Shotbird/.server.log"
PIDF="$HOME/Shotbird/.server.pid"
SHARE="$HOME/Shotbird/.share.json"
CFD="$HERE/bin/cloudflared"
[ -x "$CFD" ] || for c in /opt/homebrew/bin/cloudflared /usr/local/bin/cloudflared "$HOME/.local/bin/cloudflared" /usr/bin/cloudflared; do [ -x "$c" ] && CFD="$c" && break; done
TON="$HOME/Shotbird/.tunnel.on"
TPID="$HOME/Shotbird/.tunnel.pid"
TLOG="$HOME/Shotbird/.tunnel.log"
TURL="$HOME/Shotbird/.tunnel-url"
WPID="$HOME/Shotbird/.tunnel-watch.pid"
WLOG="$HOME/Shotbird/.tunnel-watch.log"
PON="$HOME/Shotbird/.pages.on"
PLOG="$HOME/Shotbird/.pages.log"
pages_push() { [ -f "$PON" ] && sh "$HERE/pages.sh" update "$1" >>"$PLOG" 2>&1; }  # the fixed GitHub link follows the tunnel
up() { /usr/bin/curl -s -m 1 -o /dev/null "$BASE/api/status"; }
sharing() { /usr/bin/grep -q '"enabled": true' "$SHARE" 2>/dev/null; }
tunnel_up() { [ -f "$TPID" ] && kill -0 "$(cat "$TPID")" 2>/dev/null; }
tunnel_start() {  # a Cloudflare Quick Tunnel to the board; it outlives server restarts, so the link stays the same
  tunnel_up && return 0
  [ -x "$CFD" ] || { echo "The tunnel program isn't installed: brew install cloudflared, or put it at $HERE/bin/cloudflared" >&2; return 1; }
  rm -f "$TURL" "$TLOG"  # a new log file, so nothing an old tunnel still writes lands in this one's
  nohup "$CFD" tunnel --no-autoupdate --url http://127.0.0.1:8777 >"$TLOG" 2>&1 </dev/null &
  echo $! >"$TPID"
  i=0
  while [ $i -lt 60 ]; do
    # api.trycloudflare.com is Cloudflare's own address, named in the error when the Mac has no internet yet
    U=$(/usr/bin/grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' "$TLOG" | /usr/bin/grep -v '^https://api\.' | /usr/bin/head -1)
    [ -n "$U" ] && { echo "$U" >"$TURL"; pages_push "$U" & return 0; }
    sleep 0.5; i=$((i + 1))
  done
  echo "The tunnel didn't come up. Details: $TLOG" >&2
  return 1
}
tunnel_kill() {  # a dropped tunnel can take a minute to shut down: wait 5s, then force it, so it can't linger
  P=$(cat "$TPID" 2>/dev/null)
  if [ -n "$P" ] && kill "$P" 2>/dev/null; then
    i=0
    while kill -0 "$P" 2>/dev/null && [ $i -lt 25 ]; do sleep 0.2; i=$((i + 1)); done
    kill -9 "$P" 2>/dev/null
  fi
  rm -f "$TPID" "$TURL"
}
tunnel_stop() { [ -f "$WPID" ] && kill "$(cat "$WPID")" 2>/dev/null; rm -f "$WPID"; tunnel_kill; }
# ok, gone (no tunnel, or Cloudflare deleted it: it does that to a quick tunnel it loses touch with, and cloudflared
# then retries the dead link forever), or down (no live connection to Cloudflare right now, per its /ready check)
tunnel_health() {
  tunnel_up || { echo gone; return; }
  ok=$(/usr/bin/grep -n "Registered tunnel connection" "$TLOG" | /usr/bin/tail -1 | /usr/bin/cut -d: -f1)
  lost=$(/usr/bin/grep -n "Tunnel not found" "$TLOG" | /usr/bin/tail -1 | /usr/bin/cut -d: -f1)
  [ -n "$lost" ] && [ "$lost" -gt "${ok:-0}" ] && { echo gone; return; }
  M=$(/usr/bin/grep -oE 'metrics server on [0-9.:]+' "$TLOG" | /usr/bin/head -1 | /usr/bin/awk '{print $4}')
  if [ -z "$M" ] || /usr/bin/curl -s -f -m 5 -o /dev/null "http://$M/ready"; then echo ok; else echo down; fi
}
tunnel_watch() {  # every minute: a fresh tunnel when it's gone, or down for 3 checks in a row (moves the team link too)
  bad=0
  while [ -f "$TON" ] && sharing; do
    sleep 60
    case "$(tunnel_health)" in ok) bad=0 ;; gone) bad=3 ;; *) bad=$((bad + 1)) ;; esac
    if [ $bad -ge 3 ]; then
      echo "$(date '+%F %T') the tunnel was lost; starting a fresh one"
      tunnel_kill
      tunnel_start && echo "$(date '+%F %T') new link: $(cat "$TURL")"
      bad=0
    fi
  done
  rm -f "$WPID"
}
watch_start() {
  [ -f "$WPID" ] && kill -0 "$(cat "$WPID")" 2>/dev/null && return 0
  nohup sh "$HERE/launch.sh" tunnel watch >>"$WLOG" 2>&1 </dev/null &
  echo $! >"$WPID"
}
stop() {
  if [ -f "$PIDF" ] && kill "$(cat "$PIDF")" 2>/dev/null; then echo "Shotbird stopped."
  elif /usr/bin/pkill -f "$HERE/serve.py"; then echo "Shotbird stopped."
  else echo "Shotbird isn't running."; fi
  rm -f "$PIDF"
  i=0
  while up && [ $i -lt 25 ]; do sleep 0.2; i=$((i + 1)); done
}

if [ "$1" = "stop" ]; then
  stop
  exit 0
fi

if [ "$1" = "tunnel" ]; then
  if [ "$2" = "off" ]; then
    rm -f "$TON"; tunnel_stop
    pages_push off
    echo "The internet link is closed. (Office-network sharing is unchanged.)"
    exit 0
  fi
  if [ "$2" = "watch" ]; then tunnel_watch; exit 0; fi
  sharing || { echo "Set a team password first: sh $HERE/launch.sh share" >&2; exit 1; }
  [ "$2" = "restart" ] && { rm -f "$TON"; tunnel_stop; }  # start clean: no old tunnel or watcher
  sh "$HERE/launch.sh" serve || exit 1
  touch "$TON"  # after serve, so serve's own auto-start doesn't race this one
  tunnel_start; ok=$?
  watch_start  # even if it failed (no network, say): the watcher keeps trying
  [ $ok -eq 0 ] || exit 1
  echo "Shotbird is on the internet at:"
  echo "  $(cat "$TURL")"
  echo "Teammates sign in with their name and the team password. The link changes if the tunnel restarts"
  echo "(after a reboot, for example); the board's Team link button always has the current one."
  echo "Close it: sh $HERE/launch.sh tunnel off"
  exit 0
fi

if [ "$1" = "pages" ]; then
  if [ "$2" = "off" ]; then
    pages_push off; rm -f "$PON"
    echo "The GitHub team link no longer follows the tunnel (it now says Shotbird is offline)."
    exit 0
  fi
  [ -f "$HOME/Shotbird/.pages.json" ] || { echo "Missing ~/Shotbird/.pages.json (repo and page address)." >&2; exit 1; }
  touch "$PON"
  if tunnel_up && [ -s "$TURL" ]; then sh "$HERE/pages.sh" update "$(cat "$TURL")" || exit 1
  else sh "$HERE/pages.sh" update off || exit 1; fi
  exit 0
fi

if [ "$1" = "share" ]; then
  mkdir -p "$HOME/Shotbird"
  if [ "$2" = "off" ]; then
    [ -f "$SHARE" ] && /usr/bin/sed -i.bak 's/"enabled": true/"enabled": false/' "$SHARE" && rm -f "$SHARE.bak"
    rm -f "$TON"; tunnel_stop; pages_push off  # no password, no internet link
    stop >/dev/null
    sh "$HERE/launch.sh" serve && echo "Sharing is off: only this Mac can open Shotbird."
    exit 0
  fi
  # The password goes straight into a salted PBKDF2 hash; it is never stored or shown.
  printf "Choose a password for your teammates (8+ characters): "; stty -echo; read -r PW; stty echo; echo
  printf "Type it again: "; stty -echo; read -r PW2; stty echo; echo
  [ "$PW" = "$PW2" ] || { echo "The passwords don't match. Nothing changed." >&2; exit 1; }
  [ "${#PW}" -ge 8 ] || { echo "Use at least 8 characters. Nothing changed." >&2; exit 1; }
  printf '%s' "$PW" | /usr/bin/python3 -I -c '
import hashlib, json, os, secrets, sys
pw, path = sys.stdin.read(), sys.argv[1]
salt, it = secrets.token_bytes(16), 200000
cfg = {"enabled": True, "secret": secrets.token_hex(32),  # a new secret also signs everyone out
       "password": "pbkdf2_sha256$%d$%s$%s" % (it, salt.hex(), hashlib.pbkdf2_hmac("sha256", pw.encode(), salt, it).hex())}
fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
with os.fdopen(fd, "w") as f:
    json.dump(cfg, f, indent=1)
' "$SHARE" || exit 1
  PW=""; PW2=""
  stop >/dev/null
  sh "$HERE/launch.sh" serve || exit 1
  echo "Shotbird is shared on the office network. Teammates open:"
  /usr/bin/grep "Shared on the office network" "$LOG" | /usr/bin/tail -1 \
    | /usr/bin/sed 's/^Shared on the office network: //; s/ (teammates.*//' | /usr/bin/awk -F' or ' '{for (i = 1; i <= NF; i++) print "  " $i}'
  echo "They sign in with their name and that password."
  echo "Change the password: run this again (it signs everyone out). Stop sharing: sh $HERE/launch.sh share off"
  exit 0
fi

mkdir -p "$HOME/Shotbird"
if ! up; then
  nohup /usr/bin/python3 -I "$HERE/serve.py" --port 8777 >>"$LOG" 2>&1 </dev/null &
  echo $! >"$PIDF"
  # While shared, keep the Mac from idle-sleeping (teammates can't reach a sleeping Mac); it ends with the server.
  if sharing && [ -x /usr/bin/caffeinate ]; then /usr/bin/caffeinate -i -w "$(cat "$PIDF")" >/dev/null 2>&1 & fi
  i=0
  while ! up && [ $i -lt 50 ]; do sleep 0.2; i=$((i + 1)); done
  up || { echo "The Shotbird server didn't start. Details: $LOG" >&2; exit 1; }
fi
# The internet link, if it's on, comes back with Shotbird (at login, for example).
if [ -f "$TON" ] && sharing; then { tunnel_up || tunnel_start; watch_start; } >/dev/null 2>&1 & fi

[ "$1" = "serve" ] && exit 0
[ "$(uname)" = "Darwin" ] || { echo "Shotbird is running at $BASE"; exit 0; }  # a Linux server has no window to open

if [ -d "$APP" ]; then
  open -a "$APP"
elif [ -d "/Applications/Google Chrome.app" ]; then
  open -na "Google Chrome" --args --app="$BASE/"
else
  open "$BASE/"
fi
