# Reading a reference video

{{NAME}} attaches a reference video so you can see what he is after. Your job is to extract the **craft** (how it was shot and cut) and reuse it. You never copy the content: not its characters, faces, logos, text, story or exact images. If he wants a specific element carried over, he will say so.

## Steps
1. **Extract frames.** `SB_IMG="$HOME/.claude/skills/shotbird/bin/sbimg"`, then
   `$SB_IMG frames "<video>" "<project>/refs/<name>/" --every <s> --max <n> --width 640`
   - Up to 15 s: `--every 0.25 --max 60`. 15–60 s: `--every 0.5 --max 120`. Longer: `--every 1 --max 120`, and ask them which part matters if it runs past two minutes.
   - It writes numbered frames named with their timestamps, a `contact.jpg` sheet, and `info.json` with duration, frame rate, size, audio and a `cuts` list (detected cut times).
2. **Look.** Read `contact.jpg` first for the overall shape, then the frames around each cut and the frames inside each shot. Never describe a shot you have not looked at.
3. **Break it into shots** from `cuts` (check them by eye: a whip pan or flash can be read as a cut, and a slow dissolve can be missed).
4. **For each shot, fill the nine axes** (SKILL.md): size, angle and height, lens feel (FOV from the ladder), move with direction and speed, support, blocking, light, rhythm, and the sound if it has any (effects only; ignore its music).
5. **For each join, name the transition** from `transitions.md`, with its duration and what carries across.
6. **Measure the rhythm:** shot lengths in seconds, average shot length, where it accelerates or holds.
7. **Name the look:** palette, contrast, grain, aspect ratio, frame-rate feel (slow motion, step-printed, on twos for animation).
8. **Say what you can't tell** from stills: exact speed of a move between two samples, sound, subtle focus pulls. Mark those as estimates.

## Write it down
Save `refs/<name>-analysis.md` in the project:

```
# <file name> — <duration>s, <n> shots, average shot <x>s, <aspect>, <look in one line>
| # | Time | Size | Angle / height | Lens (FOV) | Move, speed | Light | Action | Out-transition |
|---|------|------|----------------|------------|-------------|-------|--------|----------------|
| 1 | 0.0–2.4 | WS | low, knee height, tilt up 20° | 84° (24mm) | fast push-in, ~1 m/s | hard backlight, haze | runner enters left | whip pan right, 6 frames |
Rhythm: …
Look: …
What he probably wants from it: … (camera language? pacing? transitions? light?)
Estimates: …
```

## Tell them, briefly
Reply in the chat with the shot table trimmed to the essentials and one line on what you took from it. If it's unclear which quality he wants (the camera work, the pacing, the transitions or the look), ask once, with options. Otherwise carry on and write the prompts.

## Use it
- Carry the craft into their own subject and world, axis by axis.
- When he will upload the same clip to Seedance as a reference, give it one narrow job in the prompt, in the model's own label form: `@Video1 controls only the camera path and motion rhythm. Do not copy its subject, wardrobe, props or location.` Say in the notes that the clip must be attached when he generates.
- When the clip won't be attached, the prompt must carry everything in words.
- Several references: give each one job (camera from one, transitions from another), one source per axis.
