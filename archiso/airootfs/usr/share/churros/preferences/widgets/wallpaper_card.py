import os
import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from services.wallpaper import WallpaperService


class WallpaperCard(Gtk.Button):

    def __init__(self, name, path):

        super().__init__()

        self.path = path

        self.add_css_class(
            "wallpaper-card"
        )

        box = Gtk.Box(

            orientation=Gtk.Orientation.VERTICAL,

            spacing=8

        )

        picture = Gtk.Picture.new_for_filename(
            path
        )

        picture.set_size_request(
            220,
            130
        )

        picture.set_content_fit(
            Gtk.ContentFit.COVER
        )

        box.append(
            picture
        )

        label = Gtk.Label(
            label=name
        )

        label.add_css_class(
            "wallpaper-name"
        )

        box.append(
            label
        )

        self.set_child(
            box
        )

        self.connect(
            "clicked",
            self.on_clicked
        )

    def on_clicked(
        self,
        button
    ):

        WallpaperService.set(
            self.path
        )