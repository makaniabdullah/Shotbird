#!/bin/sh
# Shotbird launcher. ~/Applications/Shotbird.app (native window) calls `serve`; the login agent opens the app.
#   sh ~/.claude/skills/shotbird/launch.sh             start the server (if needed) and open the Shotbird app
#   sh ~/.claude/skills/shotbird/launch.sh serve       start the server (if needed) and wait until it answers; no window
#   sh ~/.claude/skills/shotbird/launch.sh stop        stop the server
#   sh ~/.claude/skills/shotbird/launch.sh share       share it on the office network: set the team password, restart
#   sh ~/.claude/skills/shotbird/launch.sh share off   back to this Mac only
HERE="$HOME/.claude/skills/shotbird"
APP="$HOME/Applications/Shotbird.app"
BASE="http://localhost:8777"
LOG="$HOME/Shotbird/.server.log"
PIDF="$HOME/Shotbird/.server.pid"
SHARE="$HOME/Shotbird/.share.json"
up() { /usr/bin/curl -s -m 1 -o /dev/null "$BASE/api/status"; }
sharing() { /usr/bin/grep -q '"enabled": true' "$SHARE" 2>/dev/null; }
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

if [ "$1" = "share" ]; then
  mkdir -p "$HOME/Shotbird"
  if [ "$2" = "off" ]; then
    [ -f "$SHARE" ] && /usr/bin/sed -i '' 's/"enabled": true/"enabled": false/' "$SHARE"
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
  if sharing; then /usr/bin/caffeinate -i -w "$(cat "$PIDF")" >/dev/null 2>&1 & fi
  i=0
  while ! up && [ $i -lt 50 ]; do sleep 0.2; i=$((i + 1)); done
  up || { echo "The Shotbird server didn't start. Details: $LOG" >&2; exit 1; }
fi

[ "$1" = "serve" ] && exit 0

if [ -d "$APP" ]; then
  open -a "$APP"
elif [ -d "/Applications/Google Chrome.app" ]; then
  open -na "Google Chrome" --args --app="$BASE/"
else
  open "$BASE/"
fi
