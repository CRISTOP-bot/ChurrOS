#!/usr/bin/env bash
set -e

echo "==> Configuring desktop..."

# Copiar configuración por defecto
cp -r /etc/skel/.config /home/churros/

# Permisos
chown -R churros:churros /home/churros/.config

# Regenerar cache de iconos GTK para que encuentre los iconos Churros
if command -v gtk-update-icon-cache >/dev/null 2>&1; then

    for theme_dir in /usr/share/icons/hicolor /usr/share/icons/Adwaita; do

        if [ -d "$theme_dir" ]; then

            gtk-update-icon-cache -f -t "$theme_dir" 2>/dev/null || true

        fi

    done

fi

echo "✓ Desktop configured."