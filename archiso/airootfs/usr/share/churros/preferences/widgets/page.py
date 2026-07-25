import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk


class Page(Gtk.ScrolledWindow):

    def __init__(
        self,
        navigator,
        title,
        subtitle=None
    ):

        super().__init__()

        self.navigator = navigator

        self.set_hexpand(True)
        self.set_vexpand(True)

        self.set_policy(
            Gtk.PolicyType.NEVER,
            Gtk.PolicyType.AUTOMATIC
        )

        #
        # Contenedor principal
        #

        root = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=18
        )

        root.set_margin_top(24)
        root.set_margin_bottom(24)
        root.set_margin_start(24)
        root.set_margin_end(24)

        self.set_child(root)

        #
        # Cabecera
        #

        header = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=4
        )

        title_label = Gtk.Label(
            label=title,
            xalign=0
        )

        title_label.add_css_class(
            "page-title"
        )

        header.append(title_label)

        if subtitle:

            subtitle_label = Gtk.Label(
                label=subtitle,
                xalign=0
            )

            subtitle_label.add_css_class(
                "page-subtitle"
            )

            header.append(
                subtitle_label
            )

        root.append(
            header
        )

        #
        # Contenido
        #

        self.content = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=18
        )

        root.append(
            self.content
        )

    def add(
        self,
        widget
    ):

        self.content.append(
            widget
        )