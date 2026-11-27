# Anime production: vocabulary, looks, Seedance behaviour

Companion to `directors-anime.md`. Names of people, studios and titles are for your understanding only; never write them in a prompt. Sound is effects only, never music.

---

# Part B. Production vocabulary and how to phrase it

Definitions are standard industry usage. Only impact frames, sakuga, layouts, Itano circus, postcard memories, kagenashi and satsuei were checked against a source in this pass; treat the rest as (unverified) here.

- **Key animation vs in-betweens:** Keys are the main poses; in-betweens fill the gaps. Prompt: "strong, clear key poses with few drawings in between" (snappy) or "smooth, fully in-betweened motion" (fluid).
- **Ones / twos / threes:** A new drawing every 1, 2 or 3 frames at 24 fps (24, 12 or 8 drawings a second). Prompt: "character animation on twos: the drawing changes 12 times a second and each drawing is held, stepped motion with no blending between drawings and no motion blur, while the camera and background move smoothly."
- **Smear frames:** One stretched or multiplied drawing standing in for motion blur. Prompt: "the arm stretches into a single elongated smear drawing for one frame."
- **Impact frames:** One to three stylised, often monochrome or inverted frames at the moment of a hit. Prompt: "at contact, two frames flash to rough black-and-white, then normal colour returns."
- **Sakuga:** Fan term for standout, high-effort animation. Models read it loosely. Say what it means: "fluid, detailed, hand-drawn action with varied timing."
- **Obake:** Ghost-like multiple or blurred drawings of a fast-moving part. Prompt: "the sword leaves hand-drawn afterimage shapes along its arc."
- **Held cel / kuchi-paku:** A still drawing where only the mouth flaps (usually three shapes: closed, half, open). Prompt: "the character holds still; only the mouth opens and closes in simple shapes, with one blink."
- **Pan cel:** A long drawing or background slid past the camera. Prompt: "the background slides right to left at a constant speed behind the held character."
- **Multiplane parallax:** Flat layers moving at different speeds to suggest depth. Prompt: "foreground, character and background are separate flat layers; the foreground slides faster than the background."
- **Harmony cel:** A character or object painted in the detailed style of a background, used for a held, illustrated moment. Prompt: "the frame freezes into a richly painted illustration with textured brushwork."
- **Postcard memory (Dezaki):** A dramatic freeze that turns into a pastel or painted still. Prompt: "the action freezes and the image becomes a pastel-chalk illustration, held, with a slow push-in."
- **Background animation:** The background itself is redrawn frame by frame so the space moves in perspective. Prompt: "the ground and walls are hand-drawn and rush past in perspective as the camera flies forward."
- **Speed lines:** Drawn streaks for speed or focus. Prompt: "radial speed lines converge on the character" or "horizontal streak lines replace the background."
- **Itano circus:** Swarms of missiles on twisting smoke trails around a dodging craft, with an acrobatic camera. Prompt: "dozens of missiles on curling white smoke trails weave around the craft as the camera banks with it."
- **Kanada-style poses and flares:** Angular, off-balance poses with snappy timing, and geometric light flares. Prompt: "sharp angular poses that snap into place, geometric cross-shaped light flares."
- **Satsuei (photography / compositing):** The stage that merges cels, backgrounds and effects and adds light, blur and grain. Prompt it as a separate sentence: "compositing: soft bloom, rim light, floating dust, light film grain."
- **Cel shading vs soft shading:** Hard-edged one or two shadow tones versus airbrushed gradients. Prompt: "flat colour with one hard-edged shadow tone" or "soft gradient shading on hair and cheeks." Kagenashi is "no shadow tone at all."
- **Line weight:** Thickness and variation of outlines. Always state it: "thin uniform dark-brown outlines" or "thick, tapered black outlines."
- **2D / 3DCG hybrid:** Drawn characters with CG vehicles, crowds or sets. Prompt: "hand-drawn 2D characters; the vehicle is toon-shaded 3D with matching outlines."
- **Rotoscope look:** Motion traced from live action: realistic, slightly wobbly lines. Prompt: "realistic traced movement with slightly shifting outlines and minimal facial detail."
- **Chibi / SD cutaway:** Brief switch to small, big-headed simplified characters for a gag. Prompt: "simplified two-heads-tall version of the character on a flat pattern background, bouncy movement."
- **Eyecatch:** A short title-card bumper around an ad break. Prompt: "a held illustrated still of the character with a quick graphic wipe" (add the logo in edit, not in the model).

---

# Part C. Sub-styles as selectable looks

## Classic 80s–90s cel (OVA) look
- Linework: hand-inked black outlines with slight wobble, detailed hair highlights, sharp chins.
- Shading: hard two-tone cel shadows, airbrushed metal highlights.
- Palette: slightly faded film colour, deep night blues, magenta and teal accents.
- Motion: on twos and threes, held poses, pan cels, hand-drawn smoke and explosions.
- Compositing: film grain, slight gate weave, soft halation on lights, no digital bloom.

## Modern TV digital
- Linework: clean, thin, even digital lines, sometimes coloured.
- Shading: one shadow tone plus a highlight, gradient on hair.
- Palette: bright, clean, mid-saturation.
- Motion: limited, on threes in talk, on twos in action, kuchi-paku mouths.
- Compositing: light bloom, soft depth blur, gradient overlays for time of day.

## Theatrical painterly (hand-painted backgrounds)
- Linework: thin dark-brown outlines, uniform weight.
- Shading: flat colour with one soft shadow tone.
- Palette: natural saturated greens, blues and earth tones.
- Motion: full, weighty, on ones and twos with clear anticipation and settle.
- Compositing: almost none; visible gouache brushwork in the background.

## Photoreal-background romantic drama
- Linework: thin, delicate, simple character designs.
- Shading: one shadow tone, with light-coloured rims.
- Palette: twilight gradients, teal shadows, warm highlights.
- Motion: modest character motion on twos and threes; moving clouds, rain and light.
- Compositing: lens flare, bloom, light shafts, particles, depth blur, wet reflections.

## High-contrast action sakuga
- Linework: rough, energetic, variable-weight lines that loosen at speed.
- Shading: minimal or dropped during fast motion; solid black shadows.
- Palette: show colours broken by monochrome impact flashes.
- Motion: mixed timing: slow wind-up on threes, strike on ones, smears, hit-stop.
- Compositing: impact-synced shake, radial flashes, dust and geometric debris.

## Soft slice-of-life
- Linework: very thin, soft, coloured outlines, rounded shapes.
- Shading: light single tone, blush on cheeks.
- Palette: pale pastels, low contrast, lifted blacks.
- Motion: small gestures on threes, gentle easing, long holds.
- Compositing: soft window light, bokeh, slight haze, shallow depth of field.

## Cyberpunk
- Linework: fine technical lines, dense detail on machinery and signage.
- Shading: hard shadows, neon colour spill on skin.
- Palette: teal, magenta and amber on black; or desaturated grey-green.
- Motion: restrained, realistic, on twos; long holds on cityscapes.
- Compositing: rain, haze, monitor glow, light trails, film grain.

## Watercolour / sketch (Takahata-like)
- Linework: rough charcoal or pencil, uneven pressure, open gaps.
- Shading: none; loose wash that does not fill to the line.
- Palette: pale washes on white paper.
- Motion: naturalistic on twos; lines may roughen with emotion.
- Compositing: none; paper texture, edges fading to white.

## Shonen battle
- Linework: bold tapered black outlines, sharp hair shapes.
- Shading: hard two-tone, strong rim light, glowing aura.
- Palette: saturated primaries with a signature energy colour.
- Motion: big anticipation poses, fast bursts, speed lines, impact frames, hit-stop.
- Compositing: aura glow, dust, debris, radial background streaks.

## Mecha
- Linework: precise panel lines, hard mechanical edges, hand-drawn or toon-shaded 3D.
- Shading: three-tone metal with sharp specular streaks.
- Palette: unit colours on grey-blue skies or black space.
- Motion: heavy, slow starts with fast thruster bursts; missile trails; low-angle scale shots.
- Compositing: thruster glow, cross-shaped flares, dust plumes, heat haze.

---

# Part D. Image-to-video specifics for anime on Seedance-class models

**What the guides say**
- Public guides are mostly third-party and vendor-written; none publish test data for anime. Treat specifics as claims to test.
- In image-to-video, the start frame sets the style more than the prompt does (Atlas Cloud, 2.0 guide). Draw it at the exact framing, line weight and shading you want.
- fal's 2.5 guide: 4 to 30 seconds per generation, native audio on by default. To pin the image: "Use @Image1 as the exact first frame and continue forward." Describe what stays fixed and the first new action; do not re-describe the picture.
- Higgsfield's 2.5 guide: put a global style block first (including what must not appear), then first frame and blocking, shots, camera, lighting, and audio last. Its default audio line is "No music."
- No guide confirms a separate negative-prompt field for 2.5. Write exclusions as plain "no ..." constraints in the prompt (unverified whether the field exists on a given platform).
- Atlas Cloud's 2.5 anime guide: use at most two style anchors; words such as "cinematic lighting", "dramatic shadows" and "4k" pull the result toward a 3D or plastic look. Its "flat sRGB" and ":1.2 weight" tips are vendor claims (unverified).
- Flat 2D is harder than stylised 3D: clean lines and flat fills expose flicker (Atlas Cloud).
- Keep one dominant action per shot. Use the shortest duration that fits the action.

**Failure modes and preventive wording**

| Failure | Wording that helps |
|---|---|
| Drift to 3D or semi-real shading | "Flat 2D cel animation. Flat colour fills with one hard-edged shadow tone. Not a 3D render, no volumetric shading, no realistic skin texture, no glossy highlights." Remove "cinematic", "photoreal", "4k". |
| Over-smooth motion | "Animated on twos: each drawing is held for two frames, stepped pose-to-pose motion, no in-between blending, no motion blur on the character." If it still smooths, hold frames in the edit (unverified as a fix; the guides only suggest held frames and punchy key poses). |
| Line boil, colour crawl | "Outlines stay stable and the same thickness on every frame; colours stay flat and constant." Use thicker, simpler lines and a limited palette in the start frame. |
| Melting faces | Keep the face large enough in frame; "facial features stay exactly as in the first frame; the head turns no more than a quarter." Avoid long clips and full head turns. |
| Mouth flap errors | "Mouth closed throughout" or "the mouth opens and closes in three simple shapes only while speaking; teeth and tongue not detailed." Name who speaks and who keeps the mouth closed (fal). |
| Inconsistent line weight | State the weight and colour once in the style block and add "line weight is identical in close and wide framing." |
| Unwanted camera shake | "Locked-off camera, completely static frame, no shake, no drift, no zoom." For action: "shake only for four frames on impact." |
| Hand and limb melt | Simple hand poses; hide complex gestures; one action per shot. |
| Background warping on pans | "The background is a single flat painting that slides without changing shape." |

**Camera moves for flat art**
- Describe layers, not a physical dolly: "the painted background slides slowly left; the foreground bush slides faster; the character layer stays centred."
- Push-in: "a slow scale-up of the whole flat image toward the face, no change in perspective."
- Tilt: "the frame travels up a tall painted background."
- Use true 3D camera language ("orbits", "flies through") only for the hybrid 3D-background look, and say so.
- Give speed and end point: "over the full shot, ends with the character on the right third."

**Locking style to the start frame**
- Open with: "Use the image as the exact first frame. Keep its art style unchanged: same line weight, same flat colours, same shading, same character design."
- Repeat three or four invariants (hair colour and shape, outfit, eye design, palette).
- Do not add a second style in words that conflicts with the picture.
- For sequences, start the next clip from the last frame of the previous one (fal), and use a character sheet under flat lighting as a second reference.
- End every prompt with the audio line: named sound effects with timing, then "No music."

---

# Part E. Vague note to concrete change

| Note | Concrete changes (layout / timing / FX / compositing / SFX) |
|---|---|
| More sakuga | Mixed timing (slow wind-up, strike on ones), smears, hand-drawn debris and dust, camera that moves with the action, looser lines at speed. |
| Make it hit harder | Longer anticipation hold, one or two impact frames, three-to-five-frame hit-stop, four-frame shake, shockwave ring; a beat of silence then a sharp crack and low boom. |
| More Ghibli-feeling | Painted gouache background, thin brown lines, flat shading, wind in grass and hair, weighty everyday movement, a quiet pause; wind and insect ambience. |
| More emotional | Closer framing or hands and feet inserts, long hold, one small gesture, shallow focus, soft backlight; room tone and one breath. |
| More hype | Low angle, forced perspective, pose-to-pose snaps, speed lines, colour flash, rim light; rising whoosh into impact. |
| Calmer | Locked camera, wide framing, on threes, only environmental motion, low contrast; wind, distant birds. |
| Nostalgic | 90s cel look, film grain, faded colour, golden-hour light, pan cel over a still; cicadas, distant train. |
| Dreamlike | Slow floating motion, soft bloom, pale palette, drifting particles, layers sliding at mismatched speeds; muffled, reverberant sound. |
| More cinematic | Wider aspect framing, foreground occlusion, motivated light source, slow push-in, depth blur, grain. |
| More dynamic | Diagonal composition, background animation or fast parallax, hair and cloth follow-through, shorter shot. |
| Lonelier | Tiny figure in a large empty frame, long hold, flat evening light; single ambient sound. |
| More tense | Tilted horizon, tight eye close-up, held cel with one twitch, hard shadow; ticking, hum, then silence. |
| Cuter | Rounder shapes, bigger eyes, bouncy overshoot, blush, pastel palette, sparkle; soft pops and squeaks. |
| Darker / grittier | Thicker lines, heavy black shadow shapes, desaturated palette with one accent, rain or dust, grain. |
| Faster | Fewer in-betweens, smears, whip pan, speed lines replacing the background; sharp whooshes. |
| More weight | Slower start, squash on landing, dust puff, camera dip, cloth settle after the stop; low thud. |
| More magical | Glowing particles, hair lifting, rim light in the effect colour, slow upward tilt; shimmer and soft wind. |
| More epic | Extreme wide with tiny figures, slow tilt up, towering clouds, light shafts; deep wind and distant rumble. |
| More stylised | Flat graphic background, limited palette, hard silhouettes, held poses, symmetric framing. |
| More real | Realistic proportions, accurate perspective, subtle acting on twos, natural light, detailed background clutter; dry close foley. |

---

# Sources

- Atlas Cloud, Seedance 2.5 anime guide: https://www.atlascloud.ai/blog/guides/seedance-2.5-anime-prompts-style-control
- Atlas Cloud, Seedance 2.0 2D animation guide: https://www.atlascloud.ai/blog/guides/seedance-2.0-animation-2d
- Higgsfield, Seedance 2.5 prompting guide: https://higgsfield.ai/blog/seedance-2-5-prompting-guide
- fal, Seedance 2.5 prompting guide: https://fal.ai/learn/devs/seedance-2-5-prompting-guide
- Magnific, how to write prompts for Seedance 2.0 (search summary only): https://www.magnific.com/blog/how-to-write-prompts-for-seedance-2-0/
- Luma, Seedance 2.5 scenes guide (search summary only): https://lumalabs.ai/learning-center/articles/seedance-2-5-how-to-think-in-scenes
- Sakuga Blog glossary: https://blog.sakugabooru.com/glossary/
- Sakuga Blog, Hosoda and kagenashi: https://blog.sakugabooru.com/2019/03/16/digimon-adventure-20/
- Sakuga Blog, makeup animation: https://blog.sakugabooru.com/2017/04/13/attack-on-titan-season-2-production-notes-1-2/
- ANN, Yuichi Terao interview: https://www.animenewsnetwork.com/feature/2018-01-10/interview-yuichi-terao-chief-of-ufotable-digital-team/.125658
- Wikipedia: Yutaka Nakamura, Naoko Yamada, Science Saru, Ichirō Itano, Osamu Dezaki, Hiroyuki Imaishi (en.wikipedia.org/wiki/Yutaka_Nakamura and siblings)
- Animation Obsessive, Patlabor 2 layouts and fisheye: https://animationobsessive.substack.com/p/life-under-martial-law
- BFI, Takahata and Kaguya: https://www2.bfi.org.uk/node/48309
- VFX Voice, Shinkai on lens flares: https://vfxvoice.com/?p=13137829
- Cartoon Brew, Shinkai retrospective: https://www.cartoonbrew.com/anime/makoto-shinkai-career-retrospective-your-name-225859.html
- Japan Times, Akira feature: https://features.japantimes.co.jp/akira-new/
- Tsurumaki interview on poles (translation): https://buymeacoffee.com/rikki/evangelion-1-0-crc-interview-kazuya-tsurumaki-3
- Animétudes, Imaishi and the Kanada school: https://animetudes.com/2021/07/11/artist-spotlight-hiroyuki-imaishi/
- Cartoon Brew, Kon's editing: https://cartoonbrew.com/anime/learn-how-satoshi-kon-edited-space-and-time-102014.html
- Edinburgh FORUM journal, Miyazaki and "ma": https://journals.ed.ac.uk/forum/article/download/2906/3952
