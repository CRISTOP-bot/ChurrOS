#!/usr/bin/env bash
set -e

USERNAME=$(getent passwd | awk -F: '$3>=1000 && $3<65534 {print $1}' | grep -v churros | head -1)

if [ -z "$USERNAME" ]; then
    echo "ERROR: No regular user found on target system!" >&2
    exit 1
fi

# Detectar si el usuario activó autologin en Calamares
AUTOLOGIN=0
for logfile in /var/log/Calamares.log /root/.cache/calamares/session.log /home/churros/.cache/calamares/session.log; do
    if [ -f "$logfile" ]; then
        last_autologin_user=$(grep -oE 'autoLoginUser[": =]+"[^"]*"' "$logfile" 2>/dev/null | tail -1 | sed -E 's/.*"([^"]+)"/\1/' || true)
        last_do_autologin=$(grep -oE 'doAutoLogin[": =]+(true|false)' "$logfile" 2>/dev/null | tail -1 | sed -E 's/.*(true|false)/\1/' || true)
        
        if [ "$last_do_autologin" = "true" ] || [ "$last_autologin_user" = "$USERNAME" ]; then
            AUTOLOGIN=1
        elif [ "$last_do_autologin" = "false" ] || [ -z "$last_autologin_user" ]; then
            AUTOLOGIN=0
        fi
    fi
done

EDITION="niri"
if [ -f /etc/churros-edition ]; then
    EDITION="$(tr -d '[:space:]' < /etc/churros-edition | tr '[:upper:]' '[:lower:]')"
fi

SESSION_CMD="/usr/bin/niri"
if [ "$EDITION" = "xfce" ] || [ -x /usr/bin/startxfce4 -a ! -x /usr/bin/niri ]; then
    SESSION_CMD="/usr/bin/startxfce4"
fi

# Eliminar autostart de churros-welcome en el usuario instalado
NIRI_CONF="/home/$USERNAME/.config/niri/config.kdl"
if [ -f "$NIRI_CONF" ]; then
    sed -i '/spawn-at-startup "churros-welcome"/d' "$NIRI_CONF" 2>/dev/null || true
fi
rm -f "/home/$USERNAME/.config/autostart/churros-welcome.desktop" 2>/dev/null || true
rm -f /etc/skel/.config/autostart/churros-welcome.desktop 2>/dev/null || true
chown -R "$USERNAME:$USERNAME" "/home/$USERNAME/.config" 2>/dev/null || true

# Configurar greetd según la elección del usuario en Calamares
mkdir -p /etc/greetd
if [ "$AUTOLOGIN" -eq 1 ]; then
    cat > /etc/greetd/config.toml << EOF
[terminal]
vt = 1

[initial_session]
command = "$SESSION_CMD"
user = "$USERNAME"

[default_session]
command = "cage -s -- regreet"
user = "greeter"
EOF
    echo "greetd: Autologin habilitado para $USERNAME ($SESSION_CMD)"
else
    cat > /etc/greetd/config.toml << EOF
[terminal]
vt = 1

[default_session]
command = "cage -s -- regreet"
user = "greeter"
EOF
    echo "greetd: Pantalla de inicio de sesión ReGreet habilitada (autologin desactivado)"
fi
