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


class SidebarItem(Gtk.Button):

    def __init__(
        self,
        page,
        icon,
        title
    ):

        super().__init__()

        self.page = page

        self.add_css_class(
            "sidebar-item"
        )

        content = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=12
        )

        content.set_margin_top(10)
        content.set_margin_bottom(10)
        content.set_margin_start(14)
        content.set_margin_end(14)

        image = Gtk.Image.new_from_file(

            os.path.join(
                ICON_DIR,
                icon
            )

        )

        image.set_pixel_size(
            20
        )

        label = Gtk.Label(
            label=title
        )

        label.set_xalign(
            0
        )

        label.set_hexpand(
            True
        )

        content.append(
            image
        )

        content.append(
            label
        )

        self.set_child(
            content
        )

    def activate(self):

        self.add_css_class(
            "active"
        )

    def deactivate(self):

        self.remove_css_class(
            "active"
        )