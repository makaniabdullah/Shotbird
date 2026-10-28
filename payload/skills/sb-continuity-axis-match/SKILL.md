---
name: sb-continuity-axis-match
description: "Shotbird crew skill (Slate): continuity editing, the 180° axis, eyeline and match-cut checklist. Use inside Shotbird runs."
tags:
  - continuity-editing
  - 180-degree-rule
  - axis-of-action
  - match-on-action
  - screen-direction
agents:
  allow:
    - planner
    - script_writer
    - video_designer
    - flf_video_designer
---

> **Shotbird install note.** Installed for Abdullah's Shotbird crew from a pinned GitHub commit (see ATTRIBUTION.md). Scripts, databases, CI and settings files were not installed: skip any step that runs a script, installs software, uploads media to third-party sites or writes to a local database. Shotbird logs work through `sb.py` and each agent's memory. Abdullah's house rules (Obsidian vault playbooks and the agent's own instructions) take precedence over this skill.

# Continuity Editing Axis Match

Use this skill when building sequences that must cut cleanly and preserve orientation.

## Source Basis
- No Film School / Filmmakers Academy 180-degree rule guidance.
- StudioBinder continuity editing and match-on-action guides.

## Rules
- Establish an axis of action for dialogue, movement, or combat.
- Preserve screen direction across cuts unless disorientation is intentional.
- If crossing the line, motivate it with a neutral axis shot, wrap movement, or explicit destabilization.
- Cut on motion when possible to hide transitions and preserve momentum.

## Match-On-Action Heuristics
- Cut during the peak readable phase of movement, not after the gesture finishes.
- Preserve action vector and body orientation.
- Use tighter framing on the continuation if emphasizing force or reaction.

## Apply To AI Storyboards
- State motion direction: left-to-right, right-to-left, toward camera, away from camera.
- State whether the shot is maintaining the established axis or intentionally breaking it.
- For battles and chase material, continuity of movement is more important than ornamental angles.
