---
name: sb-director-styles
description: "Shotbird crew skill (Cue and the prompt studio): write video prompts to {{NAME}}'s direction, from text alone or from reference videos he attaches. Decodes technical direction (angle, lens, move, speed, blocking, light, timing, transitions) and 'in the style of <director>' asks into concrete Seedance 2.5 prompt language, for live action (22 director profiles) and for anime films (16 director and studio styles, production vocabulary, look recipes). SFX only, never music. Use inside Shotbird runs whenever a prompt carries a direction, a director reference or an anime look."
---

# Director styles: prompts written to direction

Cue's job with this skill is to turn what {{NAME}} says as a director into a video prompt that renders it. He directs; you translate. You never soften, average or "improve" a direction he gave.

**Three standing rules**
1. **Their direction is law.** An explicit technical instruction (angle, lens, move, speed, timing, light, blocking) overrides the shot list, the bible, a director style and your own taste. If two of their instructions conflict, or one can't be reached from the approved start frame, say so in the HANDOFF and write the closest reachable version. Never drop one silently.
2. **Names never go into a prompt.** A director, studio, film or series name is input to you only. Video models ignore or block names, and a name copies nothing reliably. Write the technique: lens, move, blocking, light, colour, rhythm, sound. This also keeps every prompt original work.
3. **Audio is SFX only.** NO music, NO score, NO BGM, NO song, in every prompt, in every style. A director known for needle-drops or a famous score still gets diegetic sound effects only. Dialogue only when the script has lines.

## Where the prompt starts from (changed 2026-11-25)

{{NAME}}'s video prompts are **text-to-video by default: no start image.** He defines the shot in words, and often attaches reference videos to show what he is after.
- **Text only.** Nothing anchors the picture, so the prompt must state everything: who (age, build, face, hair, wardrobe, in a reusable character block repeated word for word in every shot of the same piece), where, when, the light, the action, the camera, the look, the sound and the end state. Don't leave an axis to chance; fill what he didn't say with the most ordinary choice that fits, and list those assumptions.
- **Reference video.** Analyse it first with `references/reference-video-analysis.md`, then carry its craft (camera, pacing, transitions, look) into their subject. Never its content.
- **Image-to-video** only when he says a frame is the start image. Then the frame fixes lens, angle, light and palette, and step 4 below applies.
- **One request, one prompt. Never scene by scene.** He does not want a prompt per scene or per shot of a film. Write only what he asked for, as a single prompt; a sequence of several shots stays inside that one prompt as labelled, timecoded shots with a transition line at each join. Split only if he asks or it can't fit one generation (4–30 s on Seedance 2.5).
- **Transitions** between shots: `references/transitions.md`. Inside one prompt, one transition line per join; across a split, write it on both sides.
- Seedance 2.5's own guidance for the three modes is in `~/.claude/skills/sb-video-prompting/references/models/seedance2-5/prompting.md` ("Apply mode-specific guidance").

## Workflow

1. **Collect the direction.** Sources, strongest first: a `DIRECTION for S##…` message (the board's Direct button, or their chat words) → `decisions.md` → the bible's director's book → the shot list. Quote their words in the prompt's board `notes` so he can see what you acted on.
2. **Split it into the nine axes** (table below). Mark each axis as *directed* (he said it), *styled* (comes from a named director or look) or *free* (yours, taken from the frame and the bible).
3. **Resolve references.** For "like <director>" open that director's entry (`references/directors-live-action.md` or `references/directors-anime.md`) and take its *Prompt translation* lines for the axes that are still free. A directed axis always beats a styled one.
4. **Check reach (image-to-video only).** The start frame is fixed: it already has a lens feel, an angle, a light and a palette. A direction that contradicts the frame (a low angle asked on an eye-level frame, night on a day frame) needs a new frame, not a prompt. Say so and write what the frame can honestly do: a move *towards* that angle, a light *shift* inside the shot. Never promise it in the prompt and hope.
5. **Write on the spine.** Use `cinema-director-v3`'s slots and the Seedance 2.5 template from your skill card. Direction lands in: Lens (FOV in degrees), Camera, Geometry Map, Action Timing (timecoded, beats ≥ 3 s on 2.5), Acting, Light and Colour Doctrine, Atmosphere, Audio.
6. **Self-check before `$SB prompt`:** every directed axis appears literally and measurably in the prompt; no name of a person, studio or title; one main camera move per segment; the audio line is SFX-only with the NO-music clause; for anime, the 2D lock block is present.

## Fitting the rest of your rules

- **`cinema-director-v3` stays the spine.** Where it and this skill disagree: v3's FOV ladder is the only lens table; v3's no-drone, no-tone-bed rule stands (a "low rumble" from a director profile is written only as the sound of something visible: wind, an engine, a train, surf); this skill's ban on names beats v3's named-DP shorthand.
- **Anime swaps four v3 slots:** Style Prefix (the 2D lock block replaces the photoreal prefix), Technical (drawn timing replaces camera-sensor language), the skin-protection lock (becomes the on-model lock), and the render-quality line (becomes line, colour and shadow-tone constancy). Every other slot stays.
- **Two beats in a short shot.** Seedance 2.5 wants ≥ 3 s per beat. If he directs two beats in a 4–5 s shot, generate 6 s at the same beat ratio and note the trim; if the cut can't take a trim, merge them into one continuous action and say so.
- **"Slow" in numbers.** Size the move to the shot, not to a fixed speed: "very slow" = the framing changes by about one shot size over the whole shot; "slow" = one size in about half the shot; "fast" = one size in under a second. Then state the m/s or °/s that gives.
- **Their direction against Hawk's composition watch** (for example "crown at the top edge: lock the camera"). Their direction wins. Write it, and add the risk and a safer alternative to the notes line.
- **Wrong word, clear intent.** "Pan up" is a tilt, "zoom in" on a walking shot is usually a push-in. Write what he means and say in the notes which word you read how.
- **A move past the edge of a still.** A tilt or pan needs picture beyond the frame. Smooth areas (sky, wall, sea) extend safely; detailed ones (faces, crowds, signage) don't. Flag it, and suggest a taller or wider start frame when the move is long.
- **Ambiguous acting notes** ("looks past the lens"): pick the reading the frame supports, state the eyeline target and side, and note it.
- **Worked examples:** `references/worked-examples.md` has one live-action and one anime prompt written from this skill, with their notes lines.

## The nine axes (what a direction can fix)

| Axis | He says | You write |
|---|---|---|
| Shot size | "wide", "cowboy", "ECU on the eyes" | The size plus what the frame edges cut: "medium close-up, frame from mid-chest to just above the hair" |
| Angle and height | "low angle", "dutch", "top shot", "worm's eye" | Camera height in metres or body landmarks, tilt in degrees, roll in degrees: "camera at knee height, tilted up 25°, horizon level" |
| Lens | "24", "long lens", "anamorphic", "fisheye" | FOV in degrees with the mm equivalent, depth of field, distortion and bokeh behaviour |
| Move | "push in", "orbit", "crane up", "whip", "oner" | One move: type, direction, speed (m/s or °/s), start and end framing, easing |
| Support | "handheld", "Steadicam", "sticks", "drone" | The shake signature: "locked-off on a tripod, zero drift" / "handheld, small 1–2 cm breathing sway, no jolts" |
| Blocking | "she crosses left to right", "he turns on the line" | Screen direction, distances, marks, who moves when, eyeline target |
| Light | "hard side light", "silhouette", "golden hour", "practicals only" | Source, direction (clock position), quality, Kelvin, contrast ratio, what it does over time |
| Rhythm | "let it breathe", "snappier", "slow-mo", "speed ramp" | Timecoded beats, holds in seconds, frame-rate language ("shot at 96 fps, played at 24") |
| Sound | "dead silent", "hear the rain", "big impact" | Timecoded SFX only, with perspective (close, distant, muffled) |

The full vocabulary, the mm ↔ FOV table, move speeds, and the "vague note → concrete change" table are in `references/direction-decoder.md`. Read it at the start of any directed job.

## Director quick index (live action)

One line each, already in prompt terms. Full 12-field entries: `references/directors-live-action.md`.

| Ask | Core translation |
|---|---|
| Kubrick | One-point symmetry, 18–25mm wide, dead-centre subject, slow reverse or forward track down the axis, practical light, cold stillness |
| Villeneuve | Huge scale against a small figure, slow deliberate moves, soft sourcey light through haze, desaturated earth and amber, long holds, low rumble and wind |
| Nolan | Large-format clarity, handheld-on-the-shoulder close work, practical in-camera scale, cool steel and warm tungsten, ticking and mechanical foley |
| Fincher | Locked or motion-controlled camera that moves only with the subject, low-key top light, sickly green-yellow or steel palette, zero handheld, precise |
| Wes Anderson | Flat planimetric frontal framing, perfect symmetry, 40mm anamorphic feel, 90° whip pans and lateral dollies, pastel palette, deadpan stillness |
| Wong Kar-wai | Step-printed smeared motion, 22 fps-feel undercranking, saturated neon reds and greens, handheld close and obstructed frames, rain, cigarette smoke |
| Tarantino | Low-angle hero frames, slow push-ins on faces, crash zooms, long dialogue holds, saturated primaries, loud tactile foley |
| Scorsese | Energetic Steadicam follow, fast push-ins, whip pans, sudden slow motion on a look, warm tungsten interiors |
| Spielberg | Blocking-driven oners that reframe wide → close, awe-struck push-in on an upturned face, strong backlight and shafts, visible beams in haze |
| Kurosawa | Telephoto compression, weather as motion (rain, wind, dust, fog), geometric group blocking, movement in every layer, axial cuts |
| Tarkovsky | Very long takes, imperceptible drift, water, wind in grass, muted earth tones, time felt passing, dripping and distant sounds |
| Ridley Scott | Layered smoke and shafts, backlit silhouettes, multiple long lenses, dense textured atmosphere, blue-teal night against amber practicals |
| P. T. Anderson | Long fluid tracking shots, sudden push-ins, anamorphic flares, warm filmic colour, restless camera around steady actors |
| Cuarón / Lubezki | Continuous wide-angle long take close to the actor, camera as participant, natural light, 18–21mm, immersive ambient sound |
| Malick | Magic-hour backlight, floating wide-angle Steadicam at body height, hands in wheat, glances away from camera, wind and insects |
| Bong Joon-ho | Precise storyboarded frames, vertical staging (stairs, levels), smooth lateral tracks, tonal turn inside the shot, rain |
| Park Chan-wook | Ornate symmetrical design, baroque camera moves and match transitions, rich jewel tones, controlled violence |
| Edgar Wright | Snap inserts, whip pans, crash zooms, action timed to hard sound effects, kinetic comedy rhythm |
| Zack Snyder | Speed-ramped slow motion, desaturated high-contrast with crushed blacks, painterly hero poses, shallow depth |
| Michael Bay | Low-angle 360° hero orbit, sunset backlight, lens flares, saturated teal and orange, constant motion, debris and sparks |
| Spike Jonze | Naturalistic handheld warmth, soft daylight, intimate close-ups, one surreal element played straight |
| Lubezki natural light | Wide lens very close to faces, only sun, sky and fire as sources, backlit at magic hour, long unbroken moves |

## Blending two styles

Take each axis from **one** source only. Safe splits: lens and composition from A, colour and light from B; or camera from A, rhythm from B. Never average a single axis (a "symmetrical handheld" or a "pastel neon" renders as mud). Say in the notes which axis came from where. If he names three or more, ask them to rank them, and until he does use the first for camera and lens and the second for light and colour.

## Anime mode

Use it when the project is an anime film: the brief or `decisions.md` says anime, or the approved start frames are 2D animation. Read `references/anime-production.md` before the first anime prompt of a project, and `references/directors-anime.md` when a director or studio style is named.

**What changes from live action**
- **Open with a 2D lock block** (first lines of the prompt, and again in the Locks chain): `2D hand-drawn anime, cel-shaded flat colour with <one|two> shadow tone(s), clean <thin|variable> linework exactly as in the start frame. NOT 3D, NOT CGI render, NOT photoreal, NOT semi-real shading. Line weight, palette and character model stay identical to the start frame in every frame.`
- **Camera is layout, not a rig.** A flat drawing cannot be dollied. Write pans across the artwork, tilt along a tall background, slow truck-in on the cel, and **parallax of separated layers** (foreground, character, mid, sky) for depth. Use real 3D camera travel only when the look is a 2D/3DCG hybrid and say so.
- **Timing is drawn.** Say how it is animated: "animated on twos: each drawing held for two frames, crisp pose-to-pose, no motion interpolation, no smooth tweening", with held poses, anticipation, snap and settle. Name smears and impact frames when the style has them; ban them when it doesn't.
- **Limited animation is a feature.** Held cel with only hair, cloth, eyes or mouth moving; background pan under a still character; mouth flaps on three shapes. Fewer moving parts also means fewer melted frames.
- **Compositing (satsuei) carries the light:** bloom, light wrap, gradient gels, dust particles, depth blur on layers, film grain. State how much, or state none.
- **Effects are drawn shapes:** smoke, water, fire, debris and speed lines as hand-drawn FX animation, not simulated particles.
- **Acting:** eyes, blinks, hair and small gestures do the work. Keep faces on-model: "no off-model drawings, facial features keep their exact shapes and spacing".
- **Audio:** the same rule. SFX only: footsteps, cloth, wind, cicadas, trains, impacts, room tone. NO music, NO opening or insert song, NO voice unless scripted.
- **Negative list adds:** `3D render, CGI, photorealism, live action, realistic skin, volumetric realistic lighting, motion interpolation, morphing lines, line boil, off-model face, extra fingers, music, score, BGM, song`.

**Anime quick index** (full entries in `references/directors-anime.md`)

| Ask | Core translation |
|---|---|
| Miyazaki | Hand-painted gouache backgrounds, thin uniform outlines, weighty full-body motion, wind in grass and cloth, towering cumulus, quiet pauses |
| Takahata | Observational everyday acting, sketch and watercolour with paper showing, mostly static camera |
| Satoshi Kon | Realist character design, match-cut transitions, wide-angle interiors, reality slipping inside the shot |
| Shinkai | Photoreal painted backgrounds, heavy bloom and lens flare, saturated twilight skies, light shafts, rain, long holds on scenery |
| Hosoda | Flat shadowless characters, clean thin lines, lateral tracking, summer clouds |
| Otomo | Dense mechanical and city detail, full animation on ones, light trails, debris and smoke FX |
| Oshii | Still contemplative layouts, fisheye and reflections, cold blue-green, rain, long silences |
| Anno | Static graphic layouts, extreme high and low angles, long held cels, power lines, hard cuts, cicadas |
| Watanabe | Cinematic widescreen staging, naturalistic action, cool stylish framing |
| Yuasa | Loose elastic shapes, wild perspective, flat bold colour, morphing motion |
| Yamada | Long-lens inserts of legs and hands, shallow focus, soft pastel light, tiny gestures |
| Ikuhara | Theatrical symmetry, repeated staged motifs, graphic colour blocks |
| Araki | Sweeping 3D-assisted camera through action, heavy rim light and gradients, dramatic low angles |
| Imaishi | Angular poses, hard smears, limited frames at full energy, bold flat colour, flashes |
| Nakamura-style action | Camera orbits a clash, impact frames, debris cubes, timing that snaps from holds to ones |
| Ufotable-style compositing | Digital FX layered on 2D, glowing particles, depth blur, 3D camera through painted sets |

## Output additions

Keep the usual Cue outputs, and add to each directed prompt's board `notes`:
`Direction: "<their words>" · directed: <axes> · styled: <source → axes> · free: <axes> · unreachable from this frame: <none | what and why>`

## References
- `references/direction-decoder.md` — technical vocabulary, mm ↔ FOV, move speeds, vague note → concrete change.
- `references/worked-examples.md` — two finished directed prompts (live action and anime).
- `references/transitions.md` — cuts, camera-made, optical and anime transitions, and how to write a join.
- `references/reference-video-analysis.md` — reading a reference video: frames, shots, axes, transitions, rhythm.
- `references/directors-live-action.md` — 22 live-action profiles, blend rules, 25 director-speak notes decoded.
- `references/directors-anime.md` — 16 anime director and studio styles.
- `references/anime-production.md` — production vocabulary, ten look recipes, Seedance failure modes for 2D, 20 anime notes decoded, sources.

Researched 2026-11-25. Lens and format facts were checked against published interviews and cinematography sources; anything marked "(unverified)" in a reference is a critical reading, not a sourced fact.
