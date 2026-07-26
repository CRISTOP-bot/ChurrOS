# Popups

Este documento describe el sistema de popups de ChurrOS: pequeñas ventanas que se muestran al interactuar con los iconos de Waybar o con atajos de teclado.

Los popups son componentes individuales del escritorio: audio, batería, bluetooth, brillo, red y energía. Cada uno es un proceso GTK4 independiente que se abre, muestra su contenido y se cierra solo.

---

# Overview

Los popups viven en:

```text
archiso/airootfs/usr/share/churros/popups/
```

Estructura:

```text
popups/
├── common/               # Código compartido
│   ├── popup.py          # PopupWindow (clase base)
│   ├── main.py           # App de prueba
│   ├── style.css
│   └── widgets/
│       ├── button.py
│       ├── card.py
│       ├── header.py
│       ├── icon_button.py
│       └── separator.py
├── audio/                # Popup de audio (volumen, mute, dispositivo)
├── battery/              # Popup de batería
├── bluetooth/            # Popup de Bluetooth
├── brightness/           # Popup de brillo
├── network/              # Popup de red (Wi-Fi + Ethernet)
└── power/                # Popup de energía
```

Cada popup individual tiene esta forma:

```text
<popup>/
├── main.py               # Entry point (Gtk.Application)
├── window.py             # <Popup>Window (extiende PopupWindow)
├── style.css             # Estilos específicos
└── widgets/              # Widgets del popup
```

El launcher está en `/usr/bin/churros-popup` (script bash) y su lógica de toggle/reemplazo vive en él, no en un módulo Python separado.

---

# How It Works

## Architecture

Cada popup es un proceso Python GTK4 independiente. El launcher `/usr/bin/churros-popup` (script bash) es el punto de entrada único desde Waybar o desde el teclado.

Flujo:

1. Waybar o niri ejecuta `churros-popup <nombre>` cuando se hace clic en un módulo o se pulsa un atajo.
2. El script revisa `/tmp/churros/popup.pid` y `/tmp/churros/popup.name` para saber qué popup está activo.
3. Si no hay popup → lanza el solicitado (`python3 /usr/share/churros/popups/<name>/main.py`).
4. Si el popup activo es el mismo → lo mata (toggle off).
5. Si hay otro popup abierto → lo mata y abre el nuevo.

## Estado en disco

```text
/tmp/churros/popup.pid     # PID del proceso del popup actual
/tmp/churros/popup.name    # Nombre del popup activo
```

El script valida con `kill -0 $pid` que el proceso siga vivo; si murió pero los archivos quedaron, los limpia automáticamente antes de lanzar uno nuevo.

## churros-popup

`/usr/bin/churros-popup` (bash, ~116 líneas):

- Acepta 6 nombres: `network`, `audio`, `bluetooth`, `power`, `brightness`, `battery`.
- Otro nombre → exit 64 (usage).
- Comprueba que `/usr/share/churros/popups/<name>/main.py` exista.
- `set -eu` para fallar rápido.
- Lanza el popup con stdout/stderr a `/dev/null` (los popups no deben imprimir).
- Espera 100ms tras lanzar para detectar fallos inmediatos (display ausente, etc.) y limpiar el PIDFILE en ese caso.

---

# Available Popups

| Nombre | Descripción | Servicio |
|--------|-------------|----------|
| `audio` | Volumen, mute, dispositivo de salida | `services/audio.py` |
| `battery` | Porcentaje, estado, tiempo restante | `services/battery.py` |
| `bluetooth` | Toggle y lista de dispositivos | (hardcodeado) |
| `brightness` | Slider de brillo | `services/brightness.py` |
| `network` | Wi-Fi (toggle + redes) + Ethernet | `services/wifi.py` + `services/ethernet.py` |
| `power` | Lock, logout, suspend, hibernate, restart, shutdown | `services/power.py` |

---

# Base Class: PopupWindow

`popups/common/popup.py` define la clase base que todos los popups extienden:

```python
class PopupWindow(Gtk.ApplicationWindow):

    def __init__(self, app, title="Popup", icon="🧪"):

        super().__init__(application=app)

        self.set_title(title)
        self.set_default_size(320, 400)
        self.set_resizable(False)
        self.set_decorated(False)
        self.add_css_class("popup")

        # Header con icono + título
        self.header = Header(icon, title)
        self.main_box.append(self.header)

        # Contenido (lo añade cada popup con self.add(widget))
        self.content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.content.set_vexpand(True)
        self.main_box.append(self.content)
```

Características comunes a todos los popups:

- Tamaño fijo 320×400 (puede ser mayor si el contenido lo requiere)
- Sin decoración de ventana
- CSS class `popup` (permite estilo global desde `common/style.css`)
- Header con icono (Nerd Font glyph) + título
- Método `add(widget)` para añadir widgets al cuerpo

---

# Integration with Waybar

Waybar invoca el launcher estable `/usr/bin/churros-popup` (script bash independizado del código Python). Ejemplos de `archiso/airootfs/etc/skel/.config/waybar/config.jsonc`:

```jsonc
"network":      { "on-click": "churros-popup network" }
"battery":      { "on-click": "churros-popup battery" }
"bluetooth":    { "on-click": "churros-popup bluetooth" }
"backlight":    { "on-click": "churros-popup brightness" }
"pulseaudio":   { "on-click": "churros-popup audio" }
```

Acciones secundarias:

- `pulseaudio` → `on-click-right` silencia (`wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle`)
- `pulseaudio` → `on-scroll-up/down` ajusta volumen en 5%
- `backlight` → `on-scroll-up/down` ajusta brillo `brightnessctl`

Atajos de teclado en niri config.kdl:

```kdl
Mod+Shift+N { spawn "churros-popup" "network"; }
Mod+Shift+A { spawn "churros-popup" "audio"; }
Mod+Shift+B { spawn "churros-popup" "bluetooth"; }
Mod+Shift+L { spawn "churros-popup" "brightness"; }
Mod+Shift+T { spawn "churros-popup" "battery"; }
Mod+Shift+E { spawn "churros-popup" "power"; }
```

El Control Center (`/usr/bin/churros-control-center`) también lanza popups directamente vía `popup_launcher.py` (`subprocess.Popen([sys.executable, popup_main])`), sin pasar por el launcher de toggle — porque desde el control center cada clic abre una ventana nueva intencionalmente.

---

# Adding a New Popup

1. Crea la carpeta del popup:

   ```text
   popups/<nombre>/
   ```

2. Implementa `main.py` (sigue el patrón de los popups existentes — añade `..` al `sys.path` para que `services.wifi`, `i18n` y otros módulos sean importables):

   ```python
   from pathlib import Path
   import sys

   sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

   import gi
   gi.require_version("Gtk", "4.0")
   from gi.repository import Gtk

   from window import MyWindow

   class MyApp(Gtk.Application):
       def do_activate(self):
           window = MyWindow(self)
           window.present()

   app = MyApp()
   app.run()
   ```

3. Implementa `window.py` extendiendo `PopupWindow`:

   ```python
   from common.popup import PopupWindow
   from widgets.my_widget import MyWidget

   class MyWindow(PopupWindow):
       def __init__(self, app):
           super().__init__(app, title="My Popup", icon="🧪")
           self.add(MyWidget())
   ```

4. Crea `style.css` con los estilos del popup.

5. Añade el nombre al case del launcher `/usr/bin/churros-popup`.

6. Añade el módulo en Waybar (`on-click: "churros-popup <nombre>"`) o en un atajo de teclado de niri (`Mod+Shift+X { spawn "churros-popup" "<nombre>"; }`).

Módulo i18n: el paquete `/usr/share/churros/i18n.py` está copiado en churros root y accessible con `from i18n import _` (gracias al `sys.path.insert(0, str(Path(__file__).resolve().parents[2]))` del `main.py`).

---

# Limitations

- **Un solo popup a la vez**: el sistema está pensado para un popup activo. Intentar abrir dos da un comportamiento indefinido.
- **Estado en `/tmp`**: al reiniciar se pierde. Esto es intencional: el popup debe reflejar el estado real del sistema, no cachear.
- **Cierre manual**: los popups no se cierran automáticamente al perder foco. Hay que hacer clic fuera o matarlos con `pkill`.
- **Sin tests**: la interacción con GTK4 hace difícil testear sin un display virtual. Los popups se prueban manualmente.

---

# Future Work

- Cierre automático al perder foco (con `focus-out` event o `wayland-popup`).
- Animaciones de entrada/salida.
- Soporte para múltiples popups simultáneos (sidebar con widgets apilados).
- Integración con la barra de notificaciones del sistema.
- API común para que las apps externas puedan mostrar popups propios.
