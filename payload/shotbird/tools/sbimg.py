#!/usr/bin/env python3
"""sbimg for Linux: image and video helper for Shotbird's agents.

Same commands, options and JSON as the macOS build (tools/sbimg.swift). Needs Pillow, numpy and, for `frames`,
ffmpeg + ffprobe:   sudo apt install python3-pil python3-numpy ffmpeg fonts-dejavu-core

  sbimg frames <video> <outdir> [--every 2.0] [--max 40] [--width 1280]
  sbimg grid   <image> <out.png> [--step 10]
  sbimg crop   <image> <out.png> --rect x,y,w,h [--scale 2]
  sbimg info   <image>
  sbimg maskinfo  <mask.png> [--pad 0.12]
  sbimg mark      <image> <mask.png> <out.png> [--rect x,y,w,h]
  sbimg composite <base> <edit> <mask.png> <out.png> [--rect x,y,w,h] [--feather px]

Every subcommand prints JSON to stdout; errors go to stderr with a non-zero exit.
"""
import io
import json
import math
import os
import subprocess
import sys


def fail(msg):
    sys.stderr.write("sbimg: %s\n" % msg)
    sys.exit(1)


try:
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    fail("needs Pillow and numpy: sudo apt install python3-pil python3-numpy")

LANCZOS = getattr(Image, "Resampling", Image).LANCZOS


# ---------------------------------------------------------------------------------------------- helpers

def num(x):
    return round(float(x), 3)


def emit(obj):
    print(json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False))


def expand(path):
    return os.path.abspath(os.path.expanduser(path))


class Args:
    """Positional arguments plus `--key value` / `--key=value` options."""

    def __init__(self, raw):
        self.positional, self.options = [], {}
        i = 0
        while i < len(raw):
            a = raw[i]
            if a.startswith("--"):
                key = a[2:]
                if "=" in key:
                    k, v = key.split("=", 1)
                    self.options[k] = v
                elif i + 1 < len(raw):
                    self.options[key] = raw[i + 1]
                    i += 1
                else:
                    fail("missing value for --%s" % key)
            else:
                self.positional.append(a)
            i += 1

    def double(self, key, default):
        v = self.options.get(key)
        if v is None:
            return default
        try:
            return float(v)
        except ValueError:
            fail("--%s must be a number, got %s" % (key, v))


def load_image(path):
    try:
        im = Image.open(expand(path))
        im.load()
        return im.convert("RGBA")
    except Exception:  # noqa: BLE001 - any unreadable file is one clean error
        fail("cannot read image %s" % path)


def save(img, path, jpeg=False):
    try:
        if jpeg:
            img.convert("RGB").save(path, "JPEG", quality=86)
        else:
            if img.mode == "RGBA" and img.getchannel("A").getextrema() == (255, 255):
                img = img.convert("RGB")  # fully opaque: a smaller PNG
            img.save(path, "PNG")
    except OSError:
        fail("cannot write %s" % path)


FONTS = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
         "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
         "/Library/Fonts/Arial Bold.ttf", "/System/Library/Fonts/Supplemental/Arial Bold.ttf"]


def font(size):
    size = max(8, int(round(size)))
    for p in FONTS:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                pass
    try:
        return ImageFont.load_default(size)
    except TypeError:
        return ImageFont.load_default()


class Label:
    """White text on a dark rounded pill, readable on any image."""

    def __init__(self, text, font_size):
        self.text, self.fs = text, font_size
        self.font = font(font_size)
        asc, desc = self.font.getmetrics()
        self.padx, self.pady = font_size * 0.45, font_size * 0.28
        self.w = int(math.ceil(self.font.getlength(text) + self.padx * 2))
        self.h = int(math.ceil(asc + desc + self.pady * 2))

    def draw(self, img, x, y_top):
        """Pastes the pill with its top-left corner at (x, y_top) onto an RGBA image."""
        layer = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        d.rounded_rectangle([0, 0, self.w - 1, self.h - 1], radius=self.fs * 0.35, fill=(0, 0, 0, 158))
        d.text((self.padx, self.pady), self.text, font=self.font, fill=(255, 255, 255, 255))
        px = int(round(min(max(0, x), img.width - self.w)))
        py = int(round(min(max(0, y_top), img.height - self.h)))
        img.alpha_composite(layer, (px, py))


def clock(t):
    m = int(t) // 60
    return "%02d:%04.1f" % (m, t - m * 60)


# ---------------------------------------------------------------------------------------------- frames

GX, GY, SUB = 32, 18, 4


def ffprobe_json(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", path],
                       capture_output=True, text=True)
    if r.returncode:
        fail("cannot read the video: %s" % (r.stderr.strip()[:200] or "ffprobe failed (is ffmpeg installed?)"))
    return json.loads(r.stdout)


def fraction(s):
    try:
        a, b = str(s).split("/")
        return float(a) / float(b) if float(b) else 0.0
    except (ValueError, ZeroDivisionError):
        return 0.0


def median(xs):
    if not xs:
        return 0.0
    s = sorted(xs)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2


def detect_cuts(times, grid, hist, fps, duration):
    """Hard cuts: a frame-to-frame change that is a local peak, well above the local median change
    (adaptive, so motion-heavy shots need a bigger spike) and backed by a histogram shift."""
    n = len(times)
    if n <= 2:
        return []
    d = np.zeros(n)
    hd = np.zeros(n)
    d[1:] = np.abs(grid[1:] - grid[:-1]).mean(axis=1)
    hd[1:] = np.abs(hist[1:] - hist[:-1]).sum(axis=1) / 2
    win = max(8, int(fps * 0.75))
    cands = []
    for i in range(1, n):
        lo, hi = max(1, i - win), min(n - 1, i + win)
        neigh = [d[j] for j in range(lo, hi + 1) if abs(j - i) > 1]
        thr = max(0.07, median(neigh) * 3.5 + 0.03)
        peak = all(j == i or d[j] < d[i] or (d[j] == d[i] and j > i) for j in range(max(1, i - 2), min(n - 1, i + 2) + 1))
        if peak and d[i] > thr and (hd[i] > 0.12 or d[i] > 0.2):
            cands.append((i, d[i] / thr))
    min_shot = 0.4  # shots shorter than this are almost always flashes or glitches: keep the stronger cut
    cuts = []
    for i, score in cands:
        t = times[i]
        if t < min_shot * 0.5:
            continue
        if cuts and t - cuts[-1][0] < min_shot:
            if score > cuts[-1][1]:
                cuts[-1] = (t, score)
        else:
            cuts.append((t, score))
    if cuts and duration - cuts[-1][0] < 0.25:
        cuts.pop()
    return [c[0] for c in cuts]


def grab_frame(video, t, width):
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", "%.3f" % t, "-i", video, "-frames:v", "1",
                        "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True)
    if not r.stdout:
        return None
    im = Image.open(io.BytesIO(r.stdout)).convert("RGB")
    im.thumbnail((width, width), LANCZOS)
    return im


def frames(args):
    if len(args.positional) != 2:
        fail("usage: sbimg frames <video> <outdir> [--every 2.0] [--max 40] [--width 1280]")
    video, outdir = expand(args.positional[0]), expand(args.positional[1])
    every = max(0.2, args.double("every", 2.0))
    max_frames = max(1, int(args.double("max", 40)))
    width = int(max(64, args.double("width", 1280)))
    if not os.path.isfile(video):
        fail("no such file: %s" % video)
    os.makedirs(outdir, exist_ok=True)

    probe = ffprobe_json(video)
    vs = next((s for s in probe.get("streams", []) if s.get("codec_type") == "video"), None)
    if not vs:
        fail("no video track in %s" % os.path.basename(video))
    audio_s = next((s for s in probe.get("streams", []) if s.get("codec_type") == "audio"), None)
    duration = float(probe.get("format", {}).get("duration") or vs.get("duration") or 0)
    fps = fraction(vs.get("avg_frame_rate")) or fraction(vs.get("r_frame_rate"))
    shown_w, shown_h = int(vs.get("width", 0)), int(vs.get("height", 0))
    rot = vs.get("tags", {}).get("rotate")
    for sd in vs.get("side_data_list", []) or []:
        rot = sd.get("rotation", rot)
    try:
        if abs(int(float(rot))) % 180 == 90:
            shown_w, shown_h = shown_h, shown_w
    except (TypeError, ValueError):
        pass
    audio = None
    if audio_s:
        audio = {"format": audio_s.get("codec_name"), "sample_rate": float(audio_s.get("sample_rate") or 0),
                 "channels": int(audio_s.get("channels") or 0)}

    # 1. Decode every frame once at 128x72 and keep a tiny signature of each (a 32x18 luma grid + a 16-bin histogram).
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", video, "-an", "-sn", "-vf", "scale=128:72:flags=area,format=gray",
                        "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True)
    n = len(r.stdout) // (128 * 72)
    if n < 1:
        fail("frames failed: could not decode the video")
    arr = np.frombuffer(r.stdout[:n * 128 * 72], dtype=np.uint8).reshape(n, 72, 128).astype(np.float32) / 255
    grid = arr.reshape(n, GY, SUB, GX, SUB).mean(axis=(2, 4)).reshape(n, GY * GX)
    bins = np.minimum(15, (arr.reshape(n, -1) * 16).astype(np.int32))
    hist = np.stack([np.bincount(b, minlength=16) for b in bins]).astype(np.float32) / (128 * 72)
    pts = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "frame=best_effort_timestamp_time", "-of", "csv=p=0", video], capture_output=True, text=True).stdout
    times = []
    for line in pts.split():
        try:
            times.append(float(line.strip(",")))
        except ValueError:
            pass
    times = sorted(times)
    if len(times) != n:
        step = 1.0 / (fps if fps > 0 else 24)
        times = [i * step for i in range(n)]

    # 2. Cuts and shots.
    cut_times = detect_cuts(times, grid, hist, fps if fps > 0 else 24, duration)
    bounds = [0.0] + cut_times + [duration]
    shots = [(k + 1, bounds[k], bounds[k + 1]) for k in range(len(bounds) - 1)]

    def shot_at(t):
        hit = [s[0] for s in shots if t >= s[1]]
        return hit[-1] if hit else 1

    # 3. Export times: the middle of each shot first, then a frame every `every` seconds.
    mids = [(s[1] + s[2]) / 2 for s in shots]
    if len(mids) >= max_frames:
        picks = [mids[0 if max_frames == 1 else int(round(j * (len(mids) - 1) / (max_frames - 1)))] for j in range(max_frames)]
    else:
        picks = list(mids)
        t = every / 2
        while t < duration - 0.05 and len(picks) < max_frames:
            if not any(abs(p - t) < every * 0.5 for p in picks):
                picks.append(t)
            t += every
    picks = sorted({round(min(max(0.0, p), max(0.0, duration - 0.04)), 3) for p in picks})

    # 4. Export the frames.
    exported = []
    for i, t in enumerate(picks):
        im = grab_frame(video, t, width) or grab_frame(video, max(0.0, t - 0.15), width)
        if im is None:
            fail("frames failed: could not read the frame at %.2fs" % t)
        name = "%03d_t%06.2f.jpg" % (i + 1, t)
        im.save(os.path.join(outdir, name), "JPEG", quality=86)
        exported.append({"file": name, "t": t, "shot": shot_at(t), "img": im})

    # 5. Contact sheet, labelled with frame number, timestamp and shot.
    contact = None
    if exported:
        count = len(exported)
        cols = count if count <= 4 else (4 if count <= 12 else (5 if count <= 30 else 6))
        rows = (count + cols - 1) // cols
        gap = 8
        tw = min(480, (2400 - gap * (cols + 1)) // cols)
        first = exported[0]["img"]
        th = int(tw * first.height / first.width)
        W, H = cols * tw + gap * (cols + 1), rows * th + gap * (rows + 1)
        sheet = Image.new("RGBA", (W, H), (18, 18, 18, 255))
        fs = max(11, tw / 26)
        for i, f in enumerate(exported):
            x, y = gap + (i % cols) * (tw + gap), gap + (i // cols) * (th + gap)
            sheet.paste(f["img"].resize((tw, th), LANCZOS).convert("RGBA"), (x, y))
            Label("#%d  %s  S%d" % (i + 1, clock(f["t"]), f["shot"]), fs).draw(sheet, x + fs * 0.5, y + fs * 0.5)
        contact = os.path.join(outdir, "contact.jpg")
        save(sheet, contact, jpeg=True)

    shot_rows = []
    for n_, s, e in shots:
        mid = (s + e) / 2
        pool = [f for f in exported if f["shot"] == n_]
        rep = min(pool, key=lambda f: abs(f["t"] - mid))["file"] if pool else None
        shot_rows.append({"n": n_, "start": num(s), "end": num(e), "duration": num(e - s), "frame": rep})
    info = {
        "video": video, "outdir": outdir, "duration": num(duration), "fps": num(fps), "width": shown_w, "height": shown_h,
        "frames_analysed": n, "has_audio": audio is not None, "audio": audio, "cuts": [num(c) for c in cut_times],
        "shots": shot_rows, "frames": [{"file": f["file"], "t": num(f["t"]), "shot": f["shot"]} for f in exported],
        "contact": contact,
        "note": "Audio is not transcribed; has_audio only reports an audio track. Cuts are hard cuts; dissolves and fades are not split.",
    }
    with open(os.path.join(outdir, "info.json"), "w", encoding="utf-8") as f:
        json.dump(info, f, indent=2, sort_keys=True, ensure_ascii=False)
    emit(info)


# ---------------------------------------------------------------------------------------------- grid / crop / info

def grid_cmd(args):
    if len(args.positional) != 2:
        fail("usage: sbimg grid <image> <out.png> [--step 10]")
    step = args.double("step", 10)
    if not 2 <= step <= 50:
        fail("--step must be between 2 and 50 (percent)")
    img = load_image(args.positional[0])
    W, H = img.size
    lw = max(1.0, min(W, H) / 900)
    fs = max(11.0, min(W, H) / 55)
    marks, p = [], step
    while p < 100 - 1e-9:
        marks.append(p)
        p += step
    dark = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    light = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dd, ld = ImageDraw.Draw(dark), ImageDraw.Draw(light)
    for m in marks:  # a dark under-stroke plus a white stroke, so lines show on light and dark images; 50% is brighter
        x, y = int(round(W * m / 100)), int(round(H * m / 100))
        mid = abs(m - 50) < 1e-9
        dw = max(1, int(round(lw + 2)))
        wh = max(1, int(round(lw * 1.8 if mid else lw)))
        for d, color, wd in ((dd, (0, 0, 0, 115), dw), (ld, (255, 255, 255, 230 if mid else 153), wh)):
            d.line([(x, 0), (x, H)], fill=color, width=wd)
            d.line([(0, y), (W, y)], fill=color, width=wd)
    img.alpha_composite(dark)
    img.alpha_composite(light)
    for m in marks:  # x% along the top edge, y% (measured from the top) down the left edge
        text = ("%.0f%%" if m % 1 == 0 else "%.1f%%") % m
        top = Label(text, fs)
        x = W * m / 100
        top.draw(img, x - top.w - 3 if x + top.w + 4 > W else x + 3, 3)
        left = Label(text, fs)
        y = H * m / 100
        left.draw(img, 3, y - left.h - 3 if y + left.h + 4 > H else y + 3)
    out = expand(args.positional[1])
    save(img, out)
    emit({"out": out, "width": W, "height": H, "step_percent": step,
          "note": "Percentages are measured from the top-left corner. Convert to pixels with x*width/100 and y*height/100."})


def parse_rect(s, inside=False):
    try:
        r = [float(x.strip()) for x in s.split(",")]
    except ValueError:
        r = []
    ok = len(r) == 4 and all(0 <= v <= 1 for v in r) and r[2] > 0 and r[3] > 0
    if ok and inside:
        ok = r[0] + r[2] <= 1.0001 and r[1] + r[3] <= 1.0001
    return r if ok else None


def crop_cmd(args):
    if len(args.positional) != 2 or "rect" not in args.options:
        fail("usage: sbimg crop <image> <out.png> --rect x,y,w,h [--scale 2]   (rect in fractions 0-1, from the top-left)")
    r = parse_rect(args.options["rect"])
    if not r:
        fail("--rect needs four fractions 0-1: x,y,w,h (e.g. 0.4,0.1,0.2,0.3)")
    scale = args.double("scale", 2)
    if not 0 < scale <= 8:
        fail("--scale must be between 0 and 8")
    img = load_image(args.positional[0])
    W, H = img.size
    px, py = int(round(r[0] * W)), int(round(r[1] * H))
    pw = max(1, min(int(round(r[2] * W)), W - px))
    ph = max(1, min(int(round(r[3] * H)), H - py))
    if px >= W or py >= H:
        fail("the rect falls outside the image")
    ow, oh = max(1, int(round(pw * scale))), max(1, int(round(ph * scale)))
    part = img.crop((px, py, px + pw, py + ph)).resize((ow, oh), LANCZOS)
    out = expand(args.positional[1])
    save(part, out)
    emit({"out": out, "width": ow, "height": oh, "scale": scale, "source_size": [W, H], "source_px": [px, py, pw, ph]})


COMMON = [("1:1", 1), ("4:5", 0.8), ("5:4", 1.25), ("4:3", 4 / 3), ("3:4", 0.75), ("3:2", 1.5), ("2:3", 2 / 3),
          ("16:9", 16 / 9), ("9:16", 9 / 16), ("21:9", 21 / 9), ("2.39:1", 2.39)]


def info_cmd(args):
    if len(args.positional) != 1:
        fail("usage: sbimg info <image>")
    W, H = load_image(args.positional[0]).size
    ratio = W / H
    near = min(COMMON, key=lambda c: abs(c[1] - ratio))
    emit({"path": expand(args.positional[0]), "width": W, "height": H, "aspect": num(ratio),
          "aspect_label": near[0] if abs(near[1] - ratio) / near[1] < 0.02 else None})


# ---------------------------------------------------------------------------------------------- area edits
# Higgsfield has no masked inpainting, so an area edit is: the edit model redraws the frame (or a crop of it)
# from the original plus a copy with the area tinted red, then `composite` keeps only the masked area of that
# redraw. Pixels outside the mask come from the original, so nothing outside the mark can change.

def mask_weights(path, W, H):
    """A mask as H x W weights 0..1: white (or opaque white) marks the area to change; black or transparent keeps."""
    mk = load_image(path)
    if mk.size != (W, H):
        mk = mk.resize((W, H), LANCZOS)
    bg = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    bg.alpha_composite(mk)
    a = np.asarray(bg, dtype=np.float32)
    return (0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]) / 255


def box_blur(a, r, axis):
    k = 2 * r + 1
    pad = [(0, 0), (0, 0)]
    pad[axis] = (r, r)
    c = np.cumsum(np.pad(a, pad, mode="edge"), axis=axis, dtype=np.float64)
    zero = list(c.shape)
    zero[axis] = 1
    c = np.concatenate([np.zeros(zero), c], axis=axis)
    n = a.shape[axis]
    return ((np.take(c, range(k, k + n), axis=axis) - np.take(c, range(0, n), axis=axis)) / k).astype(np.float32)


def feather(m, r):
    """Three box-blur passes (close to a Gaussian): softens the mask edge so the paste has no hard seam."""
    if r < 1:
        return m
    for _ in range(3):
        m = box_blur(box_blur(m, r, 1), r, 0)
    return m


def rect_option(args):
    s = args.options.get("rect")
    if s is None:
        return None
    r = parse_rect(s, inside=True)
    if not r:
        fail("--rect needs four fractions 0-1: x,y,w,h inside the image (e.g. 0.4,0.1,0.2,0.3)")
    return r


def px_rect(r, W, H):
    x, y = min(W - 1, int(round(r[0] * W))), min(H - 1, int(round(r[1] * H)))
    return x, y, max(1, min(W - x, int(round(r[2] * W)))), max(1, min(H - y, int(round(r[3] * H))))


ASPECTS = [("1:1", 1), ("4:5", 0.8), ("5:4", 1.25), ("4:3", 4 / 3), ("3:4", 0.75), ("3:2", 1.5), ("2:3", 2 / 3),
           ("16:9", 16 / 9), ("9:16", 9 / 16), ("21:9", 21 / 9)]


def maskinfo_cmd(args):
    if len(args.positional) != 1:
        fail("usage: sbimg maskinfo <mask.png> [--pad 0.12]")
    W, H = load_image(args.positional[0]).size
    m = mask_weights(args.positional[0], W, H)
    ys, xs = np.nonzero(m > 0.5)
    if len(xs) == 0:
        fail("the mask is empty: nothing is marked")
    x0, x1, y0, y1, n = int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max()), len(xs)
    bw, bh = float(x1 - x0 + 1), float(y1 - y0 + 1)
    # Crop for small areas: the marked box plus context, grown to the nearest standard aspect ratio so the edit
    # model returns exactly that shape, then kept inside the frame.
    pad = args.double("pad", 0.12)
    cw, ch = bw + 2 * max(bw * pad, W * 0.04), bh + 2 * max(bh * pad, H * 0.04)
    cw, ch = max(cw, W * 0.3), max(ch, H * 0.3)  # enough surroundings to match light and grain
    ratio = cw / ch
    asp = min(ASPECTS, key=lambda a: abs(math.log(a[1] / ratio)))
    if asp[1] > ratio:
        cw = ch * asp[1]
    else:
        ch = cw / asp[1]
    if cw > W:
        ch *= W / cw
        cw = float(W)
    if ch > H:
        cw *= H / ch
        ch = float(H)
    cx = min(max(0.0, (x0 + bw / 2) - cw / 2), W - cw)
    cy = min(max(0.0, (y0 + bh / 2) - ch / 2), H - ch)
    area = n / (W * H)
    crop_share = cw * ch / (W * H)
    fits = cw >= bw and ch >= bh
    suggest = "crop" if fits and area < 0.12 and crop_share < 0.5 else "full"
    scale = min(4, max(1, 2048 / max(cw, ch)))
    emit({"width": W, "height": H, "area": num(area),
          "bbox": [num(x0 / W), num(y0 / H), num(bw / W), num(bh / H)],
          "crop": [num(cx / W), num(cy / H), num(cw / W), num(ch / H)],
          "crop_aspect": asp[0], "crop_scale": num(scale), "suggest": suggest,
          "note": "suggest=crop: edit a crop (sbimg crop --rect <crop> --scale <crop_scale>; sbimg mark --rect <crop>) at aspect <crop_aspect>, then composite --rect <crop>. suggest=full: edit the whole frame, then composite without --rect."})


def mark_cmd(args):
    if len(args.positional) != 3:
        fail("usage: sbimg mark <image> <mask.png> <out.png> [--rect x,y,w,h]")
    img = load_image(args.positional[0])
    W, H = img.size
    inside = mask_weights(args.positional[1], W, H) > 0.5
    edge = max(2, min(W, H) // 400)

    def shifted(dy, dx):  # inside(x + dx, y + dy), false outside the frame
        out = np.zeros_like(inside)
        ys, xs = slice(max(0, -dy), H - max(0, dy)), slice(max(0, -dx), W - max(0, dx))
        yd, xd = slice(max(0, dy), H - max(0, -dy)), slice(max(0, dx), W - max(0, -dx))
        out[ys, xs] = inside[yd, xd]
        return out

    rim = ~(shifted(0, -edge) & shifted(0, edge) & shifted(-edge, 0) & shifted(edge, 0))
    a = np.where(inside, np.where(rim, 1.0, 0.45), 0.0).astype(np.float32)[..., None]  # solid outline, see-through tint
    px = np.asarray(img, dtype=np.float32).copy()
    red = np.array([255, 32, 32], dtype=np.float32)
    px[..., :3] = np.floor(px[..., :3] * (1 - a) + red * a)
    out_img = Image.fromarray(px.astype(np.uint8))
    r = rect_option(args)
    if r:
        x, y, w, h = px_rect(r, W, H)
        out_img = out_img.crop((x, y, x + w, y + h))
    out = expand(args.positional[2])
    save(out_img, out)
    emit({"out": out, "width": out_img.width, "height": out_img.height})


def composite_cmd(args):
    if len(args.positional) != 4:
        fail("usage: sbimg composite <base> <edit> <mask.png> <out.png> [--rect x,y,w,h] [--feather px]")
    base, edit = load_image(args.positional[0]), load_image(args.positional[1])
    W, H = base.size
    r = rect_option(args)
    rx, ry, rw, rh = px_rect(r, W, H) if r else (0, 0, W, H)
    # The redraw, stretched onto its rect (edit models keep the content's layout when they change the pixel size).
    edited = base.copy()
    edited.alpha_composite(edit.resize((rw, rh), LANCZOS), (rx, ry))
    m = mask_weights(args.positional[2], W, H)
    keep = np.zeros_like(m, dtype=bool)
    keep[ry:ry + rh, rx:rx + rw] = True
    m = np.where(keep, m, 0).astype(np.float32)
    radius = int(args.double("feather", max(3, max(W, H) // 400)))
    m = feather(m, radius)
    b = np.asarray(base, dtype=np.float32).copy()
    e = np.asarray(edited, dtype=np.float32)
    def luma(a):
        return 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]

    diff = np.abs(luma(b) - luma(e)) / 255
    in_rect = keep
    full, ring_m, outside_m = m > 0.99, (m > 0.01) & (m <= 0.99), (m <= 0.01) & in_rect

    def mean(mask):
        return float(diff[mask].mean()) if mask.any() else 0.0

    inside_d, ring_d, outside_d = mean(full), mean(ring_m), mean(outside_m)
    w = m[..., None]
    live = (m > 0.002)[..., None]
    blended = np.rint(b[..., :3] * (1 - w) + e[..., :3] * w)
    b[..., :3] = np.where(live, blended, b[..., :3])
    out = expand(args.positional[3])
    save(Image.fromarray(np.clip(b, 0, 255).astype(np.uint8)), out)
    emit({"out": out, "width": W, "height": H, "feather_px": radius,
          "changed_share": num(float((m > 0.002).sum()) / (W * H)),
          "inside_change": num(inside_d), "edge_diff": num(ring_d), "outside_drift": num(outside_d),
          "seam_risk": "low" if ring_d < 0.06 else "medium" if ring_d < 0.12 else "high",
          "note": "Only pixels inside the feathered mask changed. inside_change near 0 means the model changed nothing there. seam_risk high: the redraw moved or recoloured the frame around the mark; check the edge (sbimg crop) and retry, or use crop mode."})


# ---------------------------------------------------------------------------------------------- main

COMMANDS = {"frames": frames, "grid": grid_cmd, "crop": crop_cmd, "info": info_cmd,
            "maskinfo": maskinfo_cmd, "mark": mark_cmd, "composite": composite_cmd}


def main():
    argv = sys.argv[1:]
    if not argv:
        fail("usage: sbimg frames|grid|crop|info|maskinfo|mark|composite … (see tools/README.md)")
    cmd = argv.pop(0)
    if cmd not in COMMANDS:
        fail("unknown command %s; use frames, grid, crop, info, maskinfo, mark or composite" % cmd)
    COMMANDS[cmd](Args(argv))


if __name__ == "__main__":
    main()
