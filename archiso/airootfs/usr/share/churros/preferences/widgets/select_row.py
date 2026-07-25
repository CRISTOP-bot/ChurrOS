import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from widgets.row import Row


class SelectRow(Row):

    def __init__(
        self,
        title,
        subtitle=None,
        icon=None,
        active=False,
        callback=None
    ):

        self.title = title

        self.callback = callback

        self.check = Gtk.CheckButton()

        self.check.set_can_focus(False)

        self.check.set_focusable(False)

        self.check.set_active(
            active
        )

        super().__init__(

            title=title,

            subtitle=subtitle,

            icon=icon,

            suffix=self.check

        )

        self.connect(
            "clicked",
            self.on_clicked
        )

    def on_clicked(
        self,
        *args
    ):

        if self.callback is not None:

            self.callback()

    def set_active(
        self,
        active
    ):

        self.check.set_active(
            active
        )

    def get_active(
        self
    ):

        return self.check.get_active()