from widgets.page import Page
from widgets.group import Group
from widgets.select_row import SelectRow

from services.accent import AccentService


class AccentPage(Page):

    def __init__(self, navigator):

        super().__init__(
            navigator,
            "Color de acento",
            "Personaliza el color principal del sistema"
        )

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

        current = AccentService.current()

        for row in self.rows:

            row.set_active(
                row.title == current
            )