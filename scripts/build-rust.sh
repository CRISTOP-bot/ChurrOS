#!/usr/bin/env bash
#
# build-rust.sh — Compila las apps ChurrOS en Rust y despliega los binarios
# en archiso/airootfs/usr/bin/ (donde los wrappers python originales vivían).
#
# Cada crate del workspace produce un binario con el mismo nombre que el
# wrapper que reemplaza (p.ej. churros-welcome). Los assets se siguen
# leyendo desde /usr/share/churros/<app>/ en runtime.
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
RUST_DIR="$PROJECT_DIR/rust"
BIN_DIR="$PROJECT_DIR/archiso/airootfs/usr/bin"

if [ ! -f "$RUST_DIR/Cargo.toml" ]; then
    echo "  [rust] no hay workspace en $RUST_DIR — saltando"
    exit 0
fi

echo "[rust] Compilando apps Rust (release)..."

cargo build --release --manifest-path "$RUST_DIR/Cargo.toml"

# Desplegar cada binario del workspace en airootfs/usr/bin/
# SOLO los crates marcados con [package.metadata.churros] deploy = true
# (un crate sin la marca está en port activo y aún no reemplaza al Python).
for crate_dir in "$RUST_DIR"/*/; do
    [ -f "$crate_dir/Cargo.toml" ] || continue
    grep -q '^deploy = true$' "$crate_dir/Cargo.toml" || continue
    # El nombre del binario es el "name" del package (p.ej. el crate
    # preferences/ produce churros-settings), no el del directorio.
    crate_name=$(sed -n 's/^name = "\(.*\)"/\1/p' "$crate_dir/Cargo.toml" | head -1)
    [ -n "$crate_name" ] || continue
    binary="$RUST_DIR/target/release/$crate_name"
    if [ -x "$binary" ]; then
        echo "  [rust] $crate_name -> $BIN_DIR/$crate_name"
        cp "$binary" "$BIN_DIR/$crate_name"
    fi
done

echo "[rust] Apps Rust desplegadas."
