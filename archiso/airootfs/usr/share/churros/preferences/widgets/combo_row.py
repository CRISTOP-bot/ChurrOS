import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from widgets.row import Row


class ComboRow(Row):

    def __init__(
        self,
        title,
        values,
        selected=None,
        subtitle=None,
        icon=None,
        callback=None
    ):

        self.callback = callback

        self.combo = Gtk.DropDown()

        model = Gtk.StringList()

        for value in values:

            model.append(value)

        self.combo.set_model(
            model
        )

        if selected in values:

            self.combo.set_selected(

                values.index(
                    selected
                )

            )

        self.combo.connect(

            "notify::selected",

            self.on_changed

        )

        super().__init__(

            title=title,

            subtitle=subtitle,

            icon=icon,

            suffix=self.combo

        )

    def on_changed(
        self,
        combo,
        param
    ):

        if self.callback is None:

            return

        item = combo.get_selected_item()

        if item is None:

            return

        self.callback(

            item.get_string()

        )

    def value(self):

        item = self.combo.get_selected_item()

        if item is None:

            return None

        return item.get_string()

    def set_values(
        self,
        values,
        selected=None
    ):

        model = Gtk.StringList()

        for value in values:

            model.append(
                value
            )

        self.combo.set_model(
            model
        )

        if selected in values:

            self.combo.set_selected(

                values.index(
                    selected
                )

            )