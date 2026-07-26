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

from gi.repository import Gtk, Gio

from i18n import _

from widgets.button import PowerButton

from services.power import PowerService


_CONFIRM = {"Suspend", "Hibernate", "Restart", "Shutdown"}


class PowerWidget(Gtk.Box):

    def __init__(self):

        super().__init__(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=10
        )

        self.add_css_class("power-widget")

        actions = [
            ("󰤄", "Lock",      PowerService.lock),
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

            button = PowerButton(icon, _(label), self._make_callback(action, label))
            self.append(button)

    def _make_callback(self, action, label):

        def callback(*_):

            if label in _CONFIRM:

                self._confirm_and_run(label, action)

            else:

                action()

        return callback

    def _confirm_and_run(self, label, action):

        dialog = Gtk.AlertDialog()

        dialog.set_message(_("Are you sure?"))
        dialog.set_detail(
            _("Confirm action: {action}").format(action=_(label))
        )
        dialog.set_modal(True)

        dialog.choose(
            None,
            None,
            None
        )

        dialog.connect(
            "response",
            lambda d, response:
                action() if response == Gtk.ResponseType.OK else None
        )
