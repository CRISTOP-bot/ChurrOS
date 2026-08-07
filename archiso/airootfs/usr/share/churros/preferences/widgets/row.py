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


class Row(Gtk.Button):

    def __init__(
        self,
        title,
        subtitle=None,
        icon=None,
        value=None,
        suffix=None,
        callback=None
    ):

        super().__init__()

        self.callback = callback

        self.add_css_class(
            "row"
        )

        self.set_has_frame(
            False
        )

        content = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=14
        )

        content.set_margin_top(12)
        content.set_margin_bottom(12)
        content.set_margin_start(14)
        content.set_margin_end(14)

        #
        # Icono
        #

        if icon is not None:

            image = Gtk.Image.new_from_file(

                os.path.join(
                    ICON_DIR,
                    icon
                )

            )

            image.set_pixel_size(
                22
            )

            content.append(
                image
            )

        #
        # Labels
        #

        labels = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=2
        )

        labels.set_hexpand(
            True
        )

        title_label = Gtk.Label(
            label=title
        )

        title_label.set_xalign(
            0
        )

        title_label.add_css_class(
            "row-title"
        )

        self._title_label = title_label

        labels.append(
            title_label
        )

        if subtitle is not None:

            subtitle_label = Gtk.Label(
                label=subtitle
            )

            subtitle_label.set_xalign(
                0
            )

            subtitle_label.add_css_class(
                "row-subtitle"
            )

            self._subtitle_label = subtitle_label

            labels.append(
                subtitle_label
            )

        content.append(
            labels
        )

        #
        # Valor
        #

        if value is not None:

            value_label = Gtk.Label(
                label=value
            )

            value_label.add_css_class(
                "row-value"
            )

            content.append(
                value_label
            )

        #
        # Widget derecho
        #

        elif suffix is not None:

            content.append(
                suffix
            )

        self.set_child(
            content
        )

        #
        # Callback
        #

        if self.callback is not None:

            self.connect(
                "clicked",
                self._on_clicked
            )

    def _on_clicked(
        self,
        button
    ):

        self.callback(
            self
        )

    def set_subtitle(
        self,
        text
    ):

        if hasattr(
            self,
            "_subtitle_label"
        ) and self._subtitle_label is not None:

            self._subtitle_label.set_label(text)

    def set_title(
        self,
        text
    ):

        if hasattr(
            self,
            "_title_label"
        ) and self._title_label is not None:

            self._title_label.set_label(text)