#!/bin/bash
# Shotbird team installer: the crew, the board and the Shotbird app, for the current Mac user only.
#   bash install.sh                 interactive (what "Install Shotbird.command" runs)
#   bash install.sh --yes           accept the defaults (no login item, no Dock change)
#   --name=Sara --vault=/path       answer the questions up front (for scripted installs)
#   --no-login / --no-app           skip the Claude sign-in / skip building the app (used for testing)
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
SRC="$HERE/payload"
YES=0; NOLOGIN=0; NOAPP=0; ARG_NAME=""; ARG_VAULT="-"
for a in "$@"; do case "$a" in --yes) YES=1 ;; --no-login) NOLOGIN=1 ;; --no-app) NOAPP=1 ;;
  --name=*) ARG_NAME="${a#--name=}" ;; --vault=*) ARG_VAULT="${a#--vault=}" ;; esac; done
say() { printf "\n\033[1;38;5;209m▸ %s\033[0m\n" "$1"; }
ask() { if [ "$YES" = 1 ] || [ ! -t 0 ]; then echo "$2"; return; fi; read -r -p "$1 " r; echo "${r:-$2}"; }

printf "\n\033[1mShotbird\033[0m — an AI pre-production crew: brief → cast → storyboard → QC → film bible → video prompts.\n"
echo "Everything installs into your home folder. Your projects will live in ~/Shotbird."

# 1. Apple Command Line Tools: Python runs the board, swiftc builds the app
if ! xcode-select -p >/dev/null 2>&1 || ! /usr/bin/python3 -c 1 >/dev/null 2>&1 || ! command -v swiftc >/dev/null 2>&1; then
  say "Shotbird needs Apple's free Command Line Tools. A window will ask to install them."
  xcode-select --install >/dev/null 2>&1 || true
  echo "When that finishes, run the installer again."; exit 1
fi

# 2. The Claude desktop app: its built-in Claude Code runs the crew on your own Claude account
B=$(ls -d "$HOME/Library/Application Support/Claude/claude-code/"*/*/claude.app/Contents/MacOS/claude 2>/dev/null | sort -V | tail -1)
if [ -z "$B" ]; then
  say "Install the Claude desktop app first (https://claude.ai/download), sign in, and open its Code tab once. Then run this again."
  exit 1
fi

# 3. Who the crew works for
DEF_NAME=$(id -F 2>/dev/null | awk '{print $1}'); DEF_NAME=${DEF_NAME:-there}
if [ -n "$ARG_NAME" ]; then NAME="$ARG_NAME"; else NAME=$(ask "What should the crew call you? [$DEF_NAME]" "$DEF_NAME"); fi
if [ "$ARG_VAULT" != "-" ]; then VAULT="$ARG_VAULT"; else VAULT=$(ask "Path to your Obsidian vault, if Shotbird should file into it (press Enter to skip):" ""); fi
VAULT="${VAULT/#\~/$HOME}"
if [ -n "$VAULT" ] && [ ! -d "$VAULT" ]; then echo "No folder at $VAULT, so no vault for now."; VAULT=""; fi

# 4. Install, backing up anything this would overwrite
STAMP=$(date +%Y%m%d-%H%M%S); BK="$HOME/Shotbird/.backup-$STAMP"
backup() { if [ -e "$1" ]; then mkdir -p "$BK/$(dirname "${1#$HOME/}")"; mv "$1" "$BK/${1#$HOME/}"; fi; }
mkdir -p "$HOME/.claude/agents" "$HOME/.claude/skills" "$HOME/Shotbird/_crew" "$HOME/Applications"
say "Installing the crew and the board"
for f in "$SRC"/agents/*.md; do
  d="$HOME/.claude/agents/$(basename "$f")"
  [ -e "$d" ] && ! cmp -s "$f" "$d" && backup "$d"
  cp "$f" "$d"
done
for d in "$SRC"/skills/* "$SRC/shotbird"; do
  t="$HOME/.claude/skills/$(basename "$d")"; backup "$t"; cp -R "$d" "$t"
done
for f in "$SRC"/crew/*.md; do d="$HOME/Shotbird/_crew/$(basename "$f")"; backup "$d"; cp "$f" "$d"; done
xattr -dr com.apple.quarantine "$HOME/.claude/skills/shotbird" "$HOME/Shotbird/_crew" 2>/dev/null || true

# 5. Fill in the name and vault everywhere the crew reads them
/usr/bin/python3 -I - "$NAME" "$VAULT" "$HOME" <<'PY'
import glob, json, os, sys
name, vault, home = sys.argv[1:4]
files = glob.glob(home + "/.claude/agents/*.md") + glob.glob(home + "/Shotbird/_crew/*.md") + \
        glob.glob(home + "/.claude/skills/sb-*/**/*.md", recursive=True) + \
        glob.glob(home + "/.claude/skills/shotbird/**/*", recursive=True)
for p in files:
    if not os.path.isfile(p) or not p.endswith((".md", ".py", ".html", ".sh", ".js")):
        continue
    t = open(p, encoding="utf-8").read()
    if "{{" not in t:
        continue
    v = vault if p.endswith(".py") else (vault or "none configured")
    open(p, "w", encoding="utf-8").write(t.replace("{{NAME}}", name).replace("{{VAULT}}", v))
json.dump({"name": name, "vault": vault}, open(home + "/Shotbird/.config.json", "w"), indent=1)
PY

# 6. Build the frame tool and the app on this Mac
say "Building Shotbird (about a minute)"
LOGF=$(mktemp); sh "$HOME/.claude/skills/shotbird/tools/build.sh" >"$LOGF" 2>&1 || { cat "$LOGF"; echo "Building the frame tool failed."; exit 1; }
if [ "$NOAPP" = 0 ]; then sh "$HOME/.claude/skills/shotbird/app/build.sh" | tail -1; fi

# 7. Sign the crew in to Claude (one time; opens your browser)
READY=$(/usr/bin/python3 -I -c "import sys; sys.path.insert(0, '$HOME/.claude/skills/shotbird'); import serve; print(serve.auth_status().get('ready'))" 2>/dev/null || echo False)
if [ "$READY" != "True" ] && [ "$NOLOGIN" = 0 ]; then
  say "Signing the crew in to your Claude account (your browser will open)"
  sh "$HOME/.claude/skills/shotbird/login.sh" || echo "You can sign in later: sh ~/.claude/skills/shotbird/login.sh"
fi

# 8. Optional: open at login, and a Dock icon
if [ "$NOAPP" = 0 ]; then
  if [[ "$(ask "Open Shotbird when you log in? [y/N]" n)" =~ ^[Yy] ]]; then
    P="$HOME/Library/LaunchAgents/com.makani.shotbird.plist"; mkdir -p "$(dirname "$P")"
    cat >"$P" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
	<key>Label</key><string>com.makani.shotbird</string>
	<key>ProgramArguments</key><array><string>/usr/bin/open</string><string>-a</string><string>$HOME/Applications/Shotbird.app</string></array>
	<key>RunAtLoad</key><true/>
</dict></plist>
EOF
    launchctl bootout "gui/$(id -u)/com.makani.shotbird" 2>/dev/null || true
    launchctl bootstrap "gui/$(id -u)" "$P" 2>/dev/null || true
  fi
  if ! defaults read com.apple.dock persistent-apps 2>/dev/null | grep -q "Shotbird.app" \
     && [[ "$(ask "Add Shotbird to your Dock? [Y/n]" y)" =~ ^[Yy] ]]; then
    defaults write com.apple.dock persistent-apps -array-add "<dict><key>tile-data</key><dict><key>file-data</key><dict><key>_CFURLString</key><string>file://$HOME/Applications/Shotbird.app/</string><key>_CFURLStringType</key><integer>15</integer></dict><key>file-label</key><string>Shotbird</string></dict><key>tile-type</key><string>file-tile</string></dict>"
    killall Dock
  fi
fi

say "Shotbird is installed"
cat <<EOF
One more thing in Claude: Settings → Connectors → add Higgsfield and sign in.
The crew generates images through it, on your own Higgsfield credits (it always asks before spending, unless you switch on Autopilot).
PDF export of film bibles uses Google Chrome if it's installed.

Open Shotbird from ~/Applications, Spotlight or the Dock. Projects live in ~/Shotbird.
$( [ -d "$BK" ] && echo "Anything replaced was backed up to $BK" )
EOF
[ "$NOAPP" = 0 ] && [ "$YES" = 0 ] && open "$HOME/Applications/Shotbird.app" || true
