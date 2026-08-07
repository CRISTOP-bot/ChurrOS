from widgets.page import Page
from widgets.group import Group
from widgets.row import Row
from widgets.slider_row import SliderRow

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GLib

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

        self._pending = False

        #
        # Preview
        #

        current = FontService.current()

        preview_group = Group("Vista previa")

        self.preview_label = Gtk.Label(
            label="La zorra marrona salta sobre el perro perezoso"
        )
        self.preview_label.add_css_class("fonts-preview")
        self.preview_label.set_margin_top(10)
        self.preview_label.set_margin_bottom(10)
        self.preview_label.set_margin_start(14)
        self.preview_label.set_margin_end(14)

        preview_group.add(self.preview_label)

        self.add(preview_group)

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
            callback=lambda *_: self._schedule_apply()
        )

        scale_group.add(self.scale_slider)

        self.add(scale_group)

        #
        # Fuentes
        #

        group = Group(
            "Fuentes instaladas"
        )

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

        self._refresh_preview()

        self.navigator.show_page("appearance")

    def _refresh_preview(self):

        scale = FontService.scale()
        self.preview_label.set_opacity(1.0)

    def _schedule_apply(self):

        if self._pending:
            return

        self._pending = True

        def apply():

            self._pending = False

            try:

                FontService.set_scale(
                    self.scale_slider.get_value() / 100.0
                )

            except Exception as exc:

                print("[fonts] apply fallo:", exc)

        GLib.timeout_add(400, apply)
