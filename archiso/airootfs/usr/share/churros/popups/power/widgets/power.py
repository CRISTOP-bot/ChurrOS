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

from gi.repository import Gtk

from i18n import _

from widgets.button import PowerButton

from services.power import PowerService


class PowerWidget(Gtk.Box):

    def __init__(self):

        super().__init__(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=10
        )

        self.add_css_class("power-widget")

        actions = [
            ("󰌾", "Lock",      PowerService.lock),
            ("󰍃", "Logout",    PowerService.logout),
            ("󰒲", "Suspend",   PowerService.suspend),
            ("󰤅", "Hibernate", PowerService.hibernate),
            ("󰜉", "Restart",   PowerService.restart),
            ("󰐥", "Shutdown",  PowerService.shutdown),
        ]

        can_hibernate = PowerService.can_hibernate()

        for icon, label, action in actions:

            if label == "Hibernate" and not can_hibernate:

                continue

            button = PowerButton(icon, _(label), lambda *_a, _action=action: _action())
            self.append(button)
