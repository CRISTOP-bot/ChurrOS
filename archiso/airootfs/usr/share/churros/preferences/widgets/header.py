import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk


class Header(Gtk.Box):

    def __init__(
        self,
        navigator,
        title,
        subtitle=None,
        back=False
    ):

        super().__init__(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=12
        )

        self.navigator = navigator

        #
        # Barra superior
        #

        top = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=12
        )

        if back:

            button = Gtk.Button()

            button.set_icon_name(
                "go-previous-symbolic"
            )

            button.add_css_class(
                "header-back"
            )

            button.connect(
                "clicked",
                self.on_back
            )

            top.append(
                button
            )

        labels = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=2
        )

        title_label = Gtk.Label(
            label=title
        )

        title_label.set_xalign(0)

        title_label.add_css_class(
            "header-title"
        )

        labels.append(
            title_label
        )

        if subtitle:

            subtitle_label = Gtk.Label(
                label=subtitle
            )

            subtitle_label.set_xalign(0)

            subtitle_label.add_css_class(
                "header-subtitle"
            )

            labels.append(
                subtitle_label
            )

        top.append(
            labels
        )

        self.append(
            top
        )

        separator = Gtk.Separator(
            orientation=Gtk.Orientation.HORIZONTAL
        )

        separator.add_css_class(
            "header-separator"
        )

        self.append(
            separator
        )

    def on_back(
        self,
        *args
    ):

        self.navigator.back()