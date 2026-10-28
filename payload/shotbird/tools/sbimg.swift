// sbimg: image and video helper for Shotbird's agents (no ffmpeg needed).
//
//   sbimg frames <video> <outdir> [--every 2.0] [--max 40] [--width 1280]
//   sbimg grid   <image> <out.png> [--step 10]
//   sbimg crop   <image> <out.png> --rect x,y,w,h [--scale 2]
//   sbimg info   <image>
//   sbimg maskinfo  <mask.png> [--pad 0.12]                       area edit: marked area, bbox, crop rect
//   sbimg mark      <image> <mask.png> <out.png> [--rect x,y,w,h]  area edit: the image with the area tinted red
//   sbimg composite <base> <edit> <mask.png> <out.png> [--rect x,y,w,h] [--feather px]
//                   area edit: only the masked area of <edit> lands on <base>; everything else stays pixel-identical
//
// Every subcommand prints JSON to stdout; errors go to stderr with a non-zero exit.
// Build with tools/build.sh.
import AVFoundation
import CoreGraphics
import CoreText
import Foundation
import ImageIO
import UniformTypeIdentifiers

// MARK: - Small helpers

func fail(_ msg: String) -> Never {
    FileHandle.standardError.write(("sbimg: " + msg + "\n").data(using: .utf8)!)
    exit(1)
}

func emit(_ obj: Any) {
    guard let d = try? JSONSerialization.data(withJSONObject: obj, options: [.prettyPrinted, .sortedKeys, .withoutEscapingSlashes]),
          let s = String(data: d, encoding: .utf8) else { fail("could not encode JSON") }
    print(s)
}

func round3(_ x: Double) -> Double { (x * 1000).rounded() / 1000 }

/// A JSON number with at most 3 decimals (JSONSerialization prints raw doubles as 1.7709999999999999).
func num(_ x: Double) -> NSDecimalNumber { NSDecimalNumber(string: String(format: "%.3f", x)) }

func expand(_ path: String) -> URL { URL(fileURLWithPath: (path as NSString).expandingTildeInPath).standardizedFileURL }

/// Positional arguments plus `--key value` / `--key=value` options.
struct Args {
    var positional: [String] = []
    var options: [String: String] = [:]

    init(_ raw: [String]) {
        var i = 0
        while i < raw.count {
            let a = raw[i]
            if a.hasPrefix("--") {
                let key = String(a.dropFirst(2))
                if let eq = key.firstIndex(of: "=") {
                    options[String(key[..<eq])] = String(key[key.index(after: eq)...])
                } else if i + 1 < raw.count {
                    options[key] = raw[i + 1]; i += 1
                } else {
                    fail("missing value for --\(key)")
                }
            } else {
                positional.append(a)
            }
            i += 1
        }
    }

    func double(_ key: String, _ def: Double) -> Double {
        guard let v = options[key] else { return def }
        guard let d = Double(v) else { fail("--\(key) must be a number, got \(v)") }
        return d
    }
}

func loadImage(_ path: String) -> CGImage {
    guard let src = CGImageSourceCreateWithURL(expand(path) as CFURL, nil),
          let img = CGImageSourceCreateImageAtIndex(src, 0, nil) else { fail("cannot read image \(path)") }
    return img
}

func save(_ img: CGImage, to url: URL, jpeg: Bool) {
    let type = (jpeg ? UTType.jpeg : UTType.png).identifier as CFString
    guard let dst = CGImageDestinationCreateWithURL(url as CFURL, type, 1, nil) else { fail("cannot write \(url.path)") }
    let props: [CFString: Any] = jpeg ? [kCGImageDestinationLossyCompressionQuality: 0.86] : [:]
    CGImageDestinationAddImage(dst, img, props as CFDictionary)
    if !CGImageDestinationFinalize(dst) { fail("cannot write \(url.path)") }
}

func canvas(_ w: Int, _ h: Int) -> CGContext {
    guard let ctx = CGContext(data: nil, width: w, height: h, bitsPerComponent: 8, bytesPerRow: 0,
                              space: CGColorSpace(name: CGColorSpace.sRGB)!,
                              bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue)
    else { fail("cannot allocate a \(w)x\(h) canvas") }
    ctx.interpolationQuality = .high
    return ctx
}

// MARK: - Labels (white text on a dark pill, readable on any image)

struct Label {
    let line: CTLine
    let size: CGSize
    let pad: CGPoint
    let descent: CGFloat
    let radius: CGFloat

    init(_ text: String, fontSize: CGFloat) {
        let font = CTFontCreateUIFontForLanguage(.emphasizedSystem, fontSize, nil)
            ?? CTFontCreateWithName("Helvetica-Bold" as CFString, fontSize, nil)
        let attrs: [NSAttributedString.Key: Any] = [
            NSAttributedString.Key(kCTFontAttributeName as String): font,
            NSAttributedString.Key(kCTForegroundColorAttributeName as String): CGColor(gray: 1, alpha: 1),
        ]
        line = CTLineCreateWithAttributedString(NSAttributedString(string: text, attributes: attrs))
        var asc: CGFloat = 0, desc: CGFloat = 0, lead: CGFloat = 0
        let w = CGFloat(CTLineGetTypographicBounds(line, &asc, &desc, &lead))
        pad = CGPoint(x: fontSize * 0.45, y: fontSize * 0.28)
        descent = desc
        radius = fontSize * 0.35
        size = CGSize(width: w + pad.x * 2, height: asc + desc + pad.y * 2)
    }

    /// Draws with the pill's top-left corner at (x, yTop), in top-left coordinates on a canvas `canvasH` tall.
    func draw(_ ctx: CGContext, x: CGFloat, yTop: CGFloat, canvasH: CGFloat) {
        let rect = CGRect(x: x, y: canvasH - yTop - size.height, width: size.width, height: size.height)
        ctx.setFillColor(CGColor(gray: 0, alpha: 0.62))
        ctx.addPath(CGPath(roundedRect: rect, cornerWidth: radius, cornerHeight: radius, transform: nil))
        ctx.fillPath()
        ctx.textPosition = CGPoint(x: rect.minX + pad.x, y: rect.minY + pad.y + descent)
        CTLineDraw(line, ctx)
    }
}

func clock(_ t: Double) -> String {
    let m = Int(t) / 60
    return String(format: "%02d:%04.1f", m, t - Double(m * 60))
}

// MARK: - frames: reference-video analysis

/// A tiny per-frame signature: a 32x18 luma grid plus a 16-bin luma histogram.
struct Signature {
    let t: Double
    let grid: [Float]
    let hist: [Float]
}

let GX = 32, GY = 18, SUB = 4

func signature(of pb: CVPixelBuffer, at t: Double) -> Signature {
    CVPixelBufferLockBaseAddress(pb, .readOnly)
    defer { CVPixelBufferUnlockBaseAddress(pb, .readOnly) }
    let w = CVPixelBufferGetWidth(pb), h = CVPixelBufferGetHeight(pb), bpr = CVPixelBufferGetBytesPerRow(pb)
    let base = CVPixelBufferGetBaseAddress(pb)!.assumingMemoryBound(to: UInt8.self)
    var grid = [Float](repeating: 0, count: GX * GY)
    var hist = [Float](repeating: 0, count: 16)
    let cols = GX * SUB, rows = GY * SUB
    for gy in 0..<GY {
        for gx in 0..<GX {
            var sum: Float = 0
            for sy in 0..<SUB {
                let py = min(h - 1, ((gy * SUB + sy) * h + h / 2) / rows)
                for sx in 0..<SUB {
                    let px = min(w - 1, ((gx * SUB + sx) * w + w / 2) / cols)
                    let p = base + py * bpr + px * 4  // BGRA
                    let l = (0.114 * Float(p[0]) + 0.587 * Float(p[1]) + 0.299 * Float(p[2])) / 255
                    sum += l
                    hist[min(15, Int(l * 16))] += 1
                }
            }
            grid[gy * GX + gx] = sum / Float(SUB * SUB)
        }
    }
    let n = Float(cols * rows)
    return Signature(t: t, grid: grid, hist: hist.map { $0 / n })
}

func median(_ xs: [Double]) -> Double {
    guard !xs.isEmpty else { return 0 }
    let s = xs.sorted()
    return s.count % 2 == 1 ? s[s.count / 2] : (s[s.count / 2 - 1] + s[s.count / 2]) / 2
}

/// Finds hard cuts. A cut is a frame-to-frame change that is a local peak, well above the local
/// median change (adaptive, so motion-heavy shots need a bigger spike) and backed by a histogram
/// shift. Per-frame differences stay small during fades and dissolves, so those don't fire.
func detectCuts(_ sigs: [Signature], fps: Double, duration: Double) -> [Double] {
    let n = sigs.count
    guard n > 2 else { return [] }
    var d = [Double](repeating: 0, count: n), hd = [Double](repeating: 0, count: n)
    for i in 1..<n {
        let a = sigs[i - 1], b = sigs[i]
        var s: Float = 0
        for k in 0..<a.grid.count { s += abs(a.grid[k] - b.grid[k]) }
        d[i] = Double(s) / Double(a.grid.count)
        var hs: Float = 0
        for k in 0..<16 { hs += abs(a.hist[k] - b.hist[k]) }
        hd[i] = Double(hs) / 2
    }
    let win = max(8, Int(fps * 0.75))
    var candidates: [(i: Int, score: Double)] = []
    for i in 1..<n {
        let lo = max(1, i - win), hi = min(n - 1, i + win)
        var neigh: [Double] = []
        for j in lo...hi where abs(j - i) > 1 { neigh.append(d[j]) }
        let thr = max(0.07, median(neigh) * 3.5 + 0.03)
        let peak = (max(1, i - 2)...min(n - 1, i + 2)).allSatisfy { j in
            j == i || d[j] < d[i] || (d[j] == d[i] && j > i)
        }
        if peak && d[i] > thr && (hd[i] > 0.12 || d[i] > 0.2) { candidates.append((i, d[i] / thr)) }
    }
    // Shots shorter than 0.4 s are almost always flashes or glitches: keep the stronger cut.
    let minShot = 0.4
    var cuts: [(t: Double, score: Double)] = []
    for c in candidates {
        let t = sigs[c.i].t
        if t < minShot * 0.5 { continue }
        if let last = cuts.last, t - last.t < minShot {
            if c.score > last.score { cuts[cuts.count - 1] = (t, c.score) }
        } else {
            cuts.append((t, c.score))
        }
    }
    if let last = cuts.last, duration - last.t < 0.25 { cuts.removeLast() }
    return cuts.map { $0.t }
}

func fourCC(_ v: UInt32) -> String {
    let chars = [24, 16, 8, 0].map { Character(UnicodeScalar(UInt8((v >> UInt32($0)) & 0xff))) }
    return String(chars).trimmingCharacters(in: .whitespaces)
}

func frames(_ args: Args) async {
    guard args.positional.count == 2 else { fail("usage: sbimg frames <video> <outdir> [--every 2.0] [--max 40] [--width 1280]") }
    let videoURL = expand(args.positional[0]), outDir = expand(args.positional[1])
    let every = max(0.2, args.double("every", 2.0))
    let maxFrames = max(1, Int(args.double("max", 40)))
    let width = max(64, args.double("width", 1280))
    guard FileManager.default.fileExists(atPath: videoURL.path) else { fail("no such file: \(videoURL.path)") }
    do {
        try FileManager.default.createDirectory(at: outDir, withIntermediateDirectories: true)
        let asset = AVURLAsset(url: videoURL)
        let duration = try await asset.load(.duration).seconds
        guard let track = try await asset.loadTracks(withMediaType: .video).first else { fail("no video track in \(videoURL.lastPathComponent)") }
        let natural = try await track.load(.naturalSize)
        let transform = try await track.load(.preferredTransform)
        let shown = natural.applying(transform)
        let fps = Double(try await track.load(.nominalFrameRate))

        var audio: Any = NSNull()
        if let a = try await asset.loadTracks(withMediaType: .audio).first {
            var info: [String: Any] = [:]
            if let desc = try await a.load(.formatDescriptions).first,
               let asbd = CMAudioFormatDescriptionGetStreamBasicDescription(desc)?.pointee {
                info = ["format": fourCC(asbd.mFormatID), "sample_rate": asbd.mSampleRate, "channels": Int(asbd.mChannelsPerFrame)]
            }
            audio = info
        }

        // 1. Decode every frame once and keep a tiny signature of each.
        let reader = try AVAssetReader(asset: asset)
        let output = AVAssetReaderTrackOutput(track: track, outputSettings: [kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA])
        reader.add(output)
        guard reader.startReading() else { throw reader.error ?? NSError(domain: "sbimg", code: 1) }
        var sigs: [Signature] = []
        while let sb = output.copyNextSampleBuffer() {
            guard let pb = CMSampleBufferGetImageBuffer(sb) else { continue }
            sigs.append(signature(of: pb, at: CMSampleBufferGetPresentationTimeStamp(sb).seconds))
        }
        if reader.status == .failed { throw reader.error ?? NSError(domain: "sbimg", code: 2) }
        sigs.sort { $0.t < $1.t }

        // 2. Cuts and shots.
        let cutTimes = detectCuts(sigs, fps: fps > 0 ? fps : 24, duration: duration)
        let bounds = [0.0] + cutTimes + [duration]
        var shots: [(n: Int, start: Double, end: Double)] = []
        for k in 0..<(bounds.count - 1) { shots.append((k + 1, bounds[k], bounds[k + 1])) }
        func shotAt(_ t: Double) -> Int { shots.last(where: { t >= $0.start })?.n ?? 1 }

        // 3. Pick export times: the middle of each shot first, then a frame every `every` seconds.
        var times: [Double] = []
        let mids = shots.map { ($0.start + $0.end) / 2 }
        if mids.count >= maxFrames {
            for j in 0..<maxFrames {
                let idx = maxFrames == 1 ? 0 : Int((Double(j) * Double(mids.count - 1) / Double(maxFrames - 1)).rounded())
                times.append(mids[idx])
            }
        } else {
            times = mids
            var t = every / 2
            while t < duration - 0.05 && times.count < maxFrames {
                if !times.contains(where: { abs($0 - t) < every * 0.5 }) { times.append(t) }
                t += every
            }
        }
        times = Array(Set(times.map { round3(min(max(0, $0), max(0, duration - 0.04))) })).sorted()

        // 4. Export the frames.
        let gen = AVAssetImageGenerator(asset: asset)
        gen.appliesPreferredTrackTransform = true
        gen.requestedTimeToleranceBefore = .zero
        gen.requestedTimeToleranceAfter = .zero
        gen.maximumSize = CGSize(width: width, height: width)
        var exported: [(file: String, t: Double, shot: Int, img: CGImage)] = []
        for (i, t) in times.enumerated() {
            let (img, actual) = try await gen.image(at: CMTime(seconds: t, preferredTimescale: 600))
            let at = actual.seconds.isFinite ? actual.seconds : t
            let name = String(format: "%03d_t%06.2f.jpg", i + 1, at)
            save(img, to: outDir.appendingPathComponent(name), jpeg: true)
            exported.append((name, at, shotAt(at), img))
        }

        // 5. Contact sheet, labelled with frame number, timestamp and shot.
        var contactPath: Any = NSNull()
        if let first = exported.first?.img {
            let count = exported.count
            let cols = count <= 4 ? count : (count <= 12 ? 4 : (count <= 30 ? 5 : 6))
            let rowsN = (count + cols - 1) / cols
            let gap = 8
            let tw = min(480, (2400 - gap * (cols + 1)) / cols)
            let th = Int(Double(tw) * Double(first.height) / Double(first.width))
            let W = cols * tw + gap * (cols + 1), H = rowsN * th + gap * (rowsN + 1)
            let ctx = canvas(W, H)
            ctx.setFillColor(CGColor(gray: 0.07, alpha: 1))
            ctx.fill(CGRect(x: 0, y: 0, width: W, height: H))
            let fs = max(11, CGFloat(tw) / 26)
            for (i, f) in exported.enumerated() {
                let x = gap + (i % cols) * (tw + gap), yTop = gap + (i / cols) * (th + gap)
                ctx.draw(f.img, in: CGRect(x: x, y: H - yTop - th, width: tw, height: th))
                Label("#\(i + 1)  \(clock(f.t))  S\(f.shot)", fontSize: fs)
                    .draw(ctx, x: CGFloat(x) + fs * 0.5, yTop: CGFloat(yTop) + fs * 0.5, canvasH: CGFloat(H))
            }
            let url = outDir.appendingPathComponent("contact.jpg")
            save(ctx.makeImage()!, to: url, jpeg: true)
            contactPath = url.path
        }

        let info: [String: Any] = [
            "video": videoURL.path,
            "outdir": outDir.path,
            "duration": num(duration),
            "fps": num(fps),
            "width": Int(abs(shown.width).rounded()),
            "height": Int(abs(shown.height).rounded()),
            "frames_analysed": sigs.count,
            "has_audio": !(audio is NSNull),
            "audio": audio,
            "cuts": cutTimes.map(num),
            "shots": shots.map { s -> [String: Any] in
                let mid = (s.start + s.end) / 2
                let rep = exported.filter { $0.shot == s.n }.min(by: { abs($0.t - mid) < abs($1.t - mid) })?.file
                return ["n": s.n, "start": num(s.start), "end": num(s.end), "duration": num(s.end - s.start),
                        "frame": rep.map { $0 as Any } ?? NSNull()]
            },
            "frames": exported.map { ["file": $0.file, "t": num($0.t), "shot": $0.shot] as [String: Any] },
            "contact": contactPath,
            "note": "Audio is not transcribed; has_audio only reports an audio track. Cuts are hard cuts; dissolves and fades are not split.",
        ]
        let data = try JSONSerialization.data(withJSONObject: info, options: [.prettyPrinted, .sortedKeys, .withoutEscapingSlashes])
        try data.write(to: outDir.appendingPathComponent("info.json"))
        emit(info)
    } catch {
        fail("frames failed: \(error.localizedDescription)")
    }
}

// MARK: - grid: measuring overlay

func grid(_ args: Args) {
    guard args.positional.count == 2 else { fail("usage: sbimg grid <image> <out.png> [--step 10]") }
    let step = args.double("step", 10)
    guard step >= 2 && step <= 50 else { fail("--step must be between 2 and 50 (percent)") }
    let img = loadImage(args.positional[0])
    let W = img.width, H = img.height
    let w = CGFloat(W), h = CGFloat(H)
    let ctx = canvas(W, H)
    ctx.draw(img, in: CGRect(x: 0, y: 0, width: w, height: h))
    let lw = max(1, min(w, h) / 900)
    let fs = max(11, min(w, h) / 55)

    // Lines: a dark under-stroke plus a white stroke, so they show on light and dark images. 50% is brighter.
    var marks: [Double] = []
    var p = step
    while p < 100 - 1e-9 { marks.append(p); p += step }
    for m in marks {
        let x = w * CGFloat(m) / 100, y = h - h * CGFloat(m) / 100
        let mid = abs(m - 50) < 1e-9
        for (color, width) in [(CGColor(gray: 0, alpha: 0.45), lw + 2), (CGColor(gray: 1, alpha: mid ? 0.9 : 0.6), mid ? lw * 1.8 : lw)] {
            ctx.setStrokeColor(color); ctx.setLineWidth(width)
            ctx.move(to: CGPoint(x: x, y: 0)); ctx.addLine(to: CGPoint(x: x, y: h))
            ctx.move(to: CGPoint(x: 0, y: y)); ctx.addLine(to: CGPoint(x: w, y: y))
            ctx.strokePath()
        }
    }
    // Labels: x% along the top edge, y% (measured from the top) down the left edge.
    for m in marks {
        let text = String(format: m.truncatingRemainder(dividingBy: 1) == 0 ? "%.0f%%" : "%.1f%%", m)
        let top = Label(text, fontSize: fs)
        let x = w * CGFloat(m) / 100
        let lx = x + top.size.width + 4 > w ? x - top.size.width - 3 : x + 3
        top.draw(ctx, x: lx, yTop: 3, canvasH: h)
        let left = Label(text, fontSize: fs)
        let yTop = h * CGFloat(m) / 100
        let ly = yTop + left.size.height + 4 > h ? yTop - left.size.height - 3 : yTop + 3
        left.draw(ctx, x: 3, yTop: ly, canvasH: h)
    }
    let out = expand(args.positional[1])
    save(ctx.makeImage()!, to: out, jpeg: false)
    emit(["out": out.path, "width": W, "height": H, "step_percent": step,
          "note": "Percentages are measured from the top-left corner. Convert to pixels with x*width/100 and y*height/100."])
}

// MARK: - crop: close inspection

func crop(_ args: Args) {
    guard args.positional.count == 2, let rectS = args.options["rect"] else {
        fail("usage: sbimg crop <image> <out.png> --rect x,y,w,h [--scale 2]   (rect in fractions 0-1, from the top-left)")
    }
    let r = rectS.split(separator: ",").compactMap { Double($0.trimmingCharacters(in: .whitespaces)) }
    guard r.count == 4, r.allSatisfy({ $0 >= 0 && $0 <= 1 }), r[2] > 0, r[3] > 0 else {
        fail("--rect needs four fractions 0-1: x,y,w,h (e.g. 0.4,0.1,0.2,0.3)")
    }
    let scale = args.double("scale", 2)
    guard scale > 0 && scale <= 8 else { fail("--scale must be between 0 and 8") }
    let img = loadImage(args.positional[0])
    let W = Double(img.width), H = Double(img.height)
    let px = Int((r[0] * W).rounded()), py = Int((r[1] * H).rounded())
    let pw = max(1, min(Int((r[2] * W).rounded()), img.width - px))
    let ph = max(1, min(Int((r[3] * H).rounded()), img.height - py))
    guard px < img.width, py < img.height,
          let part = img.cropping(to: CGRect(x: px, y: py, width: pw, height: ph)) else { fail("the rect falls outside the image") }
    let ow = max(1, Int((Double(pw) * scale).rounded())), oh = max(1, Int((Double(ph) * scale).rounded()))
    let ctx = canvas(ow, oh)
    ctx.draw(part, in: CGRect(x: 0, y: 0, width: ow, height: oh))
    let out = expand(args.positional[1])
    save(ctx.makeImage()!, to: out, jpeg: false)
    emit(["out": out.path, "width": ow, "height": oh, "scale": scale,
          "source_size": [img.width, img.height], "source_px": [px, py, pw, ph]])
}

// MARK: - info

func info(_ args: Args) {
    guard args.positional.count == 1 else { fail("usage: sbimg info <image>") }
    let img = loadImage(args.positional[0])
    let ratio = Double(img.width) / Double(img.height)
    let common: [(String, Double)] = [("1:1", 1), ("4:5", 0.8), ("5:4", 1.25), ("4:3", 4.0 / 3), ("3:4", 0.75), ("3:2", 1.5), ("2:3", 2.0 / 3),
                                      ("16:9", 16.0 / 9), ("9:16", 9.0 / 16), ("21:9", 21.0 / 9), ("2.39:1", 2.39)]
    let near = common.min(by: { abs($0.1 - ratio) < abs($1.1 - ratio) })!
    emit(["path": expand(args.positional[0]).path, "width": img.width, "height": img.height, "aspect": num(ratio),
          "aspect_label": abs(near.1 - ratio) / near.1 < 0.02 ? near.0 as Any : NSNull()])
}

// MARK: - area edits: maskinfo, mark, composite
//
// Higgsfield has no masked inpainting, so an area edit is: the edit model redraws the frame (or a crop of it)
// from the original plus a copy with the area tinted red, then `composite` keeps only the masked area of
// that redraw. Pixels outside the mask come from the original, so nothing outside the mark can change.

/// Canvas rows in memory run top to bottom, so (x, y) here is measured from the top-left corner.
func pixels(_ ctx: CGContext) -> (UnsafeMutablePointer<UInt8>, Int) {
    (ctx.data!.assumingMemoryBound(to: UInt8.self), ctx.bytesPerRow)
}

/// A mask as W×H weights 0…1: white (or opaque white) marks the area to change; black or transparent keeps.
func maskWeights(_ path: String, _ W: Int, _ H: Int) -> [Float] {
    let ctx = canvas(W, H)
    ctx.setFillColor(CGColor(gray: 0, alpha: 1))
    ctx.fill(CGRect(x: 0, y: 0, width: W, height: H))
    ctx.draw(loadImage(path), in: CGRect(x: 0, y: 0, width: W, height: H))
    let (d, bpr) = pixels(ctx)
    var m = [Float](repeating: 0, count: W * H)
    for y in 0..<H {
        let row = d + y * bpr
        for x in 0..<W {
            let p = row + x * 4
            m[y * W + x] = (0.299 * Float(p[0]) + 0.587 * Float(p[1]) + 0.114 * Float(p[2])) / 255
        }
    }
    return m
}

/// Three box-blur passes (close to a Gaussian): softens the mask edge so the paste has no hard seam.
func feather(_ a: inout [Float], _ W: Int, _ H: Int, _ r: Int) {
    guard r >= 1 else { return }
    var t = [Float](repeating: 0, count: W * H)
    let k = 1 / Float(2 * r + 1)
    for _ in 0..<3 {
        for y in 0..<H {
            let o = y * W
            var acc: Float = 0
            for i in -r...r { acc += a[o + min(W - 1, max(0, i))] }
            for x in 0..<W {
                t[o + x] = acc * k
                acc += a[o + min(W - 1, x + r + 1)] - a[o + max(0, x - r)]
            }
        }
        for x in 0..<W {
            var acc: Float = 0
            for i in -r...r { acc += t[min(H - 1, max(0, i)) * W + x] }
            for y in 0..<H {
                a[y * W + x] = acc * k
                acc += t[min(H - 1, y + r + 1) * W + x] - t[max(0, y - r) * W + x]
            }
        }
    }
}

/// --rect x,y,w,h in fractions of the image, from the top-left; nil when absent.
func rectOption(_ args: Args) -> [Double]? {
    guard let s = args.options["rect"] else { return nil }
    let r = s.split(separator: ",").compactMap { Double($0.trimmingCharacters(in: .whitespaces)) }
    guard r.count == 4, r.allSatisfy({ $0 >= 0 && $0 <= 1 }), r[2] > 0, r[3] > 0, r[0] + r[2] <= 1.0001, r[1] + r[3] <= 1.0001 else {
        fail("--rect needs four fractions 0-1: x,y,w,h inside the image (e.g. 0.4,0.1,0.2,0.3)")
    }
    return r
}

func pxRect(_ r: [Double], _ W: Int, _ H: Int) -> (x: Int, y: Int, w: Int, h: Int) {
    let x = min(W - 1, Int((r[0] * Double(W)).rounded())), y = min(H - 1, Int((r[1] * Double(H)).rounded()))
    return (x, y, max(1, min(W - x, Int((r[2] * Double(W)).rounded()))), max(1, min(H - y, Int((r[3] * Double(H)).rounded()))))
}

let ASPECTS: [(String, Double)] = [("1:1", 1), ("4:5", 0.8), ("5:4", 1.25), ("4:3", 4.0 / 3), ("3:4", 0.75), ("3:2", 1.5),
                                   ("2:3", 2.0 / 3), ("16:9", 16.0 / 9), ("9:16", 9.0 / 16), ("21:9", 21.0 / 9)]

func maskinfo(_ args: Args) {
    guard args.positional.count == 1 else { fail("usage: sbimg maskinfo <mask.png> [--pad 0.12]") }
    let img = loadImage(args.positional[0])
    let W = img.width, H = img.height
    let m = maskWeights(args.positional[0], W, H)
    var x0 = W, y0 = H, x1 = -1, y1 = -1, n = 0
    for y in 0..<H {
        for x in 0..<W where m[y * W + x] > 0.5 {
            n += 1; x0 = min(x0, x); x1 = max(x1, x); y0 = min(y0, y); y1 = max(y1, y)
        }
    }
    guard n > 0 else { fail("the mask is empty: nothing is marked") }
    let bw = Double(x1 - x0 + 1), bh = Double(y1 - y0 + 1)
    // Crop for small areas: the marked box plus context, grown to the nearest standard aspect ratio so the
    // edit model returns exactly that shape, then kept inside the frame.
    let pad = args.double("pad", 0.12)
    var cw = bw + 2 * max(bw * pad, Double(W) * 0.04), ch = bh + 2 * max(bh * pad, Double(H) * 0.04)
    cw = max(cw, Double(W) * 0.3); ch = max(ch, Double(H) * 0.3)  // enough surroundings to match light and grain
    let ratio = cw / ch
    let asp = ASPECTS.min(by: { abs(log($0.1 / ratio)) < abs(log($1.1 / ratio)) })!
    if asp.1 > ratio { cw = ch * asp.1 } else { ch = cw / asp.1 }
    if cw > Double(W) { ch *= Double(W) / cw; cw = Double(W) }
    if ch > Double(H) { cw *= Double(H) / ch; ch = Double(H) }
    let cx = min(max(0, (Double(x0) + bw / 2) - cw / 2), Double(W) - cw)
    let cy = min(max(0, (Double(y0) + bh / 2) - ch / 2), Double(H) - ch)
    let area = Double(n) / Double(W * H)
    let cropShare = cw * ch / Double(W * H)
    let fits = cw >= bw && ch >= bh
    let suggest = fits && area < 0.12 && cropShare < 0.5 ? "crop" : "full"
    let scale = min(4, max(1, 2048 / max(cw, ch)))
    emit(["width": W, "height": H, "area": num(area),
          "bbox": [num(Double(x0) / Double(W)), num(Double(y0) / Double(H)), num(bw / Double(W)), num(bh / Double(H))],
          "crop": [num(cx / Double(W)), num(cy / Double(H)), num(cw / Double(W)), num(ch / Double(H))],
          "crop_aspect": asp.0, "crop_scale": num(scale), "suggest": suggest,
          "note": "suggest=crop: edit a crop (sbimg crop --rect <crop> --scale <crop_scale>; sbimg mark --rect <crop>) at aspect <crop_aspect>, then composite --rect <crop>. suggest=full: edit the whole frame, then composite without --rect."])
}

func mark(_ args: Args) {
    guard args.positional.count == 3 else { fail("usage: sbimg mark <image> <mask.png> <out.png> [--rect x,y,w,h]") }
    let img = loadImage(args.positional[0])
    let W = img.width, H = img.height
    let m = maskWeights(args.positional[1], W, H)
    let ctx = canvas(W, H)
    ctx.draw(img, in: CGRect(x: 0, y: 0, width: W, height: H))
    let (d, bpr) = pixels(ctx)
    let edge = max(2, min(W, H) / 400)
    func inside(_ x: Int, _ y: Int) -> Bool { x >= 0 && y >= 0 && x < W && y < H && m[y * W + x] > 0.5 }
    for y in 0..<H {
        for x in 0..<W where m[y * W + x] > 0.5 {
            let p = d + y * bpr + x * 4
            let rim = !inside(x - edge, y) || !inside(x + edge, y) || !inside(x, y - edge) || !inside(x, y + edge)
            let a: Float = rim ? 1 : 0.45  // a solid red outline around a see-through red tint
            p[0] = UInt8(Float(p[0]) * (1 - a) + 255 * a)
            p[1] = UInt8(Float(p[1]) * (1 - a) + 32 * a)
            p[2] = UInt8(Float(p[2]) * (1 - a) + 32 * a)
        }
    }
    var out = ctx.makeImage()!
    if let r = rectOption(args) {
        let c = pxRect(r, W, H)
        guard let part = out.cropping(to: CGRect(x: c.x, y: c.y, width: c.w, height: c.h)) else { fail("the rect falls outside the image") }
        out = part
    }
    let url = expand(args.positional[2])
    save(out, to: url, jpeg: false)
    emit(["out": url.path, "width": out.width, "height": out.height])
}

func composite(_ args: Args) {
    guard args.positional.count == 4 else {
        fail("usage: sbimg composite <base> <edit> <mask.png> <out.png> [--rect x,y,w,h] [--feather px]")
    }
    let base = loadImage(args.positional[0]), edit = loadImage(args.positional[1])
    let W = base.width, H = base.height
    let r = rectOption(args).map { pxRect($0, W, H) } ?? (x: 0, y: 0, w: W, h: H)
    // The redraw, stretched onto its rect (edit models keep the content's layout when they change the pixel size).
    let ce = canvas(W, H)
    ce.draw(base, in: CGRect(x: 0, y: 0, width: W, height: H))
    ce.draw(edit, in: CGRect(x: r.x, y: H - r.y - r.h, width: r.w, height: r.h))
    let cb = canvas(W, H)
    cb.draw(base, in: CGRect(x: 0, y: 0, width: W, height: H))
    var m = maskWeights(args.positional[2], W, H)
    for y in 0..<H { for x in 0..<W where x < r.x || x >= r.x + r.w || y < r.y || y >= r.y + r.h { m[y * W + x] = 0 } }
    let radius = Int(args.double("feather", Double(max(3, max(W, H) / 400))))
    feather(&m, W, H, radius)
    let (b, bpr) = pixels(cb), (e, epr) = pixels(ce)
    var ring = 0.0, ringN = 0, outside = 0.0, outN = 0, inside = 0.0, inN = 0, changed = 0
    for y in 0..<H {
        for x in 0..<W {
            let w = m[y * W + x], pb = b + y * bpr + x * 4, pe = e + y * epr + x * 4
            let lb = 0.299 * Double(pb[0]) + 0.587 * Double(pb[1]) + 0.114 * Double(pb[2])
            let le = 0.299 * Double(pe[0]) + 0.587 * Double(pe[1]) + 0.114 * Double(pe[2])
            let diff = abs(lb - le) / 255
            let inRect = x >= r.x && x < r.x + r.w && y >= r.y && y < r.y + r.h
            if w > 0.99 { inside += diff; inN += 1 } else if w > 0.01 { ring += diff; ringN += 1 } else if inRect { outside += diff; outN += 1 }
            guard w > 0.002 else { continue }
            changed += 1
            for c in 0..<3 { pb[c] = UInt8((Float(pb[c]) * (1 - w) + Float(pe[c]) * w).rounded()) }
        }
    }
    let ringD = ringN > 0 ? ring / Double(ringN) : 0
    let url = expand(args.positional[3])
    save(cb.makeImage()!, to: url, jpeg: false)
    emit(["out": url.path, "width": W, "height": H, "feather_px": radius,
          "changed_share": num(Double(changed) / Double(W * H)),
          "inside_change": num(inN > 0 ? inside / Double(inN) : 0),
          "edge_diff": num(ringD), "outside_drift": num(outN > 0 ? outside / Double(outN) : 0),
          "seam_risk": ringD < 0.06 ? "low" : ringD < 0.12 ? "medium" : "high",
          "note": "Only pixels inside the feathered mask changed. inside_change near 0 means the model changed nothing there. seam_risk high: the redraw moved or recoloured the frame around the mark; check the edge (sbimg crop) and retry, or use crop mode."])
}

// MARK: - main

@main
struct SBImg {
    static func main() async {
        var argv = Array(CommandLine.arguments.dropFirst())
        guard let cmd = argv.first else {
            fail("usage: sbimg frames|grid|crop|info|maskinfo|mark|composite … (see tools/README.md)")
        }
        argv.removeFirst()
        let args = Args(argv)
        switch cmd {
        case "frames": await frames(args)
        case "grid": grid(args)
        case "crop": crop(args)
        case "info": info(args)
        case "maskinfo": maskinfo(args)
        case "mark": mark(args)
        case "composite": composite(args)
        default: fail("unknown command \(cmd); use frames, grid, crop, info, maskinfo, mark or composite")
        }
    }
}
