# Shotbird

**An AI pre-production crew for your Mac.** You brief it in a chat, and six agents do the pre-production while a live board beside the chat fills up:

| Agent | Job |
|---|---|
| **Scout** | Reads the brief, attached PDFs and docs, and reference videos; extracts the brand look; writes the script or beat sheet |
| **Hatch** | Builds identity-locked characters and locations |
| **Slate** | Boards every shot |
| **Hawk** | Checks each frame for identity, proportions and brand, and has bad frames redone |
| **Lore** | Writes the film bible, as Markdown and PDF |
| **Cue** | Writes the image-to-video prompts. Seedance 2.5 by default; audio is SFX only, never music |

On the board you can:
- see every variation of every generation;
- Approve, Disapprove or Request changes on each one;
- mark an area of an image and say what should change there. Only that area is regenerated.

Shotbird runs on your own Claude account (Claude Code) and Higgsfield credits.

## What you need

- A Mac on macOS 13 or later.
- **The Claude desktop app**, signed in, on a plan that includes Claude Code. Open its Code tab once before installing.
- **A Higgsfield account**, connected in Claude (*Settings → Connectors → Higgsfield*).
- **Apple's Command Line Tools.** The installer offers to install them.
- Google Chrome, optional. It's used for the film bible's PDF export.

## Install

1. Download this repository: use *Code → Download ZIP* and unzip it, or `git clone` it.
2. Right-click **Install Shotbird.command** and choose *Open*. Or, in Terminal:

   ```bash
   bash install.sh
   ```

3. Answer the installer's questions (your name, an optional Obsidian vault, open at login, add to the Dock), then sign in to Claude in the browser window that opens.

Shotbird opens in its own window. Type a brief, or drop in a brief PDF or a reference video.

## Share it on your office network

One Mac can run Shotbird for a team on the same network:

```bash
sh ~/.claude/skills/shotbird/launch.sh share
```

- **Turning it on:** the command asks you to choose a team password. Shotbird stores only a salted hash of it.
- **Where teammates go:** it prints the address teammates open, `http://<your-mac>.local:8777`. They sign in with their name and the password. The chat shows who sent each message.
- **What's shared:** everyone uses that Mac's Claude account, its plan limits and its Higgsfield credits.
- **What's kept private:** teammates' turns never get the owner's Obsidian vault, and files they open download to their own browser.
- **The Mac must stay on:** it has to be on, awake and on the same network. Shotbird keeps it from idle-sleeping while sharing.
- **Turning it off:**

  ```bash
  sh ~/.claude/skills/shotbird/launch.sh share off
  ```

The crew runs on the host Mac and can run commands there, so only give the password to people you trust.

## Where things go

| Path | What |
|---|---|
| `~/Applications/Shotbird.app` | The app |
| `~/.claude/skills/shotbird` | Board, server (`serve.py`), state CLI (`sb.py`), tools |
| `~/.claude/agents/*.md` | The crew: Scout, Hatch, Slate, Hawk, Lore, Cue and the producer |
| `~/.claude/skills/sb-*`, `~/.claude/skills/cinema-director-v3` | The crew's skill packs |
| `~/Shotbird` | Your projects, and the crew's skill cards (`_crew`) |

**Never included:** projects, brand caches, Obsidian vaults, memory or credentials.

## Update and remove

- **Update:** pull or download a newer copy and run the installer again. It backs up anything it replaces to `~/Shotbird/.backup-<date>`, and leaves your projects untouched.
- **Remove:**

  ```bash
  bash ~/.claude/skills/shotbird/uninstall.sh
  ```

  Your projects stay in `~/Shotbird`.

## Layout of this repository

```
install.sh, Install Shotbird.command   the installer
payload/shotbird/                      board (board/), server (serve.py), state CLI (sb.py), launcher, app and sbimg sources
payload/agents/                        the seven crew agents
payload/skills/                        skill packs (open-source, with their licences) and cinema-director-v3
payload/crew/                          the crew's skill cards
CREDITS.txt                            credits for the skill packs
```

The files are generated from the working copy by `share/package.py --repo <this folder>`, so edit there, not here.

## Licence

© 2026 Abdullah Makani. All rights reserved, except the open-source skill packs, which keep their own licences (see [CREDITS.txt](CREDITS.txt) and [LICENSE](LICENSE)).
