import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from widgets.row import Row


class NavigationRow(Row):

    def __init__(
        self,
        navigator,
        title,
        icon,
        page_name,
        subtitle=None
    ):

        self.navigator = navigator
        self.page_name = page_name

        arrow = Gtk.Image.new_from_icon_name(
            "go-next-symbolic"
        )

        arrow.add_css_class(
            "row-arrow"
        )

        super().__init__(

            title=title,

            subtitle=subtitle,

            icon=icon,

            suffix=arrow,

            callback=self.on_clicked

        )

    def on_clicked(
        self,
        row
    ):

        self.navigator.show_page(
            self.page_name
        )