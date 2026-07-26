from widgets.page import Page
from widgets.group import Group
from widgets.row import Row
from widgets.slider_row import SliderRow

from services.fonts import FontService


class FontsPage(Page):

    def __init__(self, navigator):

        super().__init__(
            navigator,
            "Fuentes",
            "Selecciona la fuente del sistema",
            parent_page="appearance"
        )

        self.navigator = navigator

        #
        # Escala
        #

        scale_group = Group(
            "Escala de fuentes"
        )

        self.scale_slider = SliderRow(
            title="Escala",
            subtitle="Tamano relativo del texto",
            value=FontService.scale() * 100.0,
            minimum=80.0,
            maximum=150.0,
            step=5.0,
            callback=self.on_scale_changed
        )

        scale_group.add(self.scale_slider)

        self.add(scale_group)

        #
        # Fuentes
        #

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

        self.add(group)

    def select(self, font):

        FontService.set(font)

        self.navigator.show_page("appearance")

    def on_scale_changed(self, slider):

        FontService.set_scale(
            slider.get_value() / 100.0
        )
