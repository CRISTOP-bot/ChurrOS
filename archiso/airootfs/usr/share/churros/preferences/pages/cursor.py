from widgets.page import Page
from widgets.group import Group
from widgets.select_row import SelectRow
from widgets.slider_row import SliderRow

from services.cursor import CursorService
from services.dotfiles.niri_config import NiriConfig


class CursorPage(Page):

    def __init__(self, navigator):

        super().__init__(
            navigator,
            "Cursor",
            "Selecciona el tema y tamano del cursor",
            parent_page="appearance"
        )

        SelectRow.reset_group()

        self.rows = []

        #
        # Tema
        #

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

        #
        # Tamano
        #

        size_group = Group(
            "Tamano del cursor"
        )

        self.size_slider = SliderRow(
            title="Tamano",
            value=float(CursorService.size()),
            minimum=8.0,
            maximum=64.0,
            step=1.0,
            callback=self.on_size_changed
        )

        size_group.add(self.size_slider)

        self.add(size_group)

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

    def on_size_changed(
        self,
        slider
    ):

        size = slider.get_value()

        CursorService.set_size(size)

        try:

            NiriConfig.set_cursor_size(size)

        except Exception as exc:

            print("[cursor] niri size fallo:", exc)
