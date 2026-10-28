---
name: sb-frame-qc-refs
description: "Shotbird crew skill (Hawk): reference pack for judging AI storyboard frames. Covers start/end-frame consistency (BLOCK and WARN), the photoreal 'AI polish' critique rubric, and DirectorSKILL's keyframe QC gate and coded failure modes. Use inside Shotbird runs when reviewing frames."
---

# Frame QC references (Shotbird · Hawk)

These are cherry-picked references. Read the one that matches the check you're making. The verdict rules in your own `hawk.md` and Abdullah's house style always win.

| Check | Read | Gives you |
|---|---|---|
| Start/end frames, set pieces, lighting inside a shot | `references/consistency-verification.md` | BLOCK/WARN rules. Do the two frames differ enough to animate? Only lighting or background changed → BLOCK. |
| Realism and "AI polish" | `references/photoreal-critique.md` | A render-tell rubric with one fix per failure. Uniform micro-detail from front to back is the most reliable tell. |
| Keyframe pre-generation gate | `~/.claude/skills/sb-director-book/assets/qc-checklist.md` | A weighted gate with go thresholds: hands, focal-length perspective, rendered text, first/last match. |
| Failure codes with before/after fixes | `~/.claude/skills/sb-director-book/references/failure-modes.md` | F1–F19 (F10 anatomy, F11 text artifacts). Cite the code in fix notes. |

Sources: see ATTRIBUTION.md.
