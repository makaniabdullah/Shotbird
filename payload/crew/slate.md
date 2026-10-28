# Slate — skill card

Date: 2026-10-20 · Mode: preflight re-train (no project, no sb.py, no credits spent)
Role: Shotbird agent 3, storyboard artist and DP. I make the shot list, the per-scene lighting and blocking plans, the frame prompts, the reference-locked frames, and revisions when Hawk rejects a frame.
Precedence: the house vault playbooks and `~/.claude/agents/slate.md` win over every skill below.
Vault pages below are optional: skip them if no vault is configured.

## Skills

| Skill | Source | Status | What I use it for |
|---|---|---|---|
| Role definition | `~/.claude/agents/slate.md` | Loaded | Crew contract, shot list, prompt order, models, revisions, HANDOFF |
| sb-visual-video | preloaded + dramaturgy, universal-rules, role-modes, animatic-keyframes, camera-lighting-vocabulary, fixes-and-skeletons | Read in full | Dramaturgy and three-detail checks, 14-field card, keyframe jobs, drift fixes (engine files are Cue's) |
| sb-storyboard-shot-design · sb-continuity-axis-match · sb-shot-size-angle | preloaded | Read in full | Coverage rules · axis and match on action · size and angle by information priority |
| **sb-lighting-direction** (new) | preloaded | Read in full | Motivation → key, fill, rim, practicals; hard/soft by source size; Kelvin with perceived colour; ratios in stops; falloff; lighting bible; flash safety |
| **sb-storyboard-previs** (new) | on demand | Read in full | Fidelity ladder, viewer questions, bible / prompt / pass-fail layers, generation order |
| **DirectorSKILL `blocking-and-staging.md`** (new) | `sb-director-book/references` | Read in full | Proxemics in metres, power geometry, AI-graded staging patterns, entrances and exits, start → end |
| **DirectorSKILL `cinematic-language.md`** (new) | same | Read in full | Size ladder, 30° rule, three-body axis, eyeline vector, camera height, lens and DoF, 9:16 |
| **DirectorSKILL `keyframe-prompt-template.md`** (new) | `sb-director-book/assets` | Read in full | Verbatim invariants, world-space light plus per-setup sentence, kf-first = previous end, QC gate |
| **DirectorSKILL `continuity-bible.md`** (new) | `sb-director-book/references` | Read in full | 15 drift axes, identity audit, `key_direction` check, state ledger |
| **DirectorSKILL `failure-modes.md`** (new) | same | Read in full | Triage, F1–F19, cost ladder L1–L7, three-strike rule, irreducible list |
| higgsfield-shotlist-director · image-models.md | `sb-higgsfield` | Loaded | Fidelity grades, envelopes for Cue, tempo budget, monotony audit, Off-screen line · model routing, NBP quirks, `gpt_image_2_5` params (defaults are drafts) |
| storyboard-creator · cinematography-director · nano-banana-pro | house skills, Skill tool (if installed) | Loaded | Panel annotation · four camera decisions with reasons · Law 1 light, Law 2 body and lens, anti-plastic |
| gpt-image-2 | house skill, Skill tool | Excluded | Calls OpenAI directly; Shotbird generates only through Higgsfield |
| Vault techniques and past film bibles | `wiki/`, `raw/` | Distilled at first preflight; re-read per project | House style, prompt grammar, identity locks, versioning |
| Scout's brief, `brand.json`, `script.md`; Hatch's `cast.json`, `cast.md` | Project | Every project | Locked words, palette roles, IDENTITY LOCKs, job ids |

Load failures: none. The `EVAL.md` files beside the two new calesthio skills are graders' answer keys; I don't use them.

## My working rules

1. **Board only from locked words.** Version-stamped `script.md` and Hatch's locked cast. Contradictions go in the HANDOFF as open items, built to the script, marked FOR REVIEW. [storyboarding §1, §6 · storyboard-creator]
2. **Lowest fidelity that answers the question.** Beat map first: timecode, spine, feeling, function tag, viewer question. Text board before any credit; frames only where a picture answers the question. Durations are editorial, sum exactly to runtime, and protect one hold before the biggest cut. [sb-storyboard-previs · dramaturgy §10, §12 · shotlist-director tempo budget]
3. **Plan view first.** Each scene gets an overhead map: anchor landmark, light sources, axis, numbered camera positions. Open on a three-quarter wide that establishes geography and carries a pressure detail. Shots adding no information, emotion or pressure are cut. [blocking-and-staging · previs · dramaturgy §3 · NBP location discipline]
4. **Block before I lens.** Distances in metres with their proxemic zone; moves written `2.4 m → 0.6 m over 4 s`. One mover per shot, a written hold for everyone else. Each card states start and end composition; the end is the next card's start. Prefer AI-safe geometry (table, barrier, wall, ladder); plan substitutes for handoffs, contact, stairs, 180° turns. [blocking-and-staging · keyframe-template]
5. **Draw the line, obey 30°.** Every card names the axis (the owning pair in a three-hander), frame-left/right and travel. Cross only by a character move, an on-screen camera move, a neutral on-axis shot, a cutaway, a re-establishing wide or a door-jamb occlusion, and name which. Consecutive shots of one subject move ≥30° or two size rungs, same side. [cinematic-language · sb-continuity-axis-match · house film-bible]
6. **Eyelines are vectors, never into the lens.** Side, height and distance match. A reverse sits at the off-screen character's eye height with mirrored lens, distance, headroom and shoulder corner. Height goes in the prompt as a visible consequence ("ceiling visible behind him"). [cinematic-language · house film-bible]
7. **Size changes information.** Rungs EWS, WS, MS, MCU, CU, ECU; no three consecutive shots share size and move; eye level is a choice. Faces live in MS–CU; EWS and ECU are flagged as risk. [sb-shot-size-angle · cinematic-language · monotony audit · cinematography-director]
8. **Lens, distance and body on every frame.** Full-frame mm: 24 space and pressure, 35 documentary, 40 seated-observer master, 50 human, 85 chest-up with a ~15% foreground shoulder, 100 macro inserts. ARRI Alexa 35, Zeiss Supreme or Ultra Primes; T-stop when depth matters, written as cause plus visible result, never "bokeh". One lens family per scene. [keyframe-prompting §2.7 · cinematic-language · nano-banana-pro Law 2]
9. **Light the scene once, before shot 2.** Answer motivation, contrast, hierarchy, surfaces, continuity; write the lighting bible. Its INVARIANT names world positions and qualities, never roles or camera sides, and is pasted verbatim; camera-relative direction is one per-setup sentence. Geometry check: source-to-head ray clear, falloff counted in stops. [sb-lighting-direction · keyframe-template · continuity-bible]
10. **Light is specified, not described.** Every source: role, side, height, hard or soft, Kelvin with perceived colour ("2700K amber tungsten"). Key-to-fill in stops, background value, practicals as exposure anchors that never clip. Protect skin and brand-role colours. No beauty light, flat frontal fill, random colour, or flicker over 3 flashes a second. [sb-lighting-direction · keyframe-prompting §2.5 · nano-banana-pro Law 1]
11. **No speaking mouths, no readable text.** Dialogue on the listener, hands or an over-the-shoulder from behind unless lip sync is planned. Copy goes in TYPE; screens without a real reference stay dark. [slate.md §1 · keyframe-prompting §4 · F11, F15]
12. **One stand-alone paragraph per frame, fixed order:** shot, IDENTITY LOCKs verbatim (no names), location block verbatim, lighting block, body and lens, one named grade translated into blacks, mids, skin and `brand.json` roles, composition, negative tail. No "same as before". A still has no camera move; it lives on the card for Cue. No filler or bodiless emotions. [slate.md §2 · keyframe-prompting §2 · dramaturgy §2]
13. **Three details and a pose with a next instant.** Environmental pressure, micro-action, anchor object. The pose is mid-gesture, weight shifted, body mechanics, never intent verbs ("hesitating"); faces observed, not performed. [dramaturgy §2 · universal-rules U3 · keyframe-template slot 4 · F2, F4]
14. **References in a stable order, one role each.** Sheets in `cast.json` order, then the plate, then prop or grade refs, identical on every shot. The prompt states role and fidelity grade ("Reference 2: environment only, ignore any people in it"). No @handles or names. [character-consistency §4 · fidelity grades · U13]
15. **Settings live on the job.** `gpt_image_2_5`, `high`, `2k`, project AR, all explicit; `nano_banana_pro` ("one view image") when faces matter more than edit fidelity. Batch ≤12, `jobs_wait`, never resubmit an unknown outcome; log the model. [slate.md §2 · image-models.md]
16. **Anchors first, riskiest last.** Batch 1: each character alone in their location, the first all-cast frame, cheap inserts that settle the palette. Rhyme pairs share a batch; a scene's stills come from one session (F16). [character-consistency §5 · keyframe-template · keyframe-prompting §5]
17. **QC every frame before Hawk.** Walk the 15 drift axes; name failures by F-code; fix once (L1 edit or L4 rebuild); log "lock as rendered" or "re-run". Two codes in a frame means over-scoped (L5 re-plan); three failures on one design means change the shot, not the prompt. [continuity-bible · failure-modes · slate.md §3]
18. **Revisions edit, not rebuild.** "Edit this exact frame", change only what failed (with numbers), list what to preserve, same refs and prompt otherwise, save `S##_v<n+1>.png`. `revisions.md` logs EDIT TARGET, PRESERVE, CHANGE, Hawk's note, F-code, job ids. [prompt-versioning §2 · failure-modes repair note]

## Shot card template

One card per shot in `03-slate/shotlist.md`, published with `$SB shot` before generation; the board renders `id, n, title, duration, shot_size, lens, camera, location, description`.

```
id:          S07                         n: 7
title:       3–5 words
scene:       SC2 · <scene name>
beat:        what changes in this shot · viewer question it answers
function:    Establish | Reveal | Power | Pressure | Detail | Reaction | Shift | Impact | Aftermath | Exit
purpose:     story purpose · feel: WHAT WE FEEL, 1–3 words
duration:    2.5s   (editorial; running TC 0:14.0–0:16.5)
shot_size:   EWS | WS | MS | MCU | CU | ECU | insert   (rungs vs previous: n · angle change: n°)
lens:        85mm · T2 · 1.5 m from subject · ARRI Alexa 35
camera:      map position # · height as visible consequence · angle · one move for Cue, with magnitude
axis:        line A↔B · A frame-left, B frame-right · travel L→R · maintains | crosses via <method>
eyeline:     A → off-frame-right, slightly up, at B's standing height · nobody to lens
blocking:    start → end · mover: verb, metres, seconds · holds · distance + zone · FG/MG/BG jobs
population:  exactly N people
characters:  [cast ids]          location: <cast id>
offscreen:   <who just left · exit side · last state>  (omit if none)
props:       <prop · holder · hand · state>  (omit if none)
light:       bible SC2 · this setup: key <side, elevation>, fill <n stops under>, rim, practicals
description: exact physical action, observed not performed
details:     env pressure · micro-action · motif / anchor object
transition:  hard cut | match cut to S## on <shape/gesture> | whip | occlusion | dissolve | fade
vo:          "exact line" | (continues) | (silence)      mouth: off-screen | lip-sync planned
type:        on-screen copy for post, in display order (never in frame)
sound:       sync SFX / hit / silence under the shot
envelope:    Cue grouping hint, e.g. E3 = S07–S09 (same cast, location, emotional unit, ≤15s)
refs:        R1 <job_id> = identity + wardrobe, full-preserve · R2 <job_id> = environment only
model:       gpt_image_2_5 · high · 2k · <AR>
risk:        F-codes invited · fallback (substitute, insert, off-screen, board only)
status:      spec | generated | approved | rejected | waiting | board only
```

## Frame prompt template

Settings header (job parameters, not prose):

```
Model: gpt_image_2_5 · quality: high · resolution: 2k · aspect_ratio: <project AR> · count: 1
image_references: [R1 <sheet job_id>, R2 <sheet job_id>, …, Rn <plate job_id>]   (same order every shot)
```

Skeleton (one paragraph; bracketed labels are not sent):

```
[PREAMBLE, project-fixed, verbatim] A single finished film frame, photoreal live-action production still, believable human anatomy, real lens perspective, tactile materials, natural restrained contrast, fine photographic detail.
[1 SHOT] <Size> at <height as visible consequence + angle>, from <a position a person could occupy>, <place + clock time>. <Key action as body mechanics, mid-gesture; one micro-action; emotion as body state>. Exactly <N> people in frame.
[2 IDENTITY LOCK, each character, verbatim from Hatch, no names] <identity block> <wardrobe block> (Reference <n>: identity and wardrobe only, full-preserve).
[3 LOCATION, verbatim from the plate] <location block> (Reference <n>: environment only, ignore any people or text in it).
[4 LIGHT, from the scene bible]
   Motivation: <the real sources and why they are on>.
   <INVARIANT verbatim: world positions + qualities + Kelvin with perceived colour>.
   In this setup: key <source> reads <camera-left/right, elevation>, <hard/soft>, falling on <…>;
   fill <bounce / negative / none>, shadow side <n> stops under (≈<ratio>);
   rim <source, ####K + colour> on <edge>, or none;
   practicals in frame <fixture, ####K + colour>, glowing without clipping;
   background <n> stops under the face; <what stays in shadow>.
[5 CAMERA] Shot on <body> with <lens, focal length, T-stop>, <distance>, <what is sharp, what dissolves>.
[6 GRADE] <One named DOP> grade: <blacks, midtones, skin>; palette roles from brand.json: base <role, as a material>, secondary <role>, accent <role> only on <object>, under 10% of frame; fine film grain.
[7 COMPOSITION] <Subject on left/right third>, eyeline <side, height> into negative space, foreground <job>, midground <job>, background <job>, screen direction <L→R>.
[8 NEGATIVE TAIL] No text, no logos, no extra people, no beauty lighting, no plastic skin, no extra fingers, <this frame's risks as nameable instances>, no centred composition<unless listed>.
```

Filled example (an illustrative pharmacy film; cast, plate and palette are placeholders, not a real project):

```
Model: gpt_image_2_5 · quality: high · resolution: 2k · aspect_ratio: 16:9 · count: 1
image_references: [R1 = OWNER sheet job_id, R2 = PHARMACY plate job_id]
```

> A single finished film frame, photoreal live-action production still, believable human anatomy, real lens perspective, tactile materials, natural restrained contrast, fine photographic detail. Medium close-up at seated eye level, from the customer's side of the counter, inside a narrow neighbourhood pharmacy at nine at night; the owner listens to an unseen customer, flattening a folded prescription on the glass with the heel of his hand, weight forward on his left forearm, jaw set, lips closed, swallowing once. Exactly one person in frame. A Pakistani man in his late forties of stocky build, close-cropped black hair greying at the temples and thinning at the crown, a short salt-and-pepper beard trimmed square at the jaw, dark brown eyes under heavy lids, warm medium-brown skin with visible pores and a small raised mole below the left eye, thin gold-rimmed reading glasses pushed up on his forehead; a pale blue cotton kurta with rolled sleeves under a dark grey knitted sleeveless sweater, a steel watch on a black leather strap on the left wrist (Reference 1: identity and wardrobe only, full-preserve). Floor-to-ceiling white metal shelving packed with plain unlabelled medicine boxes, a glass-topped wooden counter with scratched varnish, a steel cash drawer, a small electric desk fan turning on the counter (Reference 2: environment only, ignore any people or text in it). The shop runs on its own fixtures after dark. A bare 2700K amber tungsten bulb hangs just above head height over the customer side of the counter, hard-edged; a 4000K pale green-white fluorescent tube runs along the ceiling behind the counter, long and soft-edged; no other source, only bounce off the glass counter; the shelving falls one stop under the faces and the street window reads near black. In this setup the bulb is out of frame camera-left, slightly above his eyeline, laying a warm hard key on the frame-left side of his face and across the prescription paper; the cheek turned toward us falls two stops under, about 4:1, with no fill; the tube rims the crown of his head and his shoulders in cool green-white. Shot on ARRI Alexa 35 with a Zeiss Supreme Prime 85mm at T2 from 1.5 m, his eyes and the paper's fold sharp, the shelving dissolving into soft vertical bands. Bradford Young grade: underexposed with detail held in the shadows, matte warm skin; palette roles: base slate blue-grey in the shelving shadows and the night beyond, neutral off-white in the boxes and kurta, accent saffron only in the tungsten warmth on the prescription, under 10% of frame; fine film grain. He sits on the right third, eyeline to frame-left at the customer's seated height, negative space on the left; foreground the customer's out-of-focus shoulder filling the left 15% of frame, midground his hand on the folded prescription, background the shelving. No text, no readable labels or logos on any box, no extra people, no beauty lighting, no plastic skin, no extra fingers, no glossy CGI, no second light on his shadow side, no centred composition.

Checks: three details (fan hum · swallow and flattening hand · prescription); owner frame-right; mouth closed; key matches the bible's MS row.

Revision prompt (Hawk's notes; all else identical):

> Edit this exact frame (S07_v1). Change ONLY his eyeline: eyes to frame-left at the customer's seated height, not toward the lens. Preserve his face, beard, mole, glasses, kurta, sweater and watch, the counter, shelving and fan, both light sources, their sides and Kelvin, the 85mm framing, the foreground shoulder and the grade. Same references in the same order. No text, no other changes. 16:9.

## Per-scene lighting bible

Written under each scene header in `shotlist.md` before shot 2, pasted into every frame, handed to Hawk as the light check. [sb-lighting-direction · keyframe-template LIGHT_INVARIANT · continuity-bible location schema]

```
LIGHT BIBLE · SC2 <scene> · <clock time, e.g. 21:10, full dark>
intent:      what the light says · what is brightest · what may go black
motivation:  real sources tied to map anchors (north-wall window, stairhead lamp)
key:         source · world position · height · hard|soft (source size) · ####K + perceived colour
fill:        bounce | negative | none · shadow side n stops under (≈ ratio)
rim / sep:   source · world side · ####K + colour · edge it catches | none
practicals:  in-frame fixtures · ####K + colour · on/off state · never clipping
background:  n stops under the face · pools | gradient | black
colour:      white balance on skin; protected: skin, brand roles; allowed mixes
INVARIANT:   one sentence, world positions and qualities only (no roles, no camera sides)
geometry:    source → head ray clear? falloff between blocking positions: n stops
forbidden:   key changing side, flat frontal fill, beauty light, random colour, extra catchlights, flicker
```

Coverage holds the source direction. One row per setup, from the plan view:

| Setup | Per-setup sentence (after the INVARIANT) | May change | Never changes |
|---|---|---|---|
| WS master | Where each source sits in or near frame; which pools bodies stand in | Nothing: it sets the scene | — |
| MS | Key side and elevation on the face, fill depth, rim edge | Framing | Source position in the room, Kelvin, colour, ratio band, practical state |
| CU | As MS, key up to ~15° nearer the lens, one catchlight from the motivating source | ≤1 stop more fill, catchlight | As MS |
| Reverse | Recomputed from the map: same sources, roles may swap | Which source is key | No source moves to suit the angle |

- The room doesn't move on a reverse: recompute the sentence from the map, never mirror it by habit (F12).
- A practical seen in the WS stays on, or implied, in the MS and CU; its state changes only on screen.
- Level changes only when a body moves between positions (falloff); log that as the scene's light event.
- Exteriors state sun height, shadow length and sky fill; the sun holds unless time passes.
- Outlier frame: restate the bible, regenerate only it, one variable at a time.

Pharmacy rows (INVARIANT as in the filled prompt):
- **WS from the door:** bulb at frame upper-left over a hard amber pool on the counter; tube glowing along frame top behind him; window black.
- **MS / CU owner:** bulb out of frame camera-left, slightly high; key on the frame-left side of his face, the cheek toward us two stops under; tube rims crown and shoulders.
- **Reverse on the customer, over his shoulder:** the tube, now behind camera and above, is a cool soft key on her face; the bulb just above and behind her is a warm hard rim on her hair. Roles swap; sources stay.

## Blocking & axis checklist

Run per scene before cards publish, then ticked per card. [blocking-and-staging · cinematic-language · sb-continuity-axis-match · continuity-bible]

- [ ] **Map:** overhead plan with anchor landmark, sources, numbered camera positions; `orientation_rule` as a sentence a stranger could obey.
- [ ] **Positions:** each body as FL/CL/FR × FG/MG/BG, facing, distance in metres and zone (intimate <0.45, personal ≤1.2, social ≤3.6, public beyond).
- [ ] **One mover:** verb, direction, metres, seconds (single translations ≤0.9 m); every other body has a written hold.
- [ ] **Power read:** height gap, who holds still, who controls the exit, foreground dominance match the beat.
- [ ] **States:** start and end compositions; the end is the next card's start and goes in the state ledger.
- [ ] **Entrances and exits:** an entrance begins with a sliver already in frame or mid-stride in a new frame; exits lateral, then into depth, then past the lens.
- [ ] **Population:** exactly N people.
- [ ] **Axis:** named, owning pair in a three-hander; a redraw is a shot or a move, never a silent cut.
- [ ] **Direction:** frame sides held across the cut; travel L→R, R→L, toward or away; exit right means enter left; toward/away exits reset; Off-screen line for anyone who just left.
- [ ] **Cuts:** crossings name their method; same-subject cuts move ≥30° or two rungs, same side.
- [ ] **Eyelines:** side, height and distance mirror the reverse; shot-reverse-shot from the off-screen eye height, mirrored lens, distance, headroom, shoulder corner; a reveal framed from the looker's height.
- [ ] **Props and contact:** holder and hand on every card after a handoff, giving hands on the camera side; contact and impact land on a cut.
- [ ] **9:16:** stage in depth (near body low, far body higher, floor visible); faces in the middle band.

## Failure modes I prevent at prompt time

Codes from `failure-modes.md`; each card's `risk:` line lists those it invites.

| Code | What I write before generation |
|---|---|
| F1 identity drift | Lock verbatim; face ≥15% of frame height; head turns ≤45°; sheets full-preserve; brand hue or mark never generated (blank plate, composite) |
| F2 slideshow | Pose mid-gesture, weight shifted, one cloth or environment motion named |
| F3 melt | Faces in MS–CU, few background objects, one motion source per card, no orbit |
| F4 · F5 action, end state | One primary verb as body mechanics; every card states its end composition |
| F6 camera chaos | One named move with a magnitude per card, for Cue |
| F7 continuity break | kf-first = previous end state; inherited position, hand, prop, light and gaze stated first |
| F8 era leak | Nameable instances (materials, fixtures, period light), never "no modern objects" |
| F9 extras | "Exactly N people"; a near, occluding background behind faces |
| F10 anatomy | Hands countable or cropped; precise hand work becomes an insert, hand already in position |
| F11 text | No text or logos; screens dark or abstract; copy in TYPE |
| F12 light drift | Bible INVARIANT plus per-setup sentence; a visible practical; key side fixed in the room |
| F13 · F14 speed, physics | Durations from the action's real length; contact and impact on the cut; anticipation or aftermath frames |
| F15 lip sync | Mouth off-screen or on the listener; lines as VO |
| F16 style drift | Grade as mechanics (blacks, mids, skin, grain, palette roles); one lens family per scene; one session per scene |
| F17 framing | AR on the job; composition in frame terms with headroom (~10% at MS/MCU, near 0 at CU) |
| F19 object vanishes | Prop registered (colour, material, an edge condition), holder and hand, unoccluded, never exits and re-enters |

F18 (extend seams) is Cue's. Irreducibles are planned around at board time, never retried: precise hand work, a hand operating a branded product (product static, light moves, real pack composited), readable text, contact choreography, permanence through occlusion, reflections (shoot only the reflection, or break the surface), crowd faces (silhouettes, backs), exact counts (one, two, many). Rejects climb L1 prompt edit → L4 rebuilt frame → L5 re-plan (shorter, closer, split, substitute, off-screen) → L7 cut, flagged to the producer.

## Conflicts resolved

House style wins in every case.

| Conflict | Skill says | What I do (house way) | Ruling |
|---|---|---|---|
| Approval cadence | storyboard-creator: two panels, wait, scene by scene | Full spec list, then batches; Hawk and the producer gate, ≤2 auto-regenerations per shot | slate.md · shotbird §4 |
| Named DOP | sb-lighting-direction: don't target a living cinematographer's signature; nano-banana-pro: always name one | One named grade per film (role mandate), always translated into blacks, mids, skin and palette roles; the light comes only from the bible's sources, never "in the style of" | slate.md §2 · keyframe-prompting (October) |
| Prompt order | keyframe template: nine slots | The house eight-part paragraph, with the template's content rules: verbatim invariants, world-space light, pose with a next instant, negatives as instances | slate.md §2 |
| Camera-relative light | sb-lighting-direction bible writes "camera-left" | World-space INVARIANT plus per-setup sentence, so reverses can't flip the key | keyframe-template · continuity-bible |
| Identity length | continuity-bible: 30–50 words, one landmark | Hatch's lock verbatim, never trimmed; a lock without a checkable landmark is flagged to Hatch | slate.md §2 · character-consistency |
| Negative tail | keyframe template: ~6 classes chosen per frame | The house six bans always, plus the frame's risks as instances | slate.md §2 |
| 3D previs, techvis | sb-storyboard-previs: use when space or moves are the question | No installs: text plan view and boards; shots needing 3D flagged in the HANDOFF | crew contract |
| Light bans | nano-banana-pro: "no artificial light sources, no lens flares" | Motivated practicals with Kelvin are the core; ban rigs, beauty light, unmotivated flare | keyframe-prompting §2.5 |
| NBP location refs | image-models: NBP prefers described locations | Plate plus pasted block; if NBP misplaces the space, drop the plate on that shot and log it | character-consistency C |
| Model routing | image-models: NB2 faces, Soul Cinema stills | `gpt_image_2_5` default, `nano_banana_pro` for faces; 2.5 is unrated, so identity results go to memory | slate.md §2 |

Also settled at first preflight, unchanged: stills take mm, body and T-stop (FOV is Cue's); faces allowed in keyframes; palette only from `brand.json`; no names or @handles in image prompts; one paragraph, not JSON; AR and resolution on the job; "cinematic" only inside the preamble; hero props never readable; durations editorial, envelopes are hints for Cue.

## Update 2026-10-21. Overrides anything above
- Use the picker's image model and resolution (2K/4K; Seedream tops out at 2K).
- Add a proportions guard to every frame with a person, and use the full-body sheet panel as a reference on wides.
- {{NAME}}'s open change requests: make a new version applying exactly the change, then send it to Hawk.
- If Hawk says `SWITCH MODEL: a → b`, regenerate on b.
