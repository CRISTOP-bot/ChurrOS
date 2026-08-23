#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
THEME_DIR="$SCRIPT_DIR/../branding/grub-theme"

FONTS_SRC="/usr/share/fonts/TTF/DejaVuSans.ttf"
FONTS_BOLD_SRC="/usr/share/fonts/TTF/DejaVuSans-Bold.ttf"
BG_SRC="$SCRIPT_DIR/../archiso/airootfs/usr/share/churros/wallpapers/ChurrOSDarkMinimal.png"

echo "======================================"
echo "  Building GRUB theme assets"
echo "======================================"

mkdir -p "$THEME_DIR"

if command -v grub-mkfont &>/dev/null; then
    if [ ! -f "$THEME_DIR/DejaVu Sans 16.pf2" ]; then
        echo "  Generating DejaVu Sans 16.pf2..."
        grub-mkfont -o "$THEME_DIR/DejaVu Sans 16.pf2" -s 16 "$FONTS_SRC"
    fi
    if [ ! -f "$THEME_DIR/DejaVu Sans Bold 16.pf2" ]; then
        echo "  Generating DejaVu Sans Bold 16.pf2..."
        grub-mkfont -o "$THEME_DIR/DejaVu Sans Bold 16.pf2" -s 16 "$FONTS_BOLD_SRC"
    fi
    if [ ! -f "$THEME_DIR/DejaVu Sans Bold 22.pf2" ]; then
        echo "  Generating DejaVu Sans Bold 22.pf2..."
        grub-mkfont -o "$THEME_DIR/DejaVu Sans Bold 22.pf2" -s 22 "$FONTS_BOLD_SRC"
    fi
else
    echo "  grub-mkfont not found — keeping existing .pf2 fonts (if any)."
fi

if [ ! -f "$THEME_DIR/background.png" ] && [ -f "$BG_SRC" ]; then
    echo "  Copying background from wallpapers..."
    cp "$BG_SRC" "$THEME_DIR/background.png"
fi

# GRUB styled boxes resolve select_*.png → select_c.png (and optional edges).
if [ -f "$THEME_DIR/select.png" ] && [ ! -f "$THEME_DIR/select_c.png" ]; then
    echo "  Deriving select_c.png from select.png..."
    cp "$THEME_DIR/select.png" "$THEME_DIR/select_c.png"
fi

echo
echo "======================================"
echo "  GRUB theme assets ready."
echo "======================================"
ls -la "$THEME_DIR"
