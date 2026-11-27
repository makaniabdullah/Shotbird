# Direction decoder

How to turn director's shorthand into measurable prompt language. Every row gives the phrase to write. Numbers are defaults: when {{NAME}} gives a number, their number wins.

## Shot sizes (say what the frame edges cut)

| Term | Also called | Write |
|---|---|---|
| ELS / extreme wide | vista, establishing | Figure under one-tenth of frame height; the place is the subject |
| WS / wide / full | long shot | Whole body with headroom and floor visible |
| Cowboy | American shot | Mid-thigh to above the head |
| MS / medium | waist shot | Waist to above the head |
| MCU | bust shot | Mid-chest to just above the hair |
| CU | close-up | Chin to hairline, face fills the frame |
| ECU | extreme close-up, macro | One feature only: the eyes, a hand, the lips, a product detail |
| Insert | detail | An object or hand action, no face |
| OTS | over the shoulder | Foreground shoulder and head soft on one side, subject sharp beyond |
| Two-shot / three-shot | — | Both figures in frame, name who is left and right |
| POV | subjective | Camera at the character's eye position, hands may enter from the bottom of frame |
| Single, clean / dirty | — | Clean: nobody else in frame. Dirty: a soft foreground sliver of the other person |

## Angle, height, roll

| Term | Write |
|---|---|
| Eye level | Camera at the subject's eye height, lens axis horizontal |
| Low angle | Camera below the chest, tilted up 15–35°; subject towers |
| Worm's eye / ground level | Camera on the floor, tilted up 45–80° |
| Hip level / knee level | Name the body landmark as the height |
| High angle | Camera above the head, tilted down 20–45°; subject diminished |
| Top shot / overhead / bird's eye / God's eye | Camera directly above, lens pointing straight down 90° |
| Dutch / canted | Horizon rolled 10–25°, say which way |
| Profile | Camera 90° to the face |
| Three-quarter | Camera 45° to the face |
| Frontal / planimetric | Camera square to a flat background, subject facing lens |
| Back shot / follow | Camera behind the subject, on their line of travel |
| Shoulder level | Camera at shoulder height, slightly below the eyes |

Give angle as three numbers when it matters: **height** (metres or landmark), **tilt** (degrees up or down), **roll** (degrees).

## Lens: mm ↔ field of view

**One table only: `cinema-director-v3`'s FOV ladder.** Write the FOV from it, with their mm in brackets. Copied here so you don't have to look it up:

| FOV | mm | Feel |
|---|---|---|
| 107° | 14–16 | Ultra-wide, architectural, strong stretch at the edges |
| 84° | 20–24 | Classic wide, full-body blocking, immersive |
| 63° | 28–35 | Reportage wide, walking alongside |
| 47° | 40–50 | Eye-level neutral |
| 34° | 60–70 | Short tele, stacked planes |
| 29° | 75–85 | Portrait compression |
| 18° | 100–135 | Tight portrait, held close-up |

Outside the ladder: 12mm and wider → "ultra-wide, about 115°"; 200mm → "about 10°, strong compression, background looms"; 400mm → "about 5°, heat shimmer". If v3's ladder changes, v3 wins.

Lens words and what to write:
- **Anamorphic:** oval bokeh, horizontal blue streak flares, slight barrel curve at the edges, 2.39:1 feel.
- **Spherical, clean:** round bokeh, no streaks, straight lines stay straight.
- **Fisheye:** 150–180° view, heavy barrel curve, horizon bends.
- **Shallow focus / wide open:** "razor-thin depth of field, only the near eye sharp, background dissolved".
- **Deep focus / stopped down:** "everything sharp from 1 m to infinity".
- **Rack focus:** "focus pulls from <A> to <B> between 0:02 and 0:03, smooth".
- **Split diopter:** "near object and far figure both sharp, a soft vertical seam between them".
- **Tilt-shift:** "a narrow horizontal band in focus, miniature feel".
- **Vintage glass:** "low contrast, veiling glare, soft halation around highlights".
- **Macro:** "1:1 magnification, a few millimetres in focus".
- **Zoom vs dolly:** a zoom changes FOV with no parallax; a dolly changes position and layers slide. Say which.
- **Dolly zoom / Vertigo:** "camera tracks back while the lens zooms in, subject size constant, background stretches away" (state the FOV start and end).

## Camera moves (one per segment; give speed and endpoint)

| Term | Write | Typical speed |
|---|---|---|
| Locked-off / static / sticks | "camera locked on a tripod, zero movement, zero drift" | — |
| Push-in / dolly in | "camera tracks straight forward, MS to MCU" | slow 0.1–0.2 m/s; fast 0.6+ |
| Pull-out / dolly out | "tracks straight back, revealing …" | same |
| Creep | "almost imperceptible forward drift, about 5% tighter over the shot" | 0.03–0.05 m/s |
| Track / truck / crab | "camera travels sideways, left to right, parallel to the subject" | walk 1.2–1.5 m/s |
| Follow / lead | "camera behind (or ahead of) the subject at a fixed 1.5 m" | matches subject |
| Pan | "camera rotates left to right on its axis" | slow 10°/s; whip 300°+/s with streaked blur |
| Tilt | "camera rotates up (or down)" | slow 8°/s |
| Whip pan / swish | "one hard pan, full motion-blur streak, lands locked" | under 0.3 s |
| Crash zoom / snap zoom | "sudden zoom from wide to close in 0.3 s, no camera travel" | — |
| Slow zoom | "lens slowly zooms in, no parallax" | 10–15% over the shot |
| Pedestal / boom up, down | "camera rises (or lowers) vertically, lens angle unchanged" | 0.2 m/s |
| Crane / jib | "camera rises and arcs, ending high and wide" | 0.5 m/s |
| Orbit / arc | "camera circles the subject clockwise, 90° of arc, subject stays centred" | 15–30°/s; hero orbit 60°/s |
| Roll / barrel | "camera rotates around the lens axis, 90° clockwise" | — |
| Handheld | "handheld, light 1–2 cm sway with breathing, no jolts" (calm) / "urgent handheld, jittery reframing" (action) | — |
| Steadicam / gimbal | "floating stabilised glide, no bounce" | walk speed |
| Snorricam | "camera rigged to the actor's body, face fixed in frame, world lurches behind" | — |
| Drone / aerial | "aerial, forward flight at 30 m, slow descent" | 5–10 m/s |
| FPV | "fast low dive, banking turns, wide lens" | 15+ m/s |
| Oner / long take | "single continuous shot, no cuts", then describe the path in order | — |
| Reveal | "camera clears a foreground edge to uncover …" | — |
| Parallax slide | "small sideways drift, foreground crosses frame faster than background" | 0.1 m/s |
| Bullet time | "action frozen or near-frozen while the camera arcs" | — |
| Rack + push | Avoid on i2v: two changes at once morph. Split into two beats. | — |

Easing: say "eases in over the first second, eases out to a stop" or "constant speed". A move with no stated end drifts.

## Blocking and staging
- **Screen direction:** left-to-right or right-to-left, and keep it across shots (180° rule).
- **Marks:** "starts 3 m from camera at frame left, stops at 1.2 m, frame centre".
- **Depth staging:** foreground, mid, background, and who is on which plane.
- **Eyeline:** where the eyes go and when ("looks past the lens to frame right at 0:03").
- **Cross / counter:** who passes in front of whom.
- **Entrance / exit:** which frame edge.
- **Business:** the hand action that fills a beat (pours, buttons a cuff).
- **Turn-in / reveal of face:** "turns over the left shoulder, face reaches three-quarter at 0:04".

## Light
| Term | Write |
|---|---|
| Key / fill / rim (back) | Source, clock position around the subject, height, quality |
| Hard light | "small hard source, crisp shadow edges" |
| Soft light | "large soft source, gradual falloff, no hard edges" |
| High key | "bright, low contrast, shadows filled, ratio about 2:1" |
| Low key | "mostly shadow, single key, ratio 8:1 or higher" |
| Rembrandt | "key 45° to the side and above, a small triangle of light on the shadow cheek" |
| Split | "key at 90°, half the face in shadow" |
| Butterfly / beauty | "key above the lens axis, small shadow under the nose" (ban it when the house look is natural) |
| Silhouette | "subject unlit against a bright background, pure black shape" |
| Motivated / practicals | "light only from the lamp, window, screen, fire in frame" |
| Chiaroscuro | "deep pools of black, one shaft of light" |
| Magic hour / golden | "sun 5° above the horizon, 3200–3800 K, long shadows, backlit" |
| Blue hour | "sun below the horizon, 8000–10000 K ambient, practicals glowing warm" |
| Overcast | "soft shadowless daylight, 6500 K" |
| Tungsten | 3200 K. **Daylight** 5600 K. **Candle / fire** 1900 K. **Moonlight (film)** blue-cyan 4100 K graded cool |
| Negative fill | "black on the shadow side, contrast deepened" |
| God rays / shafts | "visible beams through haze from <source>" |
| Flare | "sun or lamp just inside frame edge, veiling flare" |
| Change in shot | Say what changes and when: "cloud shadow crosses at 0:03", "neon flickers twice" |

## Time and rhythm
- **Slow motion:** "shot at 96 fps, played at 24: 4× slow motion" (48 = 2×, 120 = 5×).
- **Speed ramp:** "real time until 0:02, ramps to 4× slow motion through the impact, back to real time at 0:04".
- **Undercrank / step-printing:** "low frame-rate smear, streaked staccato motion".
- **Shutter:** 180° normal blur; 45° crisp staccato (combat look); 360° long smeary blur.
- **Hold:** name seconds of stillness. Stillness is a direction, not empty time.
- **Beat:** on Seedance 2.5 one beat needs ≥ 3 s. Two beats in a 5 s shot is the practical ceiling.
- **Freeze / time-lapse / reverse:** say it plainly and when.

## Vague note → concrete change

| He says | Change |
|---|---|
| More tension | Tighter size, slower push-in, lower key, longer hold before the action, room tone drops out |
| More epic | Wider lens, subject smaller in frame, low angle, slow crane or pull-out, haze and shafts, low rumble |
| More intimate | 65–85mm close, shallow focus, eye level, handheld breathing, close-perspective sound |
| Dreamlike | Slow motion, soft halation, backlight, floating glide, muffled sound |
| Gritty | Handheld, harder light, grain, desaturated, loud dry foley |
| More dynamic | Add one move with a clear end, foreground crossing, faster subject action; never two moves at once |
| Let it breathe | Add 1–2 s hold at head and tail, remove a beat |
| Snappier | Cut a beat, start on motion, end on the action's peak |
| Hero moment | Low angle, slow push-in or orbit, rim light, slow-motion, wind in hair and cloth |
| More cinematic | Wider aspect feel, shallow focus, motivated side light, haze depth, slow deliberate move |
| More natural | Eye level, 35–50mm, available light, small imperfect handheld, ordinary gestures |
| More premium | Slow controlled move, soft large source, clean highlights, restrained palette, precise timing |
| Colder / lonelier | Wider, subject off-centre and small, cool Kelvin, static camera, wind |
| Warmer | Lower Kelvin practicals, closer, softer light, small smile or exhale |
| More energy | Shorter beats, whip or snap zoom entry, faster subject motion, hard SFX hits |
| More mystery | Backlight, silhouette, obstructed foreground, slow reveal, sparse sound |
| More real / less AI | Fewer moving parts, real-world physics cues (weight, cloth, breath), no beauty light, skin texture, grain |
| Scarier | Low angle or too-high angle, wide lens close, long static hold, sound drops to near silence |
| Funnier | Flat frontal frame, deadpan stillness, snap zoom or whip to the reaction, hard foley on the gag |
| Bigger impact | Anticipation hold, one fast action, camera shake of 2–3 frames, debris, a single heavy low-end SFX hit |
| Smoother | Remove handheld, constant-speed move with eased ends, fewer beats |
| More depth | Foreground element, haze between planes, sideways parallax, backlight separation |
| Product hero | Macro or 85–100mm, slow orbit or push-in, hard rim plus soft key, controlled reflections, tactile SFX |
| More emotional | Slow push to the eyes, hold after the line or look, micro-expression, breath audible |
| Make it pop | Stronger subject-background separation, a saturated accent against a muted field, a clean rim |
