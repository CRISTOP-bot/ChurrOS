#!/usr/bin/env bash
#
# build-i18n.sh — Compila archivos .po -> .mo
#
# Recorre po/*.po y genera los .mo correspondientes en
# archiso/airootfs/usr/share/locale/<lang>/LC_MESSAGES/churros.mo
#

set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

cd "$ROOT"

LOCALE_BASE="archiso/airootfs/usr/share/locale"

for po in po/*.po; do

    lang=$(basename "$po" .po)

    out_dir="$LOCALE_BASE/$lang/LC_MESSAGES"

    mkdir -p "$out_dir"

    msgfmt -o "$out_dir/churros.mo" "$po"

    echo "  Compiled $po -> $out_dir/churros.mo"

done

echo "i18n: .mo files compiled."
