#!/bin/sh
# Builds bin/sbimg from tools/sbimg.swift with the Command Line Tools (no Xcode, no ffmpeg).
#   sh ~/.claude/skills/shotbird/tools/build.sh
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="$HERE/../bin/sbimg"
mkdir -p "$HERE/../bin"
if [ "$(uname)" != "Darwin" ]; then  # Linux: bin/sbimg is a small launcher for tools/sbimg.py (Pillow + numpy + ffmpeg)
  cat >"$OUT" <<'EOF'
#!/bin/sh
exec "${SBIMG_PYTHON:-/usr/bin/python3}" "$(dirname "$0")/../tools/sbimg.py" "$@"
EOF
  chmod +x "$OUT"
  echo "$(cd "$(dirname "$OUT")" && pwd)/sbimg (Linux launcher)"
  exit 0
fi
swiftc -O -parse-as-library -swift-version 5 \
  -sdk /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk \
  "$HERE/sbimg.swift" -o "$OUT" \
  -framework AVFoundation -framework CoreMedia -framework CoreVideo -framework CoreGraphics \
  -framework CoreText -framework ImageIO -framework UniformTypeIdentifiers
echo "$(cd "$(dirname "$OUT")" && pwd)/sbimg"
