from widgets.page import Page
from widgets.group import Group
from widgets.select_row import SelectRow

from services.accent import AccentService


class AccentPage(Page):

    def __init__(self, navigator):

        super().__init__(
            navigator,
            "Color de acento",
            "Personaliza el color principal del sistema",
            parent_page="appearance"
        )

        SelectRow.reset_group()

        self.rows = []

        group = Group(
            "Colores"
        )

        current = AccentService.current()

        for color in AccentService.available():

            row = SelectRow(

                title=color,

                active=color == current,

                callback=lambda c=color: self.select(c)

            )

            self.rows.append(
                row
            )

            group.add(
                row
            )

        self.add(
            group
        )

    def select(
        self,
        color
    ):

        AccentService.set(color)

        self._reload_accent_css()

        current = AccentService.current()

        for row in self.rows:

            row.set_active(
                row.title == current
            )

    def _reload_accent_css(self):

        import os
        import gi

        gi.require_version("Gtk", "4.0")

        from gi.repository import Gtk, Gdk

        try:

            accent_css = AccentService.ACCENT_CSS

            if not os.path.exists(accent_css):

                return

            provider = Gtk.CssProvider()

            provider.load_from_path(accent_css)

            Gtk.StyleContext.add_provider_for_display(
                Gdk.Display.get_default(),
                provider,
                Gtk.STYLE_PROVIDER_PRIORITY_USER + 1
            )

        except Exception:

            pass