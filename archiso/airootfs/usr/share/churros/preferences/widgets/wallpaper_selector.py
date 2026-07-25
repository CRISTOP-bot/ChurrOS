import os
import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GObject


class WallpaperSelector(Gtk.Box):

    __gsignals__ = {

        "wallpaper-selected": (

            GObject.SignalFlags.RUN_FIRST,

            None,

            (str,)

        )

    }

    def __init__(self):

        super().__init__(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=18
        )

        self.add_css_class(
            "wallpaper-selector"
        )

        title = Gtk.Label(
            label="Fondos de pantalla"
        )

        title.set_xalign(0)

        title.add_css_class(
            "group-title"
        )

        self.append(
            title
        )

        #
        # Grid
        #

        self.flow = Gtk.FlowBox()

        self.flow.set_max_children_per_line(
            4
        )

        self.flow.set_selection_mode(
            Gtk.SelectionMode.NONE
        )

        self.flow.set_row_spacing(
            14
        )

        self.flow.set_column_spacing(
            14
        )

        self.append(
            self.flow
        )

    def add_wallpaper(
        self,
        image,
        name
    ):

        button = Gtk.Button()

        button.add_css_class(
            "wallpaper-button"
        )

        picture = Gtk.Picture.new_for_filename(
            image
        )

        picture.set_content_fit(
            Gtk.ContentFit.COVER
        )

        picture.set_size_request(
            220,
            130
        )

        button.set_child(
            picture
        )

        button.connect(
            "clicked",
            self.on_clicked,
            image
        )

        self.flow.append(
            button
        )

    def on_clicked(
        self,
        button,
        path
    ):

        self.emit(

            "wallpaper-selected",

            path

        )