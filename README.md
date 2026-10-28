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

## Open it to teammates anywhere

Teammates outside the office can reach the same Mac over the internet through a free Cloudflare Quick Tunnel. It needs no account and no domain.

1. Install Cloudflare's tunnel program once: `brew install cloudflared`. Or put the `cloudflared` binary at `~/.claude/skills/shotbird/bin/cloudflared`.
2. Turn on sharing first (above), then run:

   ```bash
   sh ~/.claude/skills/shotbird/launch.sh tunnel
   ```

- **The link:** it prints a public `https://….trycloudflare.com` link. Teammates sign in there with their name and the team password, as on the office network.
- **Lockout:** five wrong passwords lock that visitor out for a minute.
- **Restarts:** the tunnel comes back with Shotbird, at login for example. Its link changes whenever it restarts.
- **Team link button:** the button in the board's top bar always copies the current link.
- **Turning it off:**

  ```bash
  sh ~/.claude/skills/shotbird/launch.sh tunnel off
  ```

### A team link that never changes

To avoid resending the link after every restart, publish a small GitHub Pages page that always forwards to the current tunnel:

1. Have a GitHub repository you can push to from this Mac, with your GitHub sign-in saved in the keychain (a normal `git push` works without asking).
2. Create `~/Shotbird/.pages.json`:

   ```json
   {"repo": "https://github.com/<you>/<repo>.git", "url": "https://<you>.github.io/<repo>/"}
   ```

3. Run:

   ```bash
   sh ~/.claude/skills/shotbird/launch.sh pages
   ```

- **How it updates:** Shotbird force-pushes a one-page `gh-pages` branch whenever the tunnel's link changes. GitHub Pages serves it at the `url` above, and the Team link button copies that address instead.
- **When it's off:** with the tunnel or sharing off, the page says Shotbird is offline.
- **Stopping it:** `launch.sh pages off`.

Anyone who can read the repository can see the current tunnel link on the `gh-pages` branch. The team password still protects it.

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
