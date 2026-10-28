#!/usr/bin/env bash
# codep installer for macOS
# https://github.com/heliopais/codep

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_NAME="${CODEP_APP_NAME:-codep}"
DEST_DIR="${CODEP_DEST_DIR:-$HOME/Applications}"
BIN_DIR="${CODEP_BIN_DIR:-$HOME/.local/bin}"
EDITOR_NAME="${CODEP_EDITOR:-Visual Studio Code}"

echo "==> Installing $APP_NAME to $DEST_DIR..."

# Check macOS requirements
if [[ "$(uname -s)" != "Darwin" ]]; then
    echo "Error: codep is only supported on macOS." >&2
    exit 1
fi

if ! command -v osacompile >/dev/null 2>&1; then
    echo "Error: osacompile not found (required to build macOS applet)." >&2
    exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
    echo "Error: python3 not found." >&2
    exit 1
fi

mkdir -p "$DEST_DIR"
TARGET_APP="$DEST_DIR/$APP_NAME.app"

# Compile AppleScript launcher
echo "==> Compiling native launcher with Cocoa focus integration..."
osacompile -o "$TARGET_APP" "$SCRIPT_DIR/src/launcher.applescript"

# Bundle internal resolver script
echo "==> Bundling smart path resolver..."
mkdir -p "$TARGET_APP/Contents/Resources"
cp "$SCRIPT_DIR/src/resolver.py" "$TARGET_APP/Contents/Resources/resolver.py"
chmod +x "$TARGET_APP/Contents/Resources/resolver.py"

# Copy editor icon if available
echo "==> Configuring icon..."
ICON_FOUND=false
POSSIBLE_ICONS=(
    "/Applications/$EDITOR_NAME.app/Contents/Resources/Code.icns"
    "/Applications/$EDITOR_NAME.app/Contents/Resources/$EDITOR_NAME.icns"
    "/Applications/Visual Studio Code.app/Contents/Resources/Code.icns"
    "/Applications/Cursor.app/Contents/Resources/Cursor.icns"
    "/Applications/Zed.app/Contents/Resources/Zed.icns"
)

for icns in "${POSSIBLE_ICONS[@]}"; do
    if [ -f "$icns" ]; then
        cp "$icns" "$TARGET_APP/Contents/Resources/applet.icns"
        ICON_FOUND=true
        echo "    Using icon from: $icns"
        break
    fi
done

if [ "$ICON_FOUND" = false ]; then
    echo "    (No custom icon found; using default system applet icon)"
fi

# Touch to trigger Spotlight re-indexing
touch "$TARGET_APP"

# Optionally install CLI wrapper
if [ -d "$BIN_DIR" ]; then
    echo "==> Installing CLI wrapper to $BIN_DIR/codep..."
    ln -sf "$SCRIPT_DIR/bin/codep" "$BIN_DIR/codep"
    chmod +x "$BIN_DIR/codep"
else
    echo "==> Note: $BIN_DIR does not exist. CLI wrapper not linked."
    echo "    To use from terminal, add bin/codep to your PATH or symlink to a bin directory."
fi

echo ""
echo "=========================================================="
echo "  codep installed successfully!"
echo "=========================================================="
echo "  * Hit Cmd + Space, type '$APP_NAME', and press Return."
echo "  * Type your project name (e.g. 'backend', 'api v2') and press Return."
echo "  * Or run in terminal: codep <query>"
echo "=========================================================="
