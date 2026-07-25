import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk


class Section(Gtk.Box):

    def __init__(self, title):

        super().__init__(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=10
        )

        self.set_margin_bottom(24)

        label = Gtk.Label(
            label=title
        )

        label.set_xalign(0)

        label.add_css_class(
            "section-title"
        )

        self.append(label)

        self.content = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=0
        )

        self.content.add_css_class(
            "section"
        )

        self.append(
            self.content
        )

    def add(self, widget):

        self.content.append(widget)