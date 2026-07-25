import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk


class Group(Gtk.Box):

    def __init__(
        self,
        title
    ):

        super().__init__(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=10
        )

        self.set_margin_bottom(24)

        #
        # Título
        #

        label = Gtk.Label(
            label=title
        )

        label.set_xalign(0)

        label.add_css_class(
            "group-title"
        )

        self.append(
            label
        )

        #
        # Tarjeta
        #

        self.card = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL
        )

        self.card.add_css_class(
            "group-card"
        )

        self.append(
            self.card
        )

        self.first = True

    def clear(
        self
    ):

        child = self.card.get_first_child()

        while child is not None:

            next_child = child.get_next_sibling()

            self.card.remove(
                child
            )

            child = next_child

        self.first = True

    def add(
        self,
        widget
    ):

        if not self.first:

            separator = Gtk.Separator(
                orientation=Gtk.Orientation.HORIZONTAL
            )

            separator.add_css_class(
                "group-separator"
            )

            self.card.append(
                separator
            )

        self.card.append(
            widget
        )

        self.first = False