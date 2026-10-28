#!/bin/sh
# Build ~/Applications/Shotbird.app (native WKWebView window) from main.swift, in place, so the Dock pin
# and the login agent keep pointing at the same path.  Usage: sh ~/.claude/skills/shotbird/app/build.sh
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
DEST="$HOME/Applications/Shotbird.app"
STAGE="$HERE/build/Shotbird.app"
SDK=/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk
ARCH="$(uname -m)"

rm -rf "$HERE/build"
mkdir -p "$STAGE/Contents/MacOS" "$STAGE/Contents/Resources"
swiftc -O -swift-version 5 -sdk "$SDK" -target "$ARCH-apple-macos13.0" \
  -framework AppKit -framework WebKit "$HERE/main.swift" -o "$STAGE/Contents/MacOS/Shotbird"
cp "$HERE/Shotbird.icns" "$STAGE/Contents/Resources/Shotbird.icns"
cp "$HERE/titlebar-logo-dark.png" "$HERE/titlebar-logo-light.png" "$STAGE/Contents/Resources/"
cat >"$STAGE/Contents/Info.plist" <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>CFBundleIdentifier</key><string>com.makani.shotbird</string>
	<key>CFBundleName</key><string>Shotbird</string>
	<key>CFBundleDisplayName</key><string>Shotbird</string>
	<key>CFBundleExecutable</key><string>Shotbird</string>
	<key>CFBundleIconFile</key><string>Shotbird</string>
	<key>CFBundlePackageType</key><string>APPL</string>
	<key>CFBundleShortVersionString</key><string>2.0</string>
	<key>CFBundleVersion</key><string>2</string>
	<key>LSMinimumSystemVersion</key><string>13.0</string>
	<key>NSHighResolutionCapable</key><true/>
	<key>NSPrincipalClass</key><string>NSApplication</string>
	<key>NSAppTransportSecurity</key><dict><key>NSAllowsLocalNetworking</key><true/></dict>
</dict>
</plist>
EOF
plutil -lint "$STAGE/Contents/Info.plist" >/dev/null

mkdir -p "$DEST"
rm -rf "$DEST/Contents"
cp -R "$STAGE/Contents" "$DEST/Contents"
codesign --force --deep -s - "$DEST"
touch "$DEST"
/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -f "$DEST"
rm -rf "$HERE/build"
echo "Built $DEST"
