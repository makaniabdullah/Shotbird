# Cue — skill card

> **House preference (2026-10-21):** Seedance 2.5 is the house main prompting engine. Optimise every prompt for **Seedance 2.5** by default, using the `### Seedance 2.5` template below. Other engines are alternates or named fallbacks only, unless the board's video picker says otherwise. Where a rule below says Seedance 2.0 is the default, read Seedance 2.5.

**Updated:** 2026-10-20 (re-train) · **Agent:** Cue (Shotbird agent 6) · **Mode:** preflight. No project, no generation, no credits; catalog checks were read-only `models_explore` calls.

**Precedence:** the house vault playbooks and `~/.claude/agents/cue.md` come first. The house skills (seedance-prompt-studio, cinema-director-v3, cinematic-prompt-builder, performance-director) come next, then the installed packs, then vendor guides. The live Higgsfield schema beats any skill on what a model accepts.

Vault pages below are optional: skip them if no vault is configured.

## Skills

| Skill | Status | What I use it for |
|---|---|---|
| sb-video-prompting (preloaded) | Loaded: SKILL.md plus the seedance2, seedance2-5, veo3, wan22 and minimax-h3 refs | In i2v the image is the anchor, and settings stay out of the prompt text. The 2.5 FORMAT / TIMELINE / ENDING STATE schema. The MiniMax H3 field schema. |
| sb-visual-video (preloaded) | Loaded: SKILL.md plus seedance, seedance-25, kling, veo, universal-rules, dramaturgy, fixes-and-skeletons | Three-detail check, one camera move, final-image rule, per-engine syntax, failure fixes. |
| **sb-still-motion-director** (new, preloaded) | Loaded in full: SKILL.md, motion-decision-framework, prompt-construction | The motion / micro-motion / static decision, amplitude 0–3, lock lists, bounded ranges, and repair by removing moving parts. Its output form is Chinese-first; I write English. |
| **sb-veo-prompting** (new) | Loaded in full | LOOK → CAMERA → ACTION → FIDELITY → DIALOGUE → AUDIO → EXCLUSIONS. Max 2 beats. Silent-clip recipe, caption tail, the NPOV news-framing block. Written for Flow, so I check Higgsfield params. |
| **sb-wan-3-prompting** (new) | Loaded in full | Its five scene-breaking rules. Wan i2v is motion + camera only. Three verb-driven audio layers, `Image1`/`Image2` binding, Director Mode multi-shot. |
| **sb-dialogue-and-voice** (new) | Loaded in full | Colon dialogue form. No ellipsis and no mid-sentence period. Language named on every line. Line-length table, voice profiles, the silence recipe. |
| **sb-kling-higgsfield-notes** (new) | Loaded in full, checked against the live schema | The live-schema rule, Kling prompt orders, failure table, one-variable settings sweep. Its "no `sound` exposed" note is stale (see Engine sheet). |
| **sb-director-book** (DirectorSKILL, new) | Loaded in full: `ai-video-tool-adapters.md`, `video-prompt-template.md`, `failure-modes.md` | Prompt shapes S1–S4, the motion budget, Runway / Luma / Hailuo / Wan adapters, Templates 1–6 plus the self-check, F1–F19, cost ladder L1–L7, the irreducible list. |
| Higgsfield pack (seedance-2-5, seedance 2.0, camera) | Re-loaded the needed sections (2.5 audio and refs, camera durations; 2.0 grepped) | `{}` dialogue after a language line; speech only in the audio clause; the move must be able to reach the end framing. |
| House skills (Skill tool) | Loaded where installed; `cinema-director-v3` ships with the team edition | Studio: word calibration, Avoid tail. v3: spine, FOV locks, NO BGM, closure protocol. Prompt-builder: motion from frame one. Performance: four pillars. |
| Vendor guides (Seedance 2.5, Veo 3.1, Kling 3.0) | Read in the first preflight; not re-fetched | Notes below |
| Higgsfield catalog | `list` (video) plus `get` on kling3_0, kling_o3_flf, kling3_0_turbo, kling_o3_image_reference, kling3_0_motion_control, wan3_0, minimax_hailuo, sync_so | Engine sheet |
| Vault | The six house pages, plus `tools/wan.md` and `tools/runway.md` | Rules and conflicts below |

**Not available:** `seedance_lint.py`, and the sibling docs the new skills link to (`docs/*.md`, `multiclip-continuity`, `identity-and-likeness`), which were never installed. Every new skill loaded.

## Engine sheet

Every row was verified live with `models_explore` on 2026-10-20. Params go in the board header, never in the prompt text. **No Higgsfield video model below exposes a negative-prompt field or a seed.**

| Engine | Model id | Durations | Ratios | Audio | Frames / refs | Use |
|---|---|---|---|---|---|---|
| **Seedance 2.0** (default) | `seedance_2_0` | 4–15 s | auto, 16:9, 9:16, 4:3, 3:4, 1:1, 21:9 | `generate_audio`, default on | start + end. Refs: 9 image, 3 video, 3 audio | Approved frame to motion. 480p–4K; 1080p and 4K need `mode: std`, since `fast` is 480/720 only. Also `genre` and `bitrate_mode`. |
| Seedance 2.0 Mini | `seedance_2_0_mini` | 4–15 s | same | same | same | 480/720 drafts. A draft proves the prompt, not the take. |
| **Seedance 2.5** | `seedance_2_5` | 4–30 s | same set | default on | start/end **only in `omni_reference`**. Up to 30 images, 50 refs total | Over 15 s, `video_edit`, forward or backward `video_extension`, big reference kits. No 4K. `draft` → `draft_job_id`. |
| **Kling 3.0** | `kling3_0` | 3–15 s | 16:9, 9:16, 1:1 only | `sound` on/off, **default on** | **start_image + end_image only.** No reference role, no cfg, no multi-shot param on this id, despite its tag | Body physics, and the fallback when Seedance morphs a face. `mode` is std, pro or 4k. Set `sound: off` for silence. |
| Kling 3.0 Omni Frames | `kling_o3_flf` | 3–15 s | same | `sound` | start + end, plus `multi_shots` with `multi_prompt` [{prompt, duration}] | Exact landings, or planned multi-shot from an approved frame. |
| Kling 3.0 Omni (refs) | `kling_o3_image_reference` | 3–15 s | same | `sound` | up to 7 `image_references`, **no start frame**; multi-shot | Elements-style identity when there is no approved frame. |
| Kling 3.0 Turbo | `kling3_0_turbo` | 3–15 s | same | no toggle | start only, 720p/1080p | Budget tests |
| Kling Motion Control | `kling3_0_motion_control` | from the driving clip | — | — | image ref + driving video; `background_source` | Performance or camera transfer |
| Kling Omni Edit | `kling_video_edit` | from the source | — | — | video ref + image ref; std/pro/4k | v2v edits (rescuing a nearly-right take) |
| **Veo 3.1** | `veo3_1` | 4, 6 or 8 s | 16:9, 9:16 | native, no toggle | start only | Only when briefed. `quality` is basic, high or ultra; `variant` is preview or fast. |
| Veo 3.1 Lite | `veo3_1_lite` | 4, 6 or 8 s | 16:9, 9:16, auto | `generate_audio`, **default off** | start + end | The Veo route when an end frame is needed |
| **Wan 3.0 / Prime** | `wan3_0` / `wan3_0_prime` | 2–30 s (−1 = auto, unlimited plans only) | auto, 16:9, 9:16, 1:1, 4:3, 3:4 | `generate_audio`, default on | start + end. Image, video and audio refs | Only when briefed. 480/720/1080p. `enable_thinking` (default off) gives better adherence but is slower. House precedent: Prime at 1080p with thinking on. |
| **Hailuo** | `minimax_hailuo` | 6 or 10 s | none (the frame decides) | none exposed | start + end; **no end frame at 512** | Only when briefed: natural physics and facial emotion. Variants minimax-2.3 (default), 2.3-fast, minimax, minimax-fast. 768 by default, 1080 available; 512 is not offered on 2.3. |
| MiniMax H3 / Max | `minimax_h3` / `minimax_h3_max` | param | auto … 21:9 | via schema | start, end, image, video, audio refs | Briefed only; strict schema |
| Sync Lipsync 3 | `sync_so` | follows its inputs | — | the input audio | input video + input audio; `sync_mode` (bounce, loop, cut_off, silence, remap) | A lip-sync pass on a silent take |
| **Runway / Luma** | **Not on the connector** | — | — | — | — | Prompt-only, run by hand. I never upload media. |

**Vendor guides in brief.** **Seedance 2.5:** labelled sections, FOV per segment, no empty establishing shot, audio last, plain "NOT" bans welcome. **Veo 3.1:** cinematography → subject → action → context → style; `SFX:` / `Ambient noise:`; write exclusions as a positive scene; `[00:00-00:02]` blocks for multi-shot. **Kling 3.0:** scene → subject and action → camera → audio; pace with "at the 4th second"; dialogue `Speaker (tone, language): line`.

## Motion decision

Decide this per shot, before writing a word, and record it in the board notes, e.g. `micro-motion · amp 1 · budget 3/4 · locks: label, logo, bottle silhouette`. *[sb-still-motion-director · DirectorSKILL]*

- **Read the frame first:** subject, state (active, resting, paused), the visible cause (gravity, wind, contact, intent), structure, and fragile elements. Separate what I observe from what I recommend.
- **Choose the type:**
  - **Motion:** one restrained, legible action the subject already implies.
  - **Micro-motion:** a breath, a few degrees, a few droplets, one light pass. For quiet, archival or fragile frames.
  - **Static:** when movement would contradict the meaning or break the design (hero pack with a legible label, typographic or poster frame, specimen). Deliver a locked camera with one bounded environmental trace, or flag it to {{NAME}} as a still or an edit hold.
- **Where motion comes from, in this order:** intrinsic action, then a physical reaction (cloth, rope, water, shadow), then an observation effect. Observation is a fallback, never a default look.
- **Limits:** one primary motion, one secondary motion from the same physical cause, and at most one observation effect.
- **Amplitude:** 0 static · 1 micro · 2 restrained · 3 expressive (only when asked). Posters, collages and type frames sit at 0–1; a clearly active body at 1–2.
- **Timing pattern:** hold → action → settle by default. Alternatives: tension → peak → release, or oscillation → smaller → stop. Never loop unless asked.
- **Range is a number:** degrees, cm, % of a region, a count, seconds. Never "move naturally", "come alive" or "cinematic motion".
- **Lock list** (what must not be redrawn). Name the 3–5 most likely to drift; "keep everything else fixed" is not enough. Candidates: typography, logos and brand marks, numbers, labels, UI and screens, product silhouette and hue, frame borders and layout, subject count, identity, wardrobe, proportions, and object connections (straps, handles, cables, joints).
- **Camera test:** would the shot still work if the camera never moved? For type, poster and product frames, lock the camera.
- **A hand operating a branded product is irreducible.** Keep the product static and move the light. Give the hand its own clip of under 1.5 s with contact on the cut, and composite the real mark in post.

## Prompt templates

Board header, outside every prompt: `shot · model id · duration · ratio · res/mode · sound · start frame 03-slate/frames/SXX_vN.png (job <id>) · end frame (if any) · motion decision`.

### Seedance 2.0: flowing sentences, 40–110 words, timed phases, Avoid tail

```
One continuous shot, no cuts. Keep the [subject]'s face, hair, wardrobe and the [location] exactly as in the start frame — [2–3 identity markers]; [named locks] stay fixed. [Camera: one move + speed + FOV° (mm) + endpoint | locked-off tripod, camera completely still]. 0–Xs [hold/start]; X–Ys [one action, ranged]; Y–Zs [settles into the photographable end state]. [One environment motion from a named source]. Light unchanged: [key direction + Kelvin], [palette roles]. Audio: [room tone], [one contact SFX], NO BGM — no background music. The camera does not cut on its own.
Avoid: face drift, morphing, [2–4 shot-specific risks], on-screen text, cuts.
```

*S01 · `seedance_2_0` · 5s · 16:9 · std 1080p · motion · amp 2 · budget 4/4*

```
One continuous shot, no cuts. Keep the woman's face, hair, charcoal blazer and the glass-walled office exactly as in the start frame — dark low bun, silver hoop in her left ear. Locked-off tripod at 47° (50mm), eye level. 0–2s she lifts the pen off the desk, wrist settling; 2–4s she signs, the paper dimpling under the nib; 4–5s her eyes lift off-screen right and hold, jaw set. A monitor behind her glows steadily. Light unchanged: 4300K window key from frame left, 3200K desk-lamp rim; cool grey dominant, warm amber accent. Audio: office room tone, nib scratching paper, NO BGM — no background music. The camera does not cut on its own.
Avoid: face drift, morphing hands, extra fingers, on-screen text, logos, cuts.
```

### Seedance 2.5: `omni_reference` plus `start_image`; labelled schema; windows of at least 3 s

```
FORMAT: one continuous take, real-time, no cuts.
The start frame fixes [composition, identity, wardrobe, set, light]; keep them exactly. [End frame: reach it through one continuous action.]
TIMELINE:
[0-Xs]: [one change, ending in a visible state]
[X-Ys]: [continues from that state]
[Y-Zs]: [final action and settle]
CAMERA: [size, FOV° (mm), path, trigger, stop]
CONTINUITY: [counts, prop ownership, screen direction]
AUDIO: [room tone], <SFX at the moment>, {dialogue only if lip-sync is planned}. NO BGM — no background music.
ENDING STATE: [exact final frame, hold]
CONSTRAINTS: no subtitles, no on-screen text, no logos, [scene-specific collapse points].
```

### Kling 3.0 (`kling3_0`): lock first, then move; positive facts; `sound: off` unless planned

```
Preserve [identity, wardrobe, set] exactly as in the start frame. [Character A: visual label]. Single continuous shot, [one camera move + FOV° (mm)], camera settles into a locked final frame. 0-Xs [action with weight]; X-Ys [contact → deformation]; Y-Zs [recovery and named end pose]. [Positive facts for the top 2–3 risks: "exactly one person in frame", "both hands stay on the rail"]. Light unchanged: [direction + Kelvin]. Audio: [diegetic contact sounds]. NO BGM — no background music.
```

*S07 · `kling3_0` · pro · 5s · 16:9 · sound off · start frame `S07_v3.png`. Board negative (not sent): blurry, distorted hands, melted face, morphing, subtitles, jitter.*

```
Preserve the runner's face, braids, orange windbreaker and the wet stairwell exactly as in the start frame. [Character A: runner in the orange windbreaker]. Single continuous shot, tracking from the side at 63° (35mm), settling into a locked final frame. 0-2s Character A takes the last two steps and her right foot slips on the wet edge; 2-4s her left hand catches the rail, her body swings out and her knee strikes the step; 4-5s she pulls herself upright and stands still, chest heaving, both hands on the rail. Exactly one person in frame. Light unchanged: 5600K skylight from above. Audio: rain on the skylight, sneaker squeak, palm slapping the metal rail. NO BGM — no background music.
```

### Veo 3.1: cinematography → subject → action → context → style; ≤2 beats; exclusions written as a positive scene

```
[One camera move + FOV° (mm) + endpoint | Static shot, camera completely still]. Maintain [subject + wardrobe] from the first frame. [00:00-00:0X] [beat 1]. [00:0X-00:0Y] [beat 2 + settle]. [Context with the absences built in]. [Light: direction + Kelvin]. Keep natural, realistic body proportions. Audio: Ambient noise: [one bed]. SFX: [one event]. [No dialogue, no speech, silent, no music | Speaker label says in <language>: line]. A clean frame with no subtitles, no captions, no on-screen text, no logos.
```

*S10 · `veo3_1` · preview, high · 6s · 16:9*

```
Slow dolly-in at 47° (50mm), eye level, ending on a medium close-up. Maintain the woman, her charcoal blazer and the office from the first frame. [00:00-00:03] she reads the signed contract, her thumb pressing the corner flat. [00:03-00:06] she exhales through her nose and looks up off-screen right, shoulders dropping. The office stays quiet and empty behind her, 4300K window light from frame left, a 3200K lamp warming her cheek. Audio: Ambient noise: low air-conditioning hum. SFX: paper crinkle at 1 second. No dialogue, no speech, silent, no music. A clean frame with no subtitles, no captions, no on-screen text, no logos.
```

### Wan 3.0: motion + camera only in i2v; one action beat; three audio layers written as verbs

```
[Subject as Image1 if refs are attached; never describe the face]. [ONE action beat, ranged and timed, ending in a held state]. Camera: [static, locked-off | push-in | pull-back | pan | tilt | orbit | handheld tracking]. [Wardrobe restated in one clause]. Keep natural, realistic body proportions. Audio. Foreground: [event as a verb]. Bed: [ambience as a verb]. Background: [distant layer]. No music, no dialogue.
```
Board-only negative, 8–20 tokens (Higgsfield has no field for it): `distorted face, deformed hands, flicker, frame hopping, subtitles, text, duplicated people`.

### Hailuo: at most two bracketed camera commands; name an expression endpoint, not an emotion

```
[Static shot] [Subject start state]. [One action, ranged]. [One environment motion]. Ends on [expression endpoint, e.g. "a small held half-smile", jaw set]. Same face, same clothes, same light.
```

### First + last frame (S3): shorter than single-frame; ordered at cut length

```
Use the first image as the opening frame and the second image as the closing frame. The only change is [one of: pose | camera position | light state], through [one continuous action]. Camera [one move with distance over the full duration | holds its position]. Steady, decelerating into the last frame. [Invariants] stay identical throughout.
```

### Runway or Luma (off-connector; run them by hand)

- **Runway:** S1 with one sentence per moving element. If a camera slider is set, delete every camera word. Brush only the region that moves. Turning a subject around produces mush. Budget ceiling 5.
- **Luma:** S3 keyframes. Both frames share one lens family, one light state, and head size within about 20%. A loop needs a returning pose. Re-anchor every 2–3 extends.
- Both: write every exclusion as a positive fact.

## Dialogue & lip-sync rules

1. **Speaking mouths stay off-screen by default.** Lines go to VO or listener coverage at the planning stage. Every dialogue shot gets a fallback (an audio bridge over a listener insert, hands or an object) and 1–2 s handles. *[vault lip-sync-dubbing · cue.md · F15]*
2. **Lock the voice before the picture.** The voice timing sets shot length: about 2.5 English words per second, plus pre-roll before the first word and a hold after the last. *[vault · DirectorSKILL Template 6]*
3. **A visible mouth gets a small job.** One speaker per clip, MCU or tighter, ≤6 words, clip ≤5 s. Line lengths: 2–4 words best, 5–7 good, 8–10 acceptable, more than 10 split. Veo speech ≤8 s. *[F15 · sb-dialogue-and-voice · Veo]*
4. **Engines for planned lip-sync.** Kling 3.0 with `sound: on`, Veo 3.1, or Seedance 2.5 with the v3 closure protocol (bilabials counted, a mouth-visible CRITICAL block, no cuts mid-word). The alternative: **generate silent, then run `sync_so`** on the locked audio, since asking for speech and performance in one generation often costs both. Wan sync is approximate. Keep dialogue off 2.0. *[DirectorSKILL Kling · v3 · Wan §1 · catalog]*
5. **Format per engine.** Labels are visual attributes, never pronouns or names.
   - Veo: `The woman in the grey coat says in English: line`. The colon form is the default; the quoted form is a fallback if speech won't trigger *[CONTESTED]*.
   - Kling: `[Character A: visual label, tone, language]: "line"`, with the action before the line and connectors (immediately, after a beat).
   - Seedance 2.5: a language line, then `{line}`, inside the audio clause only.
   - Wan: `[Label, tone]: "line"`.
   - MiniMax H3: `(S1)` … `<d>[English] words</d>`.
6. **Punctuation and language.** No ellipsis and no mid-sentence period; use commas and punctuate only at the end. Name the language on every line and every murmur. Keep accents and spell out numbers. *[sb-dialogue-and-voice]*
7. **One voice profile per speaker** (gender, language and accent, energy, delivery, emotional quality), reused word for word in every clip. Age goes in the voice profile only, never in the picture description. *[sb-dialogue-and-voice · age-blind rule]*
8. **Speech lives only in the audio clause.** Quoted subtext in the action ("a look that says…") gets voiced. *[higgsfield-seedance-2-5]*
9. **Silent shots:** no speech cue anywhere. Never write a mouth action ("lips part", "as if to speak"). State the silence positively: "No dialogue, silent scene, mouth closed", plus one ambient bed. No `Audio language:` line. Kling gets `sound: off`. *[sb-dialogue-and-voice §7 · Veo §2]*
10. **Audio hierarchy:** dialogue, then one SFX tied to a visible action, then one bed of 3–5 concrete sounds. Music is never generated; it goes in post, ducked −8 to −12 dB. *[sb-dialogue-and-voice · v3 NO BGM]*
11. **Known audio killers:** characters who read as under 18; upscaling 720p → 1080p, which can strip audio; news-broadcast framing, which hits the NPOV block. *[sb-dialogue-and-voice §8 · Veo §4]*

## Morph risks

**The rule:** if the first and last frames differ in more than one of **pose, camera position or light state**, the model morphs between them instead of moving. *[DirectorSKILL S3]*

- **Pair check on every end-frame shot.** Count the axes that change. One passes. Two or more: build a middle keyframe and make it two clips, or re-render the end frame so it matches on the other axes. Also check that both frames share one aspect ratio and one lens family, and that head size stays within about 20%.
- **Other morph triggers I design out:**
  - rotation past about 45°, or a turnaround (F3)
  - occlusion and re-reveal, or a prop or person leaving and re-entering frame (F19)
  - subject, camera and environment all moving at once (F3)
  - a state change mid-shot, such as a light switching, clothing changing or an object vanishing: cut instead (Wan rule 1)
  - long face clips: identity decays with frame index, with onset after about 60–70% of the clip (F1)
  - an extend asked to change setup, since an extend can't cross a cut (F18)
  - mirror reflections, two-person contact, crowds of resolved faces, exact counts (the irreducible list)
- **Repair**, in order: diagnose one F-code per symptom. Two codes in one clip means re-plan (L5). Then climb the ladder: L1 prompt → L2 params (shorter, lower mode) → L3 at most two re-rolls → L4 rebuild the keyframe → L4.5 v2v (Kling Omni Edit) → L5 split → L6 trim in the edit → L7 cut. After three strikes, change the shot, not the prompt. If Seedance morphs a face, move the shot to Kling 3.0. *[failure-modes · cue.md]*

## My working rules

1. **Decide motion before words.** Motion, micro-motion or static. One primary motion plus one secondary from the same cause. Name the amplitude. *[still-motion-director]*
2. **The start frame is the authority: write change, not appearance.** A lock sentence plus 2–3 identity markers. Never re-describe the frame or name what it doesn't contain (that invites hallucination). Wan i2v gets motion + camera only. *[cue.md · sb-video-prompting · Wan §2 · DirectorSKILL S1]*
3. **Name the locks.** List the fragile elements that drift (type, logos, product hue, connections, counts) as a lock clause, not a description. *[still-motion · DirectorSKILL slot 6]*
4. **Score the motion budget before writing.** Subject 0–3, plus camera 0–3, plus environment 0–3. Multiply by 1.0 (≤5 s), 1.3 (6–10 s) or 1.6 (>10 s). Add 1 for each extra actor, for a face over ⅓ of the frame, for fine hand work, and for each reference beyond the first. Ceilings: 4 close character, 6 medium/wide with people, 8 no face. Per-engine ceilings: Runway, Luma, Hailuo and Seedance-with-face 5; Kling and Wan 6; Veo 6, minus 2 when speaking. Over budget → split. *[DirectorSKILL motion budget]*
5. **One objective, one camera move, one photographable end state.** Timed beats are phases of one objective (hold → action → settle), never two objectives. Wrap them in the oner lock. Veo gets ≤2 beats; Wan and Kling get one action. *[cue.md · Template self-check · Wan rule 2 · Veo §1]*
6. **Camera: one move.** Give it a speed, FOV in degrees with mm in brackets, a trigger and an endpoint, and check that the move can actually reach the end framing. Give micro-moves as cm over seconds. Leaving the camera unmentioned does not lock it: write "locked-off, camera completely still". Never write "zoom" for a dolly. *[higgsfield-camera · Veo · Wan rule 5 · F6]*
7. **No state change inside a shot.** Light switches, vanishing props, wardrobe changes and occlusion reveals become cuts. Contact and impact land on the cut; show the anticipation or the consequence. *[Wan rule 1 · F14 · F19]*
8. **Emotion lives in the body.** 2–4 observable cues per transition, brow and forehead matched to the beat, a stated eyeline, and an expression endpoint rather than an emotion word. *[dramaturgy · v3 slot 14 · performance-director · Hailuo adapter]*
9. **Physics is a causal chain.** Mass or scale in real units, then contact, deformation, recovery, lagging cloth or hair, and a contact shadow. Pace is a number ("one footfall every 0.55 s"), never "fast". *[v3 slot 13 · F13/F14 · vault Kling scale lesson]*
10. **Light and grade stay as in the frame.** Key direction, Kelvin, and palette roles tied to sources. No fixture names, no beauty light, no mid-shot change. *[cue.md · v3 slot 10 · F12]*
11. **Duration fits the action.** Use the shortest length that fits, plus a 0.5–1 s hold. Face shots run 4–5 s on Seedance and 3–5 s on Kling. Over 8 s only for shots with no face, one environmental motion and a slow camera. *[DirectorSKILL duration strategy · F1 · kling notes]*
12. **Exclusions go where the engine reads them.**
    - Seedance gets an "Avoid:" tail plus the board field.
    - Kling, Veo, Wan and Hailuo on Higgsfield have no negative field. Their top 2–3 risks become positive facts in the prompt ("exactly one person in frame"), and the nouns go on the board only.
    - 4–6 targeted items, each tied to a real risk. Never negate what the still already prevents.

    *[seedance-prompt-studio · DirectorSKILL negatives · live schema]*
13. **Always direct the audio.** Audio is generated whether or not I write it. Diegetic only, one SFX and one bed, with "NO BGM — no background music" as plain text, never inside `( )`. Kling `sound` defaults on: set it off unless the shot is planned with sound. *[v3 slot 15 · sb-dialogue-and-voice · catalog]*
14. **No generated text or logos, and no settings in the prompt.** Copy goes in post. *[vault keyframe-prompting · sb-video-prompting · F11]*
15. **Age-blind, with no names.** Use role, hair, wardrobe and markers. Kling and Wan get visual labels (`Character A`, `Image1`), never pronouns. *[ENGINE-RULES rule 1 · v3 · Wan rule 3]*
16. **Route engines.**
    - Seedance 2.0 is the default.
    - Kling 3.0 for body physics, or after a face morph.
    - Seedance 2.5 for shots over 15 s, edits or extends.
    - Veo, Wan, Hailuo or MiniMax only when briefed.
    - Runway and Luma: prompts only, run by hand.
    - If {{NAME}} names an engine, use it everywhere. Re-check the live schema with `models_explore` before a run.
    - `ip_detected` is final: flag it.

    *[cue.md · vault · kling-notes live-schema rule]*
17. **Use an end frame only for a match cut or an exact landing,** and only when the pair passes the morph check. The pair prompt is shorter and ordered at cut length; dialogue pairs keep their handles. *[cue.md · DirectorSKILL Template 2]*
18. **Every prompt stands alone, and I preflight it by hand.** Repeat the locks word for word. Then check:
    - the five self-check questions: one action, one move, an end state, the invariants, negatives matched to real risk
    - three details per shot
    - the beats add up to the duration
    - no homographs (tearing, shoot, draw…) and no age words
    - no exit-and-re-entry and no reflections

    *[vault keyframe-prompting · universal U7 · DirectorSKILL self-check · ENGINE-RULES]*

## Conflicts resolved

House style wins: first the vault and cue.md, then the house skills, then the packs.

| Conflict | Resolution |
|---|---|
| Negatives inside a Seedance prompt (the Higgsfield pack says positive only, DirectorSKILL says naming a noun summons it, studio says always "Avoid:") | **Studio.** A short Avoid tail plus the board field, with positive locks first. On engines with no field, the exclusions become positive facts. |
| Time markers under 10 s (studio says none) | **cue.md.** Timed phases of one objective, wrapped in the oner lock. |
| Prompt length (Higgsfield 50–80, DirectorSKILL 40–80 for i2v, studio up to 180, Veo skill 100–200) | Single-shot i2v runs 40–110 words, about 50–90 at 5 s. Pair prompts run shorter. Multi-shot, long or lip-sync work uses the v3 spine. |
| Identity text with a start frame (v3 Assets lines run 60–110 words) | **cue.md.** A lock sentence plus 2–3 markers. Full Assets lines only for reference shots with no start frame. |
| Prompt language (DirectorSKILL: Chinese for Kling, Wan and Jimeng) | **English.** v3 house rule, and Higgsfield is English-first. Chinese only if {{NAME}} asks; it is untested here. |
| Kling's negative field (DirectorSKILL and vendor say there is one) | **Live schema.** None on Higgsfield, so positive facts in the prompt and nouns on the board. |
| Kling `sound` (kling-notes say it isn't exposed) | **Live schema.** `sound` on/off, default on. |
| Wan `negative_prompt`, and audio input (the Wan skill says a field exists and audio input doesn't) | **Live schema.** No negative field. `audio_references` is listed but untested. |
| Dialogue quotes (Veo guide uses quotes; field testing prefers the colon form) | **Colon form by default, quotes as a fallback.** Kling and Wan keep their own label + quote formats. |
| Mouth on silent faces (my old "stated at-rest mouth" vs "never mention lips") | State "mouth closed" only. Never write a mouth action. |
| Mouths on screen (v3 protocol vs vault off-screen default) | **Vault.** Off-screen by default. The closure protocol only for planned lip-sync shots, each with a fallback. |
| Music suppression ("NO BGM" vs "No music.") | **v3.** "NO BGM — no background music" as plain text. On Veo, "no music" is the one licensed negation. |
| Character names | **v3.** Visual descriptors and labels only. |
| Face-heavy shots on 2.0 (the visual-video pack says route faces elsewhere) | **cue.md.** Start on 2.0. After a morph or refusal, move to Kling 3.0. |

## Update 2026-10-21. Overrides anything above
- The house `cinema-director-v3` skill is your prompt grammar. Read the full `~/.claude/skills/cinema-director-v3/SKILL.md` every prompt job, and write on its 16-slot spine. The video picker answers its Step Zero (default Seedance 2.5).
- **Detailed prompts:** fill every slot concretely. A Seedance 2.5 shot is typically 350–700 words. Ignore any older "keep it short" guidance above.
- **NO MUSIC, JUST SFX:** the Audio slot reads `SFX only — <timecoded diegetic sounds>. NO music, NO score, NO BGM, NO song, NO voiceover.` Any older audio guidance above that allows music is void. `sb prompt` enforces this.
- Prompts are for approved, ungated shots only (`$SB gate <slug> --shot S##`).
