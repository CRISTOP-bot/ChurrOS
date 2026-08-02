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

        self.switch.set_valign(Gtk.Align.CENTER)

        super().__init__(
            title=title,
            subtitle=subtitle,
            icon=icon,
            suffix=self.switch,
            callback=self._on_row_clicked if callback else None
        )

        self._user_callback = callback

        if callback is not None:

            self.switch.connect(
                "notify::active",
                self._on_switch_changed
            )

    def _on_row_clicked(self, row):

        new_state = not self.switch.get_active()

        self.switch.set_active(new_state)

    def _on_switch_changed(
        self,
        switch,
        param
    ):

        if self._user_callback is not None:

            self._user_callback(
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