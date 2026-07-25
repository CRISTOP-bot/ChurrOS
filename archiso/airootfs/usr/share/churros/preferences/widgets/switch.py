import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk


class Switch(Gtk.Switch):

    def __init__(
        self,
        active=False
    ):

        super().__init__()

        self.set_active(
            active
        )

        self.set_valign(
            Gtk.Align.CENTER
        )

        self.add_css_class(
            "churros-switch"
        )