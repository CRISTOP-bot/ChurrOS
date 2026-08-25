#!/usr/bin/env bash
set -e

USERNAME=$(getent passwd | awk -F: '$3>=1000 && $3<65534 {print $1}' | grep -v churros | head -1)

if [ -z "$USERNAME" ]; then
    echo "ERROR: No regular user found on target system!" >&2
    exit 1
fi

# Post-instalacion: quitar churros-welcome y churros-control-center del autostart.
# Calamares ya se borra via shellprocess-cleanup.conf.
NIRI_CONF="/home/$USERNAME/.config/niri/config.kdl"

if [ -f "$NIRI_CONF" ]; then

    sed -i '/spawn-at-startup "churros-welcome"/d' "$NIRI_CONF" 2>/dev/null || true

fi

chown -R "$USERNAME:$USERNAME" "/home/$USERNAME/.config" 2>/dev/null || true

EDITION="niri"
if [ -f /etc/churros-edition ]; then
    EDITION="$(tr -d '[:space:]' < /etc/churros-edition | tr '[:upper:]' '[:lower:]')"
fi

SESSION_CMD="/usr/bin/niri"
if [ "$EDITION" = "xfce" ] || [ -x /usr/bin/startxfce4 -a ! -x /usr/bin/niri ]; then
    SESSION_CMD="/usr/bin/startxfce4"
fi

cat > /etc/greetd/config.toml << EOF
[terminal]
vt = 1

[default_session]
command = "$SESSION_CMD"
user = "$USERNAME"
EOF

echo "greetd config written for user: $USERNAME ($SESSION_CMD)"
