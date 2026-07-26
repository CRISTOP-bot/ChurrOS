from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
PREFERENCES = Path(__file__).resolve().parents[5] / "preferences"

sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(PREFERENCES))

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GLib

from i18n import _

from services.audio import AudioService


class VolumeWidget(Gtk.Box):

    def __init__(self, source=False):

        super().__init__(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=8
        )

        self._source = source
        self._suppress_change = False

        self.add_css_class("volume-widget")

        self.box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=12
        )

        self.icon = Gtk.Label(label="󰕾" if not source else "󰍜")
        self.icon.add_css_class("volume-icon")

        self.label = Gtk.Label()
        self.label.set_xalign(0)
        self.label.set_hexpand(True)
        self.label.add_css_class("volume-label")

        self.slider = Gtk.Scale.new_with_range(
            Gtk.Orientation.HORIZONTAL,
            0,
            100,
            1
        )
        self.slider.set_draw_value(False)
        self.slider.set_hexpand(True)
        self.slider.set_digits(0)
        self.slider.set_round_digits(0)

        if not AudioService.available():

            self.label.set_label(_("Audio requires WirePlumber (wpctl)"))
            self.slider.set_sensitive(False)
            self.box.append(self.icon)
            self.box.append(self.slider)
            self.append(self.box)
            return

        initial = (
            AudioService.get_input_volume() if source
            else AudioService.get_volume()
        )
        self.slider.set_value(initial)
        self._update_label(initial)

        self.slider.connect("value-changed", self.on_change)

        self.box.append(self.icon)
        self.box.append(self.slider)

        self.append(self.box)
        self.append(self.label)

        GLib.timeout_add_seconds(1, self._refresh)

    def _get_volume(self):

        return (
            AudioService.get_input_volume() if self._source
            else AudioService.get_volume()
        )

    def _set_volume(self, value):

        if self._source:

            AudioService.set_input_volume(value)

        else:

            AudioService.set_volume(value)

    def _update_label(self, value):

        prefix = "󰍜" if self._source else "󰕾"
        self.label.set_label(f"{prefix} {value}%")

    def _refresh(self):

        if self._suppress_change:
            return True

        current = self._get_volume()

        if current != int(self.slider.get_value()) and not self.slider.get_state_flags() & Gtk.StateFlags.ACTIVE:

            self._suppress_change = True
            self.slider.set_value(current)
            self._update_label(current)
            self._suppress_change = False

        return True

    def on_change(self, slider):

        value = int(slider.get_value())

        self._suppress_change = True
        self._update_label(value)

        try:

            self._set_volume(value)

        except Exception:
            pass

        self._suppress_change = False
