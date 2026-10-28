#!/usr/bin/env bash
# codep uninstaller for macOS
# https://github.com/heliopais/codep

set -euo pipefail

APP_NAME="${CODEP_APP_NAME:-codep}"
DEST_DIR="${CODEP_DEST_DIR:-$HOME/Applications}"
BIN_DIR="${CODEP_BIN_DIR:-$HOME/.local/bin}"

echo "==> Uninstalling $APP_NAME..."

if [ -d "$DEST_DIR/$APP_NAME.app" ]; then
    rm -rf "$DEST_DIR/$APP_NAME.app"
    echo "  Removed $DEST_DIR/$APP_NAME.app"
fi

# Also clean up legacy Code Project.app if present
if [ -d "$DEST_DIR/Code Project.app" ]; then
    rm -rf "$DEST_DIR/Code Project.app"
    echo "  Removed legacy $DEST_DIR/Code Project.app"
fi

if [ -L "$BIN_DIR/codep" ] || [ -f "$BIN_DIR/codep" ]; then
    rm -f "$BIN_DIR/codep"
    echo "  Removed CLI symlink at $BIN_DIR/codep"
fi

echo "codep uninstalled."
