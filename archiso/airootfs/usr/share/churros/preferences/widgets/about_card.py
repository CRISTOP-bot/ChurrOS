import os
import platform
import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk


ASSETS = os.path.join(
    os.path.dirname(__file__),
    "..",
    "assets"
)


class AboutCard(Gtk.Box):

    def __init__(self):

        super().__init__(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=18
        )

        self.add_css_class(
            "about-card"
        )

        self.set_margin_top(20)
        self.set_margin_bottom(20)
        self.set_margin_start(20)
        self.set_margin_end(20)

        #
        # Logo
        #

        logo = Gtk.Image.new_from_file(

            os.path.join(
                ASSETS,
                "logo.svg"
            )

        )

        logo.set_pixel_size(110)

        self.append(
            logo
        )

        #
        # Nombre
        #

        title = Gtk.Label(
            label="ChurrOS"
        )

        title.add_css_class(
            "about-title"
        )

        self.append(
            title
        )

        #
        # Versión
        #

        version = Gtk.Label(
            label="Beta"
        )

        version.add_css_class(
            "about-version"
        )

        self.append(
            version
        )

        separator = Gtk.Separator()

        self.append(
            separator
        )

        self.grid = Gtk.Grid()

        self.grid.set_column_spacing(24)
        self.grid.set_row_spacing(10)

        self.append(
            self.grid
        )

        self.add_row(
            0,
            "Kernel",
            platform.release()
        )

        self.add_row(
            1,
            "Arquitectura",
            platform.machine()
        )

        self.add_row(
            2,
            "Python",
            platform.python_version()
        )

        self.add_row(
            3,
            "Sesión",
            "Niri"
        )

        self.add_row(
            4,
            "Servidor",
            "Wayland"
        )

    def add_row(
        self,
        row,
        title,
        value
    ):

        left = Gtk.Label(
            label=title
        )

        left.set_xalign(0)

        left.add_css_class(
            "about-key"
        )

        right = Gtk.Label(
            label=value
        )

        right.set_xalign(1)

        right.add_css_class(
            "about-value"
        )

        self.grid.attach(
            left,
            0,
            row,
            1,
            1
        )

        self.grid.attach(
            right,
            1,
            row,
            1,
            1
        )