from widgets.page import Page
from widgets.group import Group
from widgets.select_row import SelectRow

from services.icons import IconsService


class IconsPage(Page):

    def __init__(self, navigator):

        super().__init__(
            navigator,
            "Iconos",
            "Selecciona el tema de iconos"
        )

        self.rows = []

        group = Group(
            "Temas disponibles"
        )

        current = IconsService.current()

        for theme in IconsService.available():

            row = SelectRow(

                title=theme,

                active=theme == current,

                callback=lambda t=theme: self.select(t)

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
        theme
    ):

        IconsService.set(
            theme
        )

        current = IconsService.current()

        for row in self.rows:

            row.set_active(
                row.title == current
            )