#!/bin/sh
# One-time login for Shotbird's in-board orchestrator. It signs the desktop app's bundled Claude Code
# into your Claude account (opens your browser). Run in Terminal:  sh ~/.claude/skills/shotbird/login.sh
B=$(ls -d "$HOME/Library/Application Support/Claude/claude-code/"*/*/claude.app/Contents/MacOS/claude 2>/dev/null | sort -V | tail -1)
if [ -z "$B" ]; then echo "Claude Code was not found inside the Claude desktop app."; exit 1; fi
echo "Using: $B"
"$B" auth login && "$B" auth status
