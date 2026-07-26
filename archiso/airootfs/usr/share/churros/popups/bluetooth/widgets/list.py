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


def _device_icon(name):

    n = name.lower()
    if any(k in n for k in ("airpod", "headphone", "earbuds", "speaker")):
        return "🎧"
    if any(k in n for k in ("keyboard", "keychron")):
        return "⌨"
    if any(k in n for k in ("mouse", "mx master", "logi")):
        return "🖱"
    if any(k in n for k in ("controller", "dualsense", "xbox", "joy")):
        return "🎮"
    if any(k in n for k in ("watch", "band")):
        return "⌚"
    return "📱"


class DeviceRow(Gtk.Box):

    def __init__(self, device):

        super().__init__(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=10
        )

        self.add_css_class("device-item")
        self.device = device

        icon = Gtk.Label(label=_device_icon(device["name"]))

        name_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=2
        )
        name_box.set_hexpand(True)

        name = Gtk.Label(label=device["name"])
        name.set_hexpand(True)
        name.set_xalign(0)
        name.add_css_class("device-name")

        status = Gtk.Label(
            label=_("Connected") if device["connected"] else ""
        )
        status.set_xalign(0)
        status.add_css_class("device-status")

        name_box.append(name)

        if device["connected"]:
            name_box.append(status)

        action_label = _("Disconnect") if device["connected"] else _("Connect")
        action = Gtk.Button(
            label=action_label,
            tooltip_text=_("Connect") if not device["connected"] else _("Disconnect")
        )
        action.add_css_class("device-action")
        action.connect("clicked", self.on_action)

        forget_btn = Gtk.Button(
            label="✕",
            tooltip_text=_("Remove")
        )
        forget_btn.add_css_class("device-forget")
        forget_btn.connect("clicked", self.on_forget)

        self.append(icon)
        self.append(name_box)
        self.append(action)
        self.append(forget_btn)

    def on_action(self, button):

        if self.device["connected"]:
            BluetoothService.disconnect(self.device["address"])
        else:
            BluetoothService.connect(self.device["address"])

    def on_forget(self, button):

        BluetoothService.remove(self.device["address"])

    def update(self):

        connected = BluetoothService._is_connected(
            self.device["address"]
        )

        if connected != self.device.get("connected"):

            self.device["connected"] = connected

            self.remove(self.get_first_child())

            while self.get_first_child():
                self.remove(self.get_first_child())

            self.__init__(self.device)


class DeviceListWidget(Gtk.Box):

    def __init__(self):

        super().__init__(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=6
        )

        self.add_css_class("device-list")

        self._header = Gtk.Label(label=_("Devices"))
        self._header.add_css_class("section-title")
        self._header.set_xalign(0)
        self.append(self._header)

        self._empty = Gtk.Label(label=_("No devices"))
        self._empty.set_xalign(0)
        self._empty.add_css_class("empty-label")

        self._devices_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=4
        )
        self.append(self._devices_box)

        self._refresh()

        GLib.timeout_add_seconds(3, self._refresh)

    def _refresh(self):

        for child in list(self._devices_box):
            self._devices_box.remove(child)

        devices = BluetoothService.list_devices()

        if not devices:

            self._devices_box.append(Gtk.Label(label=_("No devices found.")))

        for d in devices:
            self._devices_box.append(DeviceRow(d))

        return True
