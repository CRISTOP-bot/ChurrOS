import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GLib

from widgets.page import Page
from widgets.group import Group
from widgets.combo_row import ComboRow
from widgets.slider_row import SliderRow
from widgets.row import Row

from services.dotfiles.fuzzel_config import FuzzelConfig


class FuzzelPage(Page):

    def __init__(self, navigator):

        super().__init__(
            navigator,
            "Fuzzel",
            "Configura el launcher (fuente, layout, colores)",
            parent_page="appearance"
        )

        self._pending = False

        self.values = {
            "font": FuzzelConfig.get_font(),
            "icon_theme": FuzzelConfig.get_icon_theme(),
            "width": FuzzelConfig.get_width(),
            "lines": FuzzelConfig.get_lines(),
            "h_pad": FuzzelConfig.get_horizontal_pad(),
            "v_pad": FuzzelConfig.get_vertical_pad(),
            "inner_pad": FuzzelConfig.get_inner_pad(),
            "line_height": FuzzelConfig.get_line_height(),
            "letter_spacing": FuzzelConfig.get_letter_spacing(),
        }

        self._build()

    def _build(self):

        font_group = Group("Tipografia")

        font_families = [
            "JetBrainsMono Nerd Font",
            "JetBrains Mono",
            "FiraCode Nerd Font",
            "Inter",
            "Cantarell",
            "Hack",
            "Monospace",
        ]

        sizes = [str(s) for s in range(8, 24)]

        try:
            current_font = self.values["font"]
            current_family, _, current_size_full = current_font.partition(":size=")
            current_size = current_size_full.split(":")[0] if current_size_full else "13"
        except Exception:
            current_family = font_families[0]
            current_size = "13"

        self.font_family_combo = ComboRow(
            title="Familia",
            values=font_families,
            selected=current_family,
            callback=lambda *_: self._schedule_apply()
        )

        self.font_size_combo = ComboRow(
            title="Tamano",
            values=sizes,
            selected=current_size,
            callback=lambda *_: self._schedule_apply()
        )

        font_group.add(self.font_family_combo)
        font_group.add(self.font_size_combo)
        self.add(font_group)

        layout_group = Group("Disposicion")

        self.width_slider = SliderRow(
            title="Ancho (caracteres)",
            value=float(self.values["width"]),
            minimum=20,
            maximum=120,
            step=1,
            callback=lambda *_: self._schedule_apply()
        )

        self.lines_slider = SliderRow(
            title="Lineas visibles",
            value=float(self.values["lines"]),
            minimum=4,
            maximum=40,
            step=1,
            callback=lambda *_: self._schedule_apply()
        )

        self.h_pad_slider = SliderRow(
            title="Padding horizontal",
            value=float(self.values["h_pad"]),
            minimum=0,
            maximum=120,
            step=2,
            callback=lambda *_: self._schedule_apply()
        )

        self.v_pad_slider = SliderRow(
            title="Padding vertical",
            value=float(self.values["v_pad"]),
            minimum=0,
            maximum=80,
            step=2,
            callback=lambda *_: self._schedule_apply()
        )

        self.inner_pad_slider = SliderRow(
            title="Padding interno",
            value=float(self.values["inner_pad"]),
            minimum=0,
            maximum=40,
            step=1,
            callback=lambda *_: self._schedule_apply()
        )

        self.line_height_slider = SliderRow(
            title="Altura de linea",
            value=float(self.values["line_height"]),
            minimum=14,
            maximum=64,
            step=1,
            callback=lambda *_: self._schedule_apply()
        )

        self.letter_spacing_slider = SliderRow(
            title="Espaciado entre letras",
            value=float(self.values["letter_spacing"]),
            minimum=0,
            maximum=8,
            step=1,
            callback=lambda *_: self._schedule_apply()
        )

        layout_group.add(self.width_slider)
        layout_group.add(self.lines_slider)
        layout_group.add(self.h_pad_slider)
        layout_group.add(self.v_pad_slider)
        layout_group.add(self.inner_pad_slider)
        layout_group.add(self.line_height_slider)
        layout_group.add(self.letter_spacing_slider)
        self.add(layout_group)

        icon_group = Group("Iconos")

        icon_themes = [
            "",
            "Papirus-Dark",
            "Papirus",
            "Adwaita",
            "breeze-icons",
            "Gruvbox-Plus-Dark",
        ]

        self.icon_theme_combo = ComboRow(
            title="Tema de iconos",
            subtitle="Vacio = sin iconos",
            values=icon_themes,
            selected=self.values["icon_theme"],
            callback=lambda *_: self._schedule_apply()
        )

        icon_group.add(self.icon_theme_combo)
        self.add(icon_group)

        actions_group = Group("Acciones")

        reload_row = Row(
            title="Reiniciar Fuzzel",
            subtitle="Cierra la instancia actual para que aplique cambios",
            icon="applications.svg",
            callback=lambda *_: FuzzelConfig.reload()
        )

        actions_group.add(reload_row)
        self.add(actions_group)

    def _schedule_apply(self):

        if self._pending:
            return

        self._pending = True

        def apply():

            self._pending = False

            try:

                font = "{}:size={}".format(
                    self.font_family_combo.value(),
                    self.font_size_combo.value()
                )

                FuzzelConfig.set_font(font)
                FuzzelConfig.set_icon_theme(self.icon_theme_combo.value())
                FuzzelConfig.set_layout(
                    int(self.width_slider.get_value()),
                    int(self.lines_slider.get_value()),
                    int(self.h_pad_slider.get_value()),
                    int(self.v_pad_slider.get_value()),
                    int(self.inner_pad_slider.get_value()),
                    int(self.line_height_slider.get_value()),
                    int(self.letter_spacing_slider.get_value())
                )

                FuzzelConfig.reload()

            except Exception as exc:

                print("[fuzzel] apply fallo:", exc)

        GLib.timeout_add(400, apply)
