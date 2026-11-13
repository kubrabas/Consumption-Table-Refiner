#!/bin/bash
# Installs "Consumption Table Refiner.app" into the Applications folder, so that it starts like any other app
# (Spotlight: command + space, then type "Consumption").
# Run it once after cloning (double-click in Finder), and again if this folder is moved.
# The app runs the code of this folder, so after a git pull it uses the new version without a new installation.
#
# The app is an AppleScript applet (osacompile, part of macOS): its program runs natively on Apple silicon and Intel
# Macs. It only starts macos/launch.sh.

set -euo pipefail

APP_NAME="Consumption Table Refiner"
BUNDLE_ID="io.github.kubrabas.ConsumptionTableRefiner"
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -w /Applications ]; then
  TARGET_DIR=/Applications
else
  TARGET_DIR="$HOME/Applications"   # no write access to /Applications (e.g. managed Macs)
fi
APP_DIR="$TARGET_DIR/$APP_NAME.app"

# path of the launcher as an AppleScript string (escape \ and ")
launcher="$REPO_DIR/macos/launch.sh"
launcher="${launcher//\\/\\\\}"
launcher="${launcher//\"/\\\"}"

chmod +x "$REPO_DIR/macos/launch.sh"
mkdir -p "$TARGET_DIR"
rm -rf "$APP_DIR"
# errors of launch.sh are shown by launch.sh itself, so the applet ignores them
/usr/bin/osacompile -o "$APP_DIR" \
  -e 'try' \
  -e "do shell script quoted form of \"$launcher\"" \
  -e 'end try'

# name, icon, no Dock icon while it starts
plist="$APP_DIR/Contents/Info.plist"
/usr/bin/plutil -replace CFBundleIdentifier -string "$BUNDLE_ID" "$plist"
/usr/bin/plutil -replace CFBundleIconFile -string "applet" "$plist"
/usr/bin/plutil -remove CFBundleIconName "$plist" >/dev/null 2>&1 || true   # else the default icon of Assets.car wins
/usr/bin/plutil -replace LSUIElement -bool true "$plist"
rm -f "$APP_DIR/Contents/Resources/Assets.car"
cp "$REPO_DIR/macos/AppIcon.icns" "$APP_DIR/Contents/Resources/applet.icns"
/usr/bin/codesign --force --deep --sign - "$APP_DIR" 2>/dev/null   # sign again (local signature) after the changes

touch "$APP_DIR"
/usr/bin/mdimport "$APP_DIR" >/dev/null 2>&1 || true   # make Spotlight find it right away

echo "Installed: $APP_DIR"
echo "Start it with command + space, then type \"Consumption\". You can close this window."
