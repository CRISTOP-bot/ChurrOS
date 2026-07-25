from widgets.page import Page
from widgets.group import Group
from widgets.row import Row

from services.fonts import FontService


class FontsPage(Page):

    def __init__(self, navigator):

        super().__init__(
            navigator,
            "Fuentes",
            "Selecciona la fuente del sistema"
        )

        self.navigator = navigator

        group = Group(
            "Fuentes instaladas"
        )

        current = FontService.current()

        fonts = FontService.available()

        if not fonts:

            group.add(

                Row(

                    title="No se encontraron fuentes",

                    subtitle="Instala una fuente",

                    icon="font.svg"

                )

            )

        else:

            for font in fonts:

                group.add(

                    Row(

                        title=font,

                        subtitle=(
                            "Seleccionada"
                            if font == current
                            else None
                        ),

                        icon="font.svg",

                        callback=lambda _, f=font: self.select(f)

                    )

                )

        self.add(
            group
        )

    def select(
        self,
        font
    ):

        FontService.set(
            font
        )

        self.navigator.show_page(
            "appearance"
        )