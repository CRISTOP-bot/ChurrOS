import sys
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PREF = os.path.abspath(os.path.join(ROOT, "preferences"))

sys.path.insert(0, ROOT)
sys.path.insert(0, PREF)

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GLib

from widgets.page import Page
from widgets.group import Group
from widgets.slider_row import SliderRow
from widgets.switch_row import SwitchRow
from widgets.combo_row import ComboRow
from widgets.color_picker import ColorPickerRow
from widgets.row import Row

from services.dotfiles.mako_config import MakoConfig


class MakoPage(Page):

    def __init__(self, navigator):

        super().__init__(
            navigator,
            "Mako",
            "Configura las notificaciones (fuente, colores, bordes, posicion)",
            parent_page="appearance"
        )

        self._pending = False

        try:

            self.values = {
                "font": MakoConfig.get_font(),
                "background_color": MakoConfig.get_background_color(),
                "text_color": MakoConfig.get_text_color(),
                "border_color": MakoConfig.get_border_color(),
                "border_size": MakoConfig.get_border_size(),
                "border_radius": MakoConfig.get_border_radius(),
                "padding": MakoConfig.get_padding(),
                "margin": MakoConfig.get_margin(),
                "default_timeout": MakoConfig.get_default_timeout(),
                "width": MakoConfig.get_width(),
                "anchor": MakoConfig.get_anchor(),
                "markup": MakoConfig.get_markup(),
                "actions": MakoConfig.get_actions(),
                "icons": MakoConfig.get_icons(),
                "history": MakoConfig.get_history(),
                "max_icon_size": MakoConfig.get_max_icon_size(),
            }

        except Exception:

            self.values = MakoConfig.DEFAULTS.copy()
            self.values["background_color"] = "#1e1e2e"
            self.values["text_color"] = "#cdd6f4"
            self.values["border_color"] = "#f97316"
            self.values["padding"] = "12,16"

        self._build()

    def _build(self):

        #
        # Tipografia
        #

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

        sizes = [str(s) for s in range(8, 22)]

        try:
            current_font = self.values["font"]
            current_family, _, current_size_full = current_font.partition(
                ":size="
            )
            current_size = current_size_full.split(":")[0] \
                if current_size_full else "11"
        except Exception:
            current_family = font_families[0]
            current_size = "11"

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

        #
        # Colores
        #

        colors_group = Group("Colores")

        self.background_picker = ColorPickerRow(
            title="Fondo",
            value=self.values["background_color"],
            callback=lambda *_: self._schedule_apply()
        )

        self.text_picker = ColorPickerRow(
            title="Texto",
            value=self.values["text_color"],
            callback=lambda *_: self._schedule_apply()
        )

        self.border_color_picker = ColorPickerRow(
            title="Borde",
            value=self.values["border_color"],
            callback=lambda *_: self._schedule_apply()
        )

        colors_group.add(self.background_picker)
        colors_group.add(self.text_picker)
        colors_group.add(self.border_color_picker)

        self.add(colors_group)

        #
        # Bordes
        #

        borders_group = Group("Bordes")

        self.border_size_slider = SliderRow(
            title="Grosor del borde",
            subtitle="Ancho en pixeles (0 = sin borde)",
            value=float(self.values["border_size"]),
            minimum=0,
            maximum=8,
            step=1,
            callback=lambda *_: self._schedule_apply()
        )

        self.border_radius_slider = SliderRow(
            title="Radio de las esquinas",
            subtitle="Redondez en pixeles",
            value=float(self.values["border_radius"]),
            minimum=0,
            maximum=24,
            step=1,
            callback=lambda *_: self._schedule_apply()
        )

        borders_group.add(self.border_size_slider)
        borders_group.add(self.border_radius_slider)

        self.add(borders_group)

        #
        # Disposicion
        #

        layout_group = Group("Disposicion")

        anchors = [
            "top-right",
            "top-center",
            "top-left",
            "bottom-right",
            "bottom-center",
            "bottom-left",
            "center",
        ]

        self.anchor_combo = ComboRow(
            title="Posicion",
            values=anchors,
            selected=self.values["anchor"],
            callback=lambda *_: self._schedule_apply()
        )

        layout_group.add(self.anchor_combo)

        self.width_slider = SliderRow(
            title="Ancho",
            subtitle="Ancho de las notificaciones (px)",
            value=float(self.values["width"]),
            minimum=200,
            maximum=600,
            step=10,
            callback=lambda *_: self._schedule_apply()
        )

        layout_group.add(self.width_slider)

        self.margin_slider = SliderRow(
            title="Margen exterior",
            subtitle="Separacion desde el borde de la pantalla (px)",
            value=float(self.values["margin"]),
            minimum=0,
            maximum=64,
            step=1,
            callback=lambda *_: self._schedule_apply()
        )

        layout_group.add(self.margin_slider)

        self.add(layout_group)

        #
        # Padding
        #

        padding_group = Group("Padding interno")

        try:
            parts = [p.strip() for p in self.values["padding"].split(",")]
            pad_h = int(parts[0])
            pad_v = int(parts[1]) if len(parts) > 1 else pad_h
        except Exception:
            pad_h, pad_v = 12, 16

        self.pad_v_slider = SliderRow(
            title="Padding vertical",
            value=float(pad_v),
            minimum=0,
            maximum=32,
            step=1,
            callback=lambda *_: self._schedule_apply()
        )

        self.pad_h_slider = SliderRow(
            title="Padding horizontal",
            value=float(pad_h),
            minimum=0,
            maximum=48,
            step=1,
            callback=lambda *_: self._schedule_apply()
        )

        padding_group.add(self.pad_v_slider)
        padding_group.add(self.pad_h_slider)

        self.add(padding_group)

        #
        # Comportamiento
        #

        behavior_group = Group("Comportamiento")

        self.timeout_slider = SliderRow(
            title="Tiempo visible (segundos)",
            subtitle="Duracion por defecto antes de ocultar",
            value=float(self.values["default_timeout"]) / 1000.0,
            minimum=1.0,
            maximum=30.0,
            step=1.0,
            callback=lambda *_: self._schedule_apply()
        )

        behavior_group.add(self.timeout_slider)

        self.markup_switch = SwitchRow(
            title="Permitir markup",
            subtitle="Interpreta etiquetas HTML en el texto",
            active=self.values["markup"],
            callback=lambda *_: self._schedule_apply()
        )

        behavior_group.add(self.markup_switch)

        self.actions_switch = SwitchRow(
            title="Acciones",
            subtitle="Permite botones accionables en las notificaciones",
            active=self.values["actions"],
            callback=lambda *_: self._schedule_apply()
        )

        behavior_group.add(self.actions_switch)

        self.icons_switch = SwitchRow(
            title="Iconos",
            subtitle="Muestra el icono de la aplicacion",
            active=self.values["icons"],
            callback=lambda *_: self._schedule_apply()
        )

        behavior_group.add(self.icons_switch)

        self.history_switch = SwitchRow(
            title="Historial",
            subtitle="Guarda notificaciones pasadas",
            active=self.values["history"],
            callback=lambda *_: self._schedule_apply()
        )

        behavior_group.add(self.history_switch)

        self.max_icon_slider = SliderRow(
            title="Tamano maximo de icono",
            subtitle="En pixeles",
            value=float(self.values["max_icon_size"]),
            minimum=16,
            maximum=128,
            step=4,
            callback=lambda *_: self._schedule_apply()
        )

        behavior_group.add(self.max_icon_slider)

        self.add(behavior_group)

        #
        # Acciones
        #

        actions_group = Group("Acciones")

        reload_row = Row(
            title="Recargar Mako",
            subtitle="Aplica los cambios a las notificaciones",
            icon="mako.svg",
            callback=lambda *_: MakoConfig.reload()
        )

        actions_group.add(reload_row)

        self.add(actions_group)

        #
        # Estado de notificaciones (Do Not Disturb)
        #

        state_group = Group("Estado actual")

        self.dnd_switch = SwitchRow(
            title="No molestar",
            subtitle="Silencia todas las notificaciones entrantes",
            active=self._is_dnd_active(),
            callback=lambda v: self._on_dnd_toggle(v)
        )

        state_group.add(self.dnd_switch)

        self.dnd_status = Row(
            title="Estado de makoctl",
            subtitle=self._dnd_status_text(),
            icon="mako.svg",
            value=None
        )

        state_group.add(self.dnd_status)

        self.add(state_group)

    def _is_dnd_active(self):

        try:

            import subprocess

            r = subprocess.run(
                ["makoctl", "mode"],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                timeout=2
            )

            output = r.stdout.decode("utf-8", errors="replace")

            return "do-not-disturb" in output

        except Exception:

            return False

    def _dnd_status_text(self):

        try:

            import subprocess

            r = subprocess.run(
                ["makoctl", "mode"],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                timeout=2
            )

            output = r.stdout.decode("utf-8", errors="replace").strip()

            if output:
                return "Modos activos: " + output

            return "Sin modos activos"

        except Exception as exc:

            return "makoctl no disponible: " + str(exc)

    def _on_dnd_toggle(self, active):

        try:

            import subprocess

            r = subprocess.run(
                ["makoctl", "mode"],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                timeout=2
            )

            current = r.stdout.decode("utf-8", errors="replace")

            is_active = "do-not-disturb" in current

            if active and not is_active:

                subprocess.Popen(
                    ["makoctl", "mode", "-a", "do-not-disturb"]
                )

            elif not active and is_active:

                subprocess.Popen(
                    ["makoctl", "mode", "-r", "do-not-disturb"]
                )

            GLib.timeout_add(
                300,
                lambda: (
                    self.dnd_status.set_subtitle(self._dnd_status_text()),
                    False
                )[-1]
            )

        except Exception as exc:

            print("[mako] DND toggle fallo:", exc)

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

                MakoConfig.set_font(font)

                MakoConfig.set_appearance(
                    background_color=self.background_picker.get_value(),
                    text_color=self.text_picker.get_value(),
                    border_color=self.border_color_picker.get_value(),
                    border_size=int(self.border_size_slider.get_value()),
                    border_radius=int(self.border_radius_slider.get_value())
                )

                MakoConfig.set_layout(
                    padding="{},{}".format(
                        int(self.pad_h_slider.get_value()),
                        int(self.pad_v_slider.get_value())
                    ),
                    margin=int(self.margin_slider.get_value()),
                    default_timeout=int(
                        self.timeout_slider.get_value() * 1000
                    ),
                    width=int(self.width_slider.get_value())
                )

                MakoConfig.set_anchor(self.anchor_combo.value())

                MakoConfig.set_behaviors(
                    markup=self.markup_switch.get_active(),
                    actions=self.actions_switch.get_active(),
                    icons=self.icons_switch.get_active(),
                    history=self.history_switch.get_active(),
                    max_icon_size=int(self.max_icon_slider.get_value())
                )

                MakoConfig.reload()

            except Exception as exc:

                print("[mako] apply fallo:", exc)

        GLib.timeout_add(400, apply)
