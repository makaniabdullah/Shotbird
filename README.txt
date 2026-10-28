SHOTBIRD — an AI pre-production crew
====================================

Brief it in a chat and six agents do the pre-production:
  Scout   reads the brief (or attached PDFs, docs, reference videos) and the brand
  Hatch   builds identity-locked characters and locations
  Slate   boards every shot
  Hawk    QCs each frame (identity, proportions, brand) and has bad frames redone
  Lore    writes the film bible (Markdown and PDF)
  Cue     writes the image-to-video prompts (Seedance 2.5 by default, SFX only, no music)

It runs on your own Mac, with your own Claude account and your own Higgsfield credits.
Nothing is shared with anyone else.


WHAT YOU NEED
  - A Mac on macOS 13 or later
  - The Claude desktop app (claude.ai/download), signed in, with Claude Code available on your plan.
    Open its Code tab once before installing.
  - A Higgsfield account, connected in Claude: Settings → Connectors → Higgsfield
  - Apple's Command Line Tools (the installer offers to install them)
  - Google Chrome, optional: used for the film bible PDF export


INSTALL
  1. Unzip Shotbird-Installer.zip.
  2. Right-click "Install Shotbird.command" and choose Open. You only need to right-click the first time:
     macOS asks because the file came from a teammate, not the App Store.
     (Or in Terminal: bash ~/Downloads/Shotbird-Installer/install.sh)
  3. Answer the questions:
     - your name;
     - an optional Obsidian vault;
     - whether to open Shotbird at login;
     - whether to add it to the Dock.
  4. Sign in to Claude in the browser window that opens. This happens once, so the crew can work for you.
  5. In Claude: Settings → Connectors → add Higgsfield.

Shotbird opens in its own window. Type a brief, or drop in a brief PDF or a reference video.


WHERE THINGS GO
  ~/Applications/Shotbird.app                              the app
  ~/.claude/skills/shotbird                                board, server and tools
  ~/.claude/agents/{scout,hatch,slate,hawk,lore,cue,shotbird-producer}.md   the crew
  ~/.claude/skills/sb-*, ~/.claude/skills/cinema-director-v3              the crew's skill packs
  ~/Shotbird                                               your projects, and the crew's skill cards (_crew)
  The installer backs up anything it replaces to ~/Shotbird/.backup-<date>.


GOOD TO KNOW
  - Credits: the crew asks before spending Higgsfield credits ("Always ask"). Autopilot lets it go ahead
    within the budget you approve.
  - Change requests: "Request changes" on a frame blocks the run until that frame is redone and approved.
  - Update: run a newer installer. Your projects are untouched.
  - Remove: bash ~/.claude/skills/shotbird/uninstall.sh (your projects stay in ~/Shotbird).
  - Credits for the open-source skill packs are in CREDITS.txt.
