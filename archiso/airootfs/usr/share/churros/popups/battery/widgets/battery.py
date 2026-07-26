from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
PREFERENCES = Path(__file__).resolve().parents[4] / "preferences"

sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(PREFERENCES))

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GLib

from i18n import _

from services.battery import BatteryService


_STATE_LABELS = {
    "charging": "Charging",
    "discharging": "Discharging",
    "fully-charged": "Full",
    "pending-charge": "Pending charge",
    "pending-discharge": "Pending discharge",
    "empty": "Empty",
    "unknown": "Unknown",
}


class BatteryWidget(Gtk.Box):

    def __init__(self):

        super().__init__(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=12
        )

        self.add_css_class("battery-widget")

        self.percentage = Gtk.Label()
        self.percentage.add_css_class("battery-percentage")

        self.status = Gtk.Label()
        self.status.add_css_class("battery-status")

        self.remaining = Gtk.Label()
        self.remaining.add_css_class("battery-remaining")

        self.append(self.percentage)
        self.append(self.status)
        self.append(self.remaining)

        self.update()

        GLib.timeout_add_seconds(
            5,
            self.update
        )

    def update(self):

        try:

            battery = BatteryService.get()

        except Exception:

            battery = {"available": False}

        if not battery["available"]:

            self.percentage.set_label(_("No battery detected"))
            self.status.set_visible(False)
            self.remaining.set_visible(False)

            return True

        self.status.set_visible(True)
        self.remaining.set_visible(True)

        self.percentage.set_label(
            f"{battery['icon']} {battery['percentage']}%"
        )

        state_key = battery["state"]
        state_label = _STATE_LABELS.get(state_key, state_key.title())
        self.status.set_label(_(state_label))

        if battery["state"] == "charging" and battery["time_to_full"]:

            self.remaining.set_label(
                f"{battery['time_to_full']} {_('until full')}"
            )

        elif battery["state"] == "discharging" and battery["time_to_empty"]:

            self.remaining.set_label(
                f"{battery['time_to_empty']} {_('until empty')}"
            )

        else:

            self.remaining.set_label("")

        return True
