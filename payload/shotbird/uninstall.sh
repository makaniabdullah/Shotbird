#!/bin/bash
# Removes the Shotbird app, crew and board. Your projects in ~/Shotbird stay.
#   bash ~/.claude/skills/shotbird/uninstall.sh
sh "$HOME/.claude/skills/shotbird/launch.sh" stop >/dev/null 2>&1
pkill -x Shotbird 2>/dev/null
launchctl bootout "gui/$(id -u)/com.makani.shotbird" 2>/dev/null; rm -f "$HOME/Library/LaunchAgents/com.makani.shotbird.plist"
rm -rf "$HOME/Applications/Shotbird.app"
for a in scout hatch slate hawk lore cue shotbird-producer; do rm -f "$HOME/.claude/agents/$a.md"; done
rm -rf "$HOME"/.claude/skills/sb-* "$HOME/.claude/skills/cinema-director-v3"
rm -rf "$HOME/.claude/skills/shotbird"
echo "Shotbird removed. Your projects are still in ~/Shotbird. If it's pinned, drag its Dock icon off."
