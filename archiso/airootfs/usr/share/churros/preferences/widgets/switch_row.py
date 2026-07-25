import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from widgets.row import Row


class SwitchRow(Row):

    def __init__(
        self,
        title,
        icon=None,
        subtitle=None,
        active=False,
        callback=None
    ):

        self.switch = Gtk.Switch()

        self.switch.set_active(
            active
        )

        super().__init__(
            title=title,
            subtitle=subtitle,
            icon=icon,
            suffix=self.switch
        )

        if callback is not None:

            self.switch.connect(
                "notify::active",
                self._on_changed
            )

            self.callback = callback

        else:

            self.callback = None

    def _on_changed(
        self,
        switch,
        param
    ):

        if self.callback is not None:

            self.callback(
                switch.get_active()
            )

    def get_active(self):

        return self.switch.get_active()

    def set_active(
        self,
        active
    ):

        self.switch.set_active(
            active
        )