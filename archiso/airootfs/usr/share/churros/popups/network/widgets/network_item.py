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


class NetworkItem(Gtk.Box):

    def __init__(self, network, callback, forget_callback=None):

        super().__init__(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=10
        )

        self.add_css_class("network-item")

        self.network = network
        self.callback = callback
        self.forget_callback = forget_callback

        self.set_hexpand(True)

        main_btn = Gtk.Button()
        main_btn.set_hexpand(True)
        main_btn.add_css_class("network-main")
        main_btn.connect("clicked", self.on_clicked)

        root = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=8
        )

        row = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=10
        )

        signal = network["signal"]

        if signal >= 80:
            icon = "󰤨"
        elif signal >= 60:
            icon = "󰤥"
        elif signal >= 40:
            icon = "󰤢"
        elif signal >= 20:
            icon = "󰤟"
        else:
            icon = "󰤯"

        icon_label = Gtk.Label(label=icon)
        icon_label.add_css_class("network-icon")

        name = Gtk.Label(label=network["ssid"])
        name.set_hexpand(True)
        name.set_xalign(0)
        name.add_css_class("network-name")

        row.append(icon_label)
        row.append(name)

        if network["security"] not in ("", "--"):

            lock = Gtk.Label(label="󰌾")
            lock.add_css_class("network-lock")
            row.append(lock)

        root.append(row)

        status = Gtk.Label()
        status.set_xalign(0)
        status.add_css_class("network-status")

        if network["connected"]:

            status.set_label(_("Connected"))
            status.add_css_class("connected")

        else:

            status.set_label(_("Signal %d%%") % signal)

        root.append(status)

        main_btn.set_child(root)
        self.append(main_btn)

        if forget_callback and network["saved"] and not network["connected"]:

            forget_btn = Gtk.Button(
                label="✕",
                tooltip_text=_("Forget")
            )
            forget_btn.add_css_class("network-forget")
            forget_btn.connect("clicked", self.on_forget)
            self.append(forget_btn)

    def on_clicked(self, button):

        self.callback(self.network)

    def on_forget(self, button):

        self.forget_callback(self.network)
