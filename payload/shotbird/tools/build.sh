#!/bin/sh
# Builds bin/sbimg from tools/sbimg.swift with the Command Line Tools (no Xcode, no ffmpeg).
#   sh ~/.claude/skills/shotbird/tools/build.sh
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="$HERE/../bin/sbimg"
mkdir -p "$HERE/../bin"
swiftc -O -parse-as-library -swift-version 5 \
  -sdk /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk \
  "$HERE/sbimg.swift" -o "$OUT" \
  -framework AVFoundation -framework CoreMedia -framework CoreVideo -framework CoreGraphics \
  -framework CoreText -framework ImageIO -framework UniformTypeIdentifiers
echo "$(cd "$(dirname "$OUT")" && pwd)/sbimg"
