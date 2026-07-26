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


class MuteWidget(Gtk.Button):

    def __init__(self, source=False):

        super().__init__()

        self._source = source
        self.add_css_class("mute-button")

        self._update_state()

        self.connect("clicked", self.toggle)

        GLib.timeout_add_seconds(1, self._update_state)

    def _is_muted(self):

        return (
            AudioService.is_input_muted() if self._source
            else AudioService.is_muted()
        )

    def _set_muted(self, value):

        if self._source:
            AudioService.set_input_mute(value)
        else:
            AudioService.set_mute(value)

    def _update_label(self, muted):

        prefix = "󰍚" if self._source else "󰝟"
        if muted:
            self.set_label(f"{prefix}  {_('Mute')}")
        else:
            self.set_label(f"{prefix}  {_('Unmute')}")

    def _update_state(self):

        try:

            self._update_label(self._is_muted())

        except Exception:
            pass

        return True

    def toggle(self, button):

        current = self._is_muted()
        self._set_muted(not current)
        self._update_label(not current)
