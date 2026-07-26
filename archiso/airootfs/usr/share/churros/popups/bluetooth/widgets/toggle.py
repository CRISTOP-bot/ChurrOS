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

from services.bluetooth import BluetoothService


class BluetoothToggleWidget(Gtk.Box):

    def __init__(self):

        super().__init__(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=12
        )

        self.add_css_class("bluetooth-toggle")

        self.label = Gtk.Label(label="Bluetooth")
        self.label.set_hexpand(True)
        self.label.set_xalign(0)

        self.switch = Gtk.Switch()

        if BluetoothService.is_blocked():

            self.switch.set_active(False)
            self.switch.set_sensitive(False)
            self.label.set_label(_("Bluetooth blocked (rfkill)"))

        else:

            self.switch.set_active(BluetoothService.is_enabled())
            self.switch.connect("state-set", self.on_toggle)

        self.append(self.label)
        self.append(self.switch)

        GLib.timeout_add_seconds(2, self._refresh)

    def _refresh(self):

        if not BluetoothService.is_blocked():

            current = BluetoothService.is_enabled()

            if current != self.switch.get_active():

                self.switch.handler_block_by_func(
                    self.on_toggle
                ) if False else None

                self.switch.set_active(current)

        return True

    def on_toggle(self, switch, state):

        if state:

            BluetoothService.enable()
            BluetoothService.scan_start()

        else:

            BluetoothService.scan_stop()
            BluetoothService.disable()
