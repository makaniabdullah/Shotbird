#!/bin/sh
# Shotbird's fixed team link: a GitHub Pages page that forwards to the current Cloudflare tunnel link.
#   sh ~/.claude/skills/shotbird/pages.sh update <https://….trycloudflare.com | off>
# launch.sh calls this whenever the tunnel's link changes (and with "off" when the tunnel closes).
# Settings: ~/Shotbird/.pages.json {"repo": "https://github.com/<you>/<repo>.git", "url": "https://<you>.github.io/<repo>/"}
# The page lives alone on the repo's gh-pages branch, force-pushed as one commit, so old links never pile up in history.
# The push uses the GitHub sign-in already saved in the macOS keychain; it never prompts.
set -e
CFG="$HOME/Shotbird/.pages.json"
LAST="$HOME/Shotbird/.pages-url"
REPO=$(/usr/bin/python3 -I -c 'import json,sys; print(json.load(open(sys.argv[1]))["repo"])' "$CFG")
TARGET="$2"
[ "$1" = "update" ] && [ -n "$TARGET" ] || { echo "usage: pages.sh update <url|off>" >&2; exit 2; }
case "$TARGET" in
  off) ;;
  https://*.trycloudflare.com) ;;
  *) echo "pages.sh: refusing to publish $TARGET" >&2; exit 2 ;;
esac
[ -f "$LAST" ] && [ "$(cat "$LAST")" = "$TARGET" ] && { echo "The team link already points at $TARGET"; exit 0; }

W=$(/usr/bin/mktemp -d "${TMPDIR:-/tmp}/shotbird-pages.XXXXXX")
trap '/bin/rm -rf "$W"' EXIT
cd "$W"
/usr/bin/git init -q -b gh-pages
/usr/bin/git config user.name "Shotbird"
/usr/bin/git config user.email "shotbird@users.noreply.github.com"
: >.nojekyll
if [ "$TARGET" = "off" ]; then
  BODY='<p>Shotbird is offline right now.</p><p class="s">Ask the person who runs it to switch it back on.</p>'
  SCRIPT=''
else
  BODY="<p>Opening Shotbird…</p><p class=\"s\"><a href=\"$TARGET/\">Tap here if nothing happens</a></p>"
  # keep ?p=<project>#tab, so a bookmarked project still opens on the right page
  SCRIPT="<script>location.replace('$TARGET/'+location.search+location.hash)</script>"
fi
/bin/cat >index.html <<EOF
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Shotbird</title>
<style>
:root{color-scheme:light dark}
body{margin:0;min-height:100vh;display:grid;place-items:center;font:15px/1.5 system-ui,-apple-system,sans-serif;background:#000;color:#f4f4f5;text-align:center;padding:24px}
.m{width:52px;height:52px;border-radius:16px;margin:0 auto 16px;background:linear-gradient(180deg,#ff8657,#ff4f1a);box-shadow:0 14px 40px -12px rgba(255,91,34,.6)}
p{margin:0 0 6px}.s{color:#a1a1aa;font-size:13px}a{color:#ff6b3d}
</style>
</head>
<body><div><div class="m"></div>$BODY</div>$SCRIPT</body>
</html>
EOF
/usr/bin/git add -A
/usr/bin/git commit -q -m "Team link: $([ "$TARGET" = off ] && echo offline || echo updated)"
GIT_TERMINAL_PROMPT=0 /usr/bin/git push -q -f "$REPO" gh-pages:gh-pages
echo "$TARGET" >"$LAST"
echo "Team link updated: $(/usr/bin/python3 -I -c 'import json,sys; print(json.load(open(sys.argv[1]))["url"])' "$CFG") -> $TARGET"
