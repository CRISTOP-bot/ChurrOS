from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
PREFERENCES = Path(__file__).resolve().parents[5] / "preferences"

sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(PREFERENCES))

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from i18n import _

from services.audio import AudioService


class DeviceWidget(Gtk.Box):

    def __init__(self, source=False):

        super().__init__(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=6
        )

        self._source = source
        self.add_css_class("device-widget")

        self.dropdown = Gtk.DropDown.new_from_strings([])
        self.dropdown.add_css_class("device-dropdown")
        self.dropdown.connect("notify::selected", self.on_device_selected)

        self._update_devices()

    def _update_devices(self):

        devices = (
            AudioService.list_sources() if self._source
            else AudioService.list_sinks()
        )

        names = [d["name"] for d in devices]

        self._devices = devices
        self._updating = True

        self.dropdown.set_model(Gtk.StringList.new(names))

        for i, d in enumerate(devices):

            if d.get("default"):
                self.dropdown.set_selected(i)
                break

        self._updating = False

    def on_device_selected(self, dropdown, pspec):

        if getattr(self, "_updating", True):
            return

        idx = dropdown.get_selected()

        if idx >= 0 and idx < len(self._devices):

            AudioService.set_default_sink(
                self._devices[idx]["id"]
            )
