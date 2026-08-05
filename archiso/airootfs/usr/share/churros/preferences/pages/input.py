from widgets.page import Page
from widgets.group import Group
from widgets.switch_row import SwitchRow
from widgets.slider_row import SliderRow
from widgets.combo_row import ComboRow

import subprocess

from services.dotfiles.niri_config import NiriConfig


def _run(command):

    try:

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=2
        )

        return result.stdout.strip().strip("'\"")

    except Exception:

        return ""


def _set_gsettings(key, value):

    try:

        subprocess.run(
            ["gsettings", "set", "org.gnome.desktop.input-sources", key, str(value)],
            capture_output=True,
            timeout=2
        )

    except Exception:

        pass


class InputPage(Page):

    def __init__(self, navigator):

        super().__init__(
            navigator,
            "Entrada",
            "Teclado, raton y panel tactil"
        )

        #
        # Teclado
        #

        keyboard = Group("Teclado")

        layouts = [
            "es",
            "us",
            "latam",
            "fr",
            "de",
            "it"
        ]

        current = _run(
            ["gsettings", "get", "org.gnome.desktop.input-sources", "sources"]
        )

        current_layout = "es"
        if "es" in current:
            current_layout = "es"
        elif "us" in current:
            current_layout = "us"
        elif "latam" in current:
            current_layout = "latam"

        self.layout_combo = ComboRow(
            title="Disposicion del teclado",
            values=layouts,
            selected=current_layout,
            callback=self.on_layout_changed
        )

        keyboard.add(self.layout_combo)

        self.add(keyboard)

        #
        # Raton
        #

        mouse = Group("Raton")

        tap_value = _run(
            ["gsettings", "get", "org.gnome.desktop.peripherals.mouse", "tap-to-click"]
        )
        tap_active = "true" in tap_value.lower()

        mouse.add(
            SwitchRow(
                title="Tocar para clic",
                subtitle="Raton: clic con un toque",
                active=tap_active,
                callback=self.on_tap_changed
            )
        )

        self.add(mouse)

        #
        # Velocidad del raton
        #

        speed_group = Group("Velocidad")

        try:

            speed_raw = _run(
                ["gsettings", "get", "org.gnome.desktop.peripherals.mouse", "speed"]
            )
            speed = float(speed_raw) if speed_raw else 0.0
        except Exception:

            speed = 0.0

        self.speed_slider = SliderRow(
            title="Velocidad del raton",
            value=speed * 100.0,
            minimum=-100.0,
            maximum=100.0,
            step=10.0,
            callback=self.on_speed_changed
        )

        speed_group.add(self.speed_slider)

        self.add(speed_group)

    def on_layout_changed(self, layout):

        _set_gsettings(
            "sources",
            "[('xkb', '" + layout + "')]"
        )

        try:

            NiriConfig.set_keyboard_layout(layout)

        except Exception as exc:

            print("[input] niri layout fallo:", exc)

    def on_tap_changed(self, active):

        _set_gsettings("tap-to-click", "true" if active else "false")

    def on_speed_changed(self, slider):

        value = slider.get_value() / 100.0

        try:

            subprocess.run(
                ["gsettings", "set", "org.gnome.desktop.peripherals.mouse", "speed", str(value)],
                capture_output=True,
                timeout=2
            )

        except Exception:

            pass
