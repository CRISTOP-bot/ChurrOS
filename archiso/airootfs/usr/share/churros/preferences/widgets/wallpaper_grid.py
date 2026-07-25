import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from widgets.wallpaper_card import WallpaperCard


class WallpaperGrid(Gtk.FlowBox):

    def __init__(self):

        super().__init__()

        self.set_selection_mode(
            Gtk.SelectionMode.NONE
        )

        self.set_max_children_per_line(
            4
        )

        self.set_min_children_per_line(
            2
        )

        self.set_row_spacing(
            16
        )

        self.set_column_spacing(
            16
        )

        self.set_margin_top(
            12
        )

        self.set_margin_bottom(
            12
        )

        self.set_margin_start(
            12
        )

        self.set_margin_end(
            12
        )

        self.set_homogeneous(
            True
        )

    def add_wallpaper(
        self,
        name,
        path
    ):

        card = WallpaperCard(
            name,
            path
        )

        self.append(
            card
        )