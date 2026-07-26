import sys
import os

sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "..",
        "..",
        "preferences"
    )
)

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GLib, Gio

from i18n import _
from services.brightness import BrightnessService


class BrightnessWidget(Gtk.Box):

    def __init__(self):

        super().__init__(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=12
        )

        self.add_css_class(
            "brightness-widget"
        )

        self._suppress_change = False

        data = BrightnessService.get()

        self.label = Gtk.Label()
        self.label.add_css_class("brightness-label")
        self.append(self.label)

        self.slider = Gtk.Scale.new_with_range(
            Gtk.Orientation.HORIZONTAL,
            0,
            100,
            1
        )
        self.slider.set_draw_value(False)
        self.slider.add_css_class("brightness-slider")
        self.slider.set_hexpand(True)

        if data["available"]:

            self.slider.set_value(data["brightness"])
            self.label.set_label(f"󰃠 {data['brightness']}%")

            self.slider.connect("value-changed", self.on_change)

        else:

            self.slider.set_value(100)
            self.slider.set_sensitive(False)
            self.label.set_label(_("Brightness unavailable"))

            info = Gtk.Label(
                label=_("No software brightness control on this display.")
            )
            info.set_wrap(True)
            info.set_xalign(0)
            info.add_css_class("brightness-info")
            self.append(info)

        self.append(self.slider)

        if data["available"]:

            GLib.timeout_add_seconds(
                2,
                self._refresh
            )

    def _refresh(self):

        if self._suppress_change:

            return True

        data = BrightnessService.get()

        if data["available"]:

            current = int(self.slider.get_value())

            if current != data["brightness"] and not self.slider.get_state_flags() & Gtk.StateFlags.ACTIVE:

                self._suppress_change = True
                self.slider.set_value(data["brightness"])
                self._suppress_change = False

                self.label.set_label(f"󰃠 {data['brightness']}%")

        return True

    def on_change(self, slider):

        value = int(slider.get_value())

        self._suppress_change = True

        Gio.Subprocess.new(
            [
                "brightnessctl",
                "--class=backlight",
                "set",
                f"{value}%"
            ],
            Gio.SubprocessFlags.NONE
        )

        self.label.set_label(f"󰃠 {value}%")

        self._suppress_change = False
