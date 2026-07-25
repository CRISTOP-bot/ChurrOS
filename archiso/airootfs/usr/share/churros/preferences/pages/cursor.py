from widgets.page import Page
from widgets.group import Group
from widgets.select_row import SelectRow

from services.cursor import CursorService


class CursorPage(Page):

    def __init__(self, navigator):

        super().__init__(
            navigator,
            "Cursor",
            "Selecciona el tema del cursor"
        )

        self.rows = []

        group = Group(
            "Temas disponibles"
        )

        current = CursorService.current()

        for cursor in CursorService.available():

            row = SelectRow(

                title=cursor,

                active=cursor == current,

                callback=lambda c=cursor: self.select(c)

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
        cursor
    ):

        CursorService.set(
            cursor
        )

        current = CursorService.current()

        for row in self.rows:

            row.set_active(
                row.title == current
            )