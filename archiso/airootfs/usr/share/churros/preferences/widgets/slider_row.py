import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from widgets.row import Row


class SliderRow(Row):

    def __init__(
        self,
        title,
        icon=None,
        subtitle=None,
        minimum=0,
        maximum=100,
        step=1,
        value=0,
        callback=None
    ):

        self.scale = Gtk.Scale.new_with_range(
            Gtk.Orientation.HORIZONTAL,
            minimum,
            maximum,
            step
        )

        self.scale.set_draw_value(False)

        self.scale.set_hexpand(True)

        self.scale.set_value(
            value
        )

        self.scale.set_size_request(
            180,
            -1
        )

        if callback is not None:

            self.scale.connect(
                "value-changed",
                callback
            )

        super().__init__(
            title=title,
            subtitle=subtitle,
            icon=icon,
            suffix=self.scale
        )

    def get_value(self):

        return self.scale.get_value()

    def set_value(
        self,
        value
    ):

        self.scale.set_value(
            value
        )