import os

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk


ICON_DIR = os.path.join(
    os.path.dirname(__file__),
    "..",
    "assets",
    "icons"
)


class InfoRow(Gtk.Box):

    def __init__(
        self,
        title,
        value,
        icon=None
    ):

        super().__init__(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=14
        )

        self.add_css_class(
            "info-row"
        )

        self.set_margin_top(12)
        self.set_margin_bottom(12)
        self.set_margin_start(14)
        self.set_margin_end(14)

        #
        # Icono
        #

        if icon:

            image = Gtk.Image.new_from_file(

                os.path.join(
                    ICON_DIR,
                    icon
                )

            )

            image.set_pixel_size(
                22
            )

            self.append(
                image
            )

        #
        # Título
        #

        title_label = Gtk.Label(
            label=title
        )

        title_label.set_xalign(
            0
        )

        title_label.set_hexpand(
            True
        )

        title_label.add_css_class(
            "row-title"
        )

        self.append(
            title_label
        )

        #
        # Valor
        #

        self.value = Gtk.Label(
            label=value
        )

        self.value.add_css_class(
            "info-value"
        )

        self.append(
            self.value
        )

    def set_value(
        self,
        value
    ):

        self.value.set_label(
            value
        )