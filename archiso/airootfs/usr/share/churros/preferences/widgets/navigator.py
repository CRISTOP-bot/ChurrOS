import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GObject


class Navigator(Gtk.Stack):

    __gsignals__ = {

        "navigated": (

            GObject.SignalFlags.RUN_FIRST,

            None,

            (str,)

        )

    }

    def __init__(self):

        super().__init__()

        self.set_hexpand(True)
        self.set_vexpand(True)

        self.set_transition_type(
            Gtk.StackTransitionType.SLIDE_LEFT_RIGHT
        )

        self.set_transition_duration(
            250
        )

        self.history = []

    def add_page(
        self,
        name,
        widget
    ):

        if self.get_child_by_name(name) is None:

            self.add_named(
                widget,
                name
            )

    def show_page(
        self,
        name
    ):

        current = self.get_visible_child_name()

        if current and current != name:

            self.history.append(
                current
            )

        self.set_visible_child_name(
            name
        )

        self.emit(
            "navigated",
            name
        )

    def back(self):

        if not self.history:

            return

        page = self.history.pop()

        self.set_visible_child_name(
            page
        )

        self.emit(
            "navigated",
            page
        )

    def clear_history(self):

        self.history.clear()