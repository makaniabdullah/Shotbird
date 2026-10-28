# sbimg: image and video helper for Shotbird agents

`~/.claude/skills/shotbird/bin/sbimg` is built from `tools/sbimg.swift` with `sh ~/.claude/skills/shotbird/tools/build.sh`. It needs only the Command Line Tools, no ffmpeg. Every command prints JSON to stdout. Errors go to stderr with a non-zero exit.

```
SBIMG="$HOME/.claude/skills/shotbird/bin/sbimg"
$SBIMG frames <video> <outdir> [--every 2.0] [--max 40] [--width 1280]
$SBIMG grid   <image> <out.png> [--step 10]
$SBIMG crop   <image> <out.png> --rect x,y,w,h [--scale 2]
$SBIMG info   <image>
$SBIMG maskinfo  <mask.png> [--pad 0.12]
$SBIMG mark      <image> <mask.png> <out.png> [--rect x,y,w,h]
$SBIMG composite <base> <edit> <mask.png> <out.png> [--rect x,y,w,h] [--feather px]
```

## frames: analyse a reference video (Scout)

Use this for mp4 or mov references.
- **Cut detection.** It decodes every frame once and finds hard cuts. A cut is an adaptive spike in frame-to-frame luma change, backed by a histogram shift. Shots shorter than 0.4 s are merged.
- **Exported frames.** It exports the middle frame of each shot first, then one frame every `--every` seconds, up to `--max` frames. Files are named `NNN_tSSS.ss.jpg`, with the long edge at most `--width`.
- **Other outputs.** It writes `contact.jpg`, a labelled contact sheet (`#n  mm:ss.s  S<shot>`), and `info.json`. The JSON is also printed.

`info.json` contains:
- `duration`, `fps`, `width`, `height` (display size, with rotation applied)
- `frames_analysed`
- `has_audio`, and `audio` with format, sample rate and channels
- `cuts`: the times in seconds where each new shot starts
- `shots`: `n`, `start`, `end`, `duration`, and `frame` (the representative exported file)
- `frames`: `file`, `t`, `shot`
- `contact`

**Workflow:**
1. Read `contact.jpg` for the overview.
2. Read each shot's `frame` for detail.
3. Write the analysis: shot list, sizes and angles, camera moves (compare neighbouring frames of the same shot), pacing from shot durations, palette and light, and on-screen text.

**Limits:**
- Audio is not transcribed. You only learn whether a track exists, so say so in the analysis.
- Dissolves, fades and whip-pans hidden by motion blur are not split into separate shots. The periodic frames still cover them.
- Very long videos take longer, because every frame is decoded. Expect about 1–3 s per minute of HD footage.

## grid: measuring overlay (Hawk)

Draws lines every `--step` % (2–50, default 10), labelled along the top edge (x %) and the left edge (y %, from the top). The 50 % lines are brighter. The lines stay readable on light and dark images.

Use it for proportions: read the head's top and chin y %, the shoulder x extents, the feet y %, and so on, then convert to pixels with `% × width / 100` and `% × height / 100`.

Examples:
- **Head-to-body ratio:** a standing adult is about 7–8 heads tall.
- **Head width vs shoulder width.**
- **Face size vs neighbouring shots.**

## crop: close inspection (Hawk)

`--rect` is in fractions of the image (0–1) from the top-left. For example, `0.33,0.12,0.2,0.3` is a box starting at 33 % across and 12 % down, 20 % wide and 30 % tall. A rectangle that runs past the edge is clamped; `source_px` reports the actual pixel box.

The output is upscaled by `--scale` (default 2, max 8) with high-quality interpolation. Use it on faces, hands, logos and text.

## info

Prints `width`, `height`, `aspect`, and `aspect_label`, the nearest common ratio within 2 %, or null.

## maskinfo, mark, composite: area edits (Slate, Hatch, Hawk)

{{NAME}} marks an area on a gen in the board. The server saves `07-edits/<stem>-e<n>/` with `mask.png` (white marks the area to change), `marked.png` and `request.json`. Higgsfield has no masked inpainting, so the edit model redraws the frame, and `composite` keeps only the marked area of that redraw.

- **`maskinfo`** reports:
  - `area` (share of the frame) and `bbox` (fractions from the top-left);
  - a `crop` rect: the marked box plus context, grown to the nearest standard aspect (`crop_aspect`) and kept inside the frame;
  - `crop_scale`, an upscale that brings the crop's long side to about 2048 px;
  - `suggest`: `crop` for small areas, `full` otherwise.
- **`mark`** writes the image with the area tinted red and outlined, as the edit model's second reference. `--rect` crops it the same way as `sbimg crop`.
- **`composite`** writes the result, and its JSON reports the blend:
  - What it does:
    - It stretches `<edit>` onto the frame, or onto `--rect` in crop mode.
    - It feathers the mask by `--feather` px (default: long edge / 400).
    - It blends, so pixels outside the feathered mask are the base's, untouched.
  - What the JSON reports:
    - `inside_change`: the mean luma change inside the mask. Near 0 means the model changed nothing.
    - `edge_diff` and `seam_risk` (`low`, `medium` or `high`): how different the redraw is in the feather ring. `high` means the redraw moved or recoloured the frame there, so check the edge.
    - `outside_drift`: how much the redraw changed outside the mask. Information only, because those pixels are not used.
