---
name: sb-wan-3-prompting
description: "Shotbird crew skill (Cue): Wan 3.0 image-to-video prompting rules. Use inside Shotbird runs when Wan is the target engine."
---

> **Shotbird install note.** Installed for Abdullah's Shotbird crew from a pinned GitHub commit (see ATTRIBUTION.md). Only Markdown and data were installed: skip any step that runs a script, installs software, needs an API key, uploads media to third-party sites or writes to a local database. Abdullah's house rules (Obsidian vault playbooks and the agent's own instructions) take precedence over this skill.


# Wan 3.0 prompting

Researched against primary sources (Alibaba Model Studio official prompt guide, Runware
Wan 3.0 API docs, the Wan 3.0 prompt guide, and a provider OpenAPI schema read
directly). Background write-up with the full citation trail:
[`docs/wan-3-research.md`](../../docs/wan-3-research.md).

`[NV]` = not verified — confirm before relying on it.

---

## 1. The five rules that break scenes

Every illogical scene traces back to one of these. They are **documented behaviour**,
not bad luck.

1. **No state change inside a shot.** Alibaba is explicit: *"cuts happen BETWEEN clips,
   not within"*. An object that disappears, clothing that tears, lights that switch —
   each must become a **cut**. (Cost: two paid generations on a necklace that refused
   to leave a neck.)
2. **One action beat per shot.** *"Keep actions simple and short."* A 5s clip cannot do
   "sprints + vaults a planter + shoulders through a door". Two beats = two clips.
3. **Label speakers, never pronouns.** With two people on screen, "He says" makes the
   model guess. Use `[Man in the black tuxedo, firm]: "..."`.
4. **Address references by identifier.** The model binds `Image1` / `Image2` written in
   the prompt text to the uploaded reference array. Natural language ("the man from the
   first reference") is measurably weaker.
5. **Name the camera explicitly.** The default behaviour is a gentle drift. A locked
   frame requires the literal words `static, locked-off`.

Also documented as unreliable: **precise lip sync to specific words.** Ask for the
line, accept the approximation, or dub in post. Writing "precise lip sync" does not
buy it.

---

## 2. Prompt skeleton

Order matters more than sentence construction. Subject and setting first, then action,
then camera, then audio — Runware is explicit that this ordering "lands more
predictably".

```
Image1 is <one clause, no facial description>. Image2 is <one clause>.
<SETTING + LIGHTING, one sentence>.
<ONE action beat. Who does what, using Image1/Image2 as the subjects.>
Camera: <exactly one of: static locked-off | push-in | pull-back | pan | tilt |
         orbit | handheld tracking>.
[<Label>, <tone>]: "<line, accents intact>"
Audio. Foreground: <verb-driven event>. Bed: <verb-driven ambience>.
       Background: <verb-driven distant layer>.
Style: <lens>, photorealistic, <grade>, film grain.
```

Plus, as a **separate API field — never inside the prompt text**:

```
negative_prompt: low quality, blurry, distorted face, deformed hands, unnatural
movement, text, watermark, subtitles, shaky camera, duplicated people
```

Keep the negative prompt at **8–20 tokens**. Specific beats generic: "flicker,
exposure flicker, frame hopping" works; "stable video please" does not. Stacking 80
tags makes it impossible to know what fixed anything.

**The base formulas Alibaba publishes:**

| Case | Formula |
|---|---|
| Base | `Entity + Scene + Motion` |
| Advanced | `Entity(desc) + Scene(desc) + Motion(desc) + aesthetic control + stylization` |
| With sound | `… + sound description (voice / SFX / score)` |
| Multi-shot | `Overall description + shot number + timestamp + shot content` |
| **Image-to-video** | **`Motion + camera move` only** — the image already carries entity, scene and style |

In image-to-video, describing what is already in the image is wasted; describing what
is *not* in it produces hallucination or is ignored.

---

## 3. Identity with real people

Say as little as possible about the face. Descriptive text about eyes, hair or jaw
pulls the render toward a generic average and **fights** the reference photo.

- **Restate wardrobe in every shot** (the generator never sees the other shots).
- **Never restate faces.**
- **Body fidelity, one short line per shot:**
  `Keep natural, realistic body proportions. Do not slim or idealize.`
  The negative-only form ("do NOT slim") was ignored on its own; an affirmative
  physical description over-corrected. This short line plus good references is the
  balance that held.

---

## 4. Audio: three named layers, written as verbs

The docs require each layer to be its own directive, in order of prominence, and to use
**verbs for sound events, not nouns or adjectives**.

Not `"wind, cables humming, held breath"`. Write the event happening:

```
Audio. Foreground: the mask tearing free with a sharp rip of fabric.
      Bed: cables groaning under load.
      Background: the city humming far below.
```

Audio is generated natively on the Wan 3.0 family — always direct it.

---

## 5. Camera — the six moves that respond by name

`static / locked-off` · `dolly / push-in` · `pull-back` · `pan / tilt` · `orbit` ·
`handheld tracking`

Never combine contradictory terms — "drone shot zooming into close-up" confuses the
model; pick one perspective. Emotional intent per move, per Alibaba: push-in = intimacy
or tension · pull-out = scale or isolation · tracking = puts the viewer alongside ·
orbit = emphasises importance · locked = stillness and focus.

---

## 6. API surface that actually exists

Read from a provider OpenAPI schema and live model list. Exact field names vary by
provider; the *capabilities* are the point.

| Field | Reality |
|---|---|
| `duration` | **2s to 30s** — not just 5s. Match duration to beat count (~5–8s per beat) |
| `resolution` | 480p / 720p / 1080p. **No 4K**, despite marketing |
| `aspect_ratio` | adaptive, 16:9, 9:16, 1:1, 4:3, 3:4 |
| `prompt` | up to **20,000 characters** — length was never the constraint |
| `negative_prompt` | supported, and routinely forgotten |
| `reference_image_urls` | data URLs accepted; **short side ≥ 240 px**; up to 5 references, each identity controlled independently |
| `audio` | generated natively; audio *input* is false on this model (no voice cloning) |
| **no `seed`** | **no reproducibility on the video route** — a re-run is a new roll |
| `keyframes` | present in some schemas but **not supported by this model** — it belongs to keyframe-driven models |
| `elements` / `@Element1` | a different model family (Kling), not Wan |
| `creativity` / `realism` / `sharp` / `noise` | marked *"enhancement models only"* — inert here |

**Prompt-extend is the most dangerous silent default** `[NV]` on any given route:
Wan's own tooling ships it **on**, and it rewrites your prompt before generation, which
quietly destroys timecoded shot control. If timecoded shots come back ignored, suspect
this first.

---

## 7. AI Director Mode — several shots in one generation

Because duration reaches 30s, 4–6 shots can render in a single pass with the model
handling transitions and cross-shot identity itself. This is usually **better
continuity than stitching separate 5s generations**.

```
Overall: Image1 and Image2, <wardrobe>. <Grade>. Character consistency across all shots.
Shot 1 [0-6s]:   <shot type> - <content, under 20 words>
Shot 2 [6-12s]:  <shot type> - <content, under 20 words>
Shot 3 [12-18s]: <shot type> - <content, under 20 words>
Audio: <three layers>. Style: <lens, grade, grain>.
```

Rules: 4–6 shots max · each shot description **under 20 words** · the character
reference declared **once** in the Overall line, never repeated per shot (Identity Lock
handles the rest).

---

## 8. The fixing pass — run this on any draft script

1. **Beat count.** Count action beats per shot. More than one → split the shot.
2. **State changes.** Anything appearing/disappearing, clothing changing, light
   switching → split into a before-shot and an after-shot. The cut sells the change.
3. **Pronouns.** Replace every "he/she says" with a labelled speaker plus tone.
4. **References.** Rewrite subjects as `Image1` / `Image2`.
5. **Camera.** Exactly one named move per shot; write `static, locked-off` where the
   frame should hold. Never combine contradictory moves.
6. **Audio.** Rewrite noun lists into three verb-driven layers.
7. **Wardrobe.** Restate in every shot. Faces: never.
8. **Duration.** Match to beats (~5–8s each) instead of defaulting to 5s.
9. **Negative prompt.** Attach it to every generation.
10. **Continuity.** Run [`skills/multiclip-continuity`](../multiclip-continuity/SKILL.md)
    — props, wardrobe progression, cast, knowledge, audio bridges, setup/payoff — then
    produce the regeneration ledger.

---

## 9. Operational rules for paid API routes

- **Log the job id the instant a job is queued**, to a file. On most routes it is the
  only handle on a **paid** job, and some providers have no list endpoint — a killed
  script buries the id in an unflushed buffer and the money is gone.
- **Quote before you generate** where the provider offers it.
- Retrieval may return **raw MP4 bytes rather than a URL** — branch on `Content-Type`,
  do not look for a URL field. A working implementation is in
  [`reference/venice_video_provider.py`](../../reference/venice_video_provider.py).
