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
from widgets.color_picker import ColorPickerRow
from widgets.row import Row

from services.dotfiles.niri_config import NiriConfig


class NiriPage(Page):

    def __init__(self, navigator):

        super().__init__(
            navigator,
            "Niri",
            "Configura el compositor (disposicion, bordes, blur, ventanas)",
            parent_page="appearance"
        )

        self._pending = False

        try:

            self.values = {
                "gaps": NiriConfig.get_gaps(),
                "prefer_no_csd": NiriConfig.get_prefer_no_csd(),
                "border": NiriConfig.get_border(),
                "focus_ring": NiriConfig.get_focus_ring(),
                "blur": NiriConfig.get_blur(),
                "animations": NiriConfig.get_animations(),
            }

        except Exception:

            self.values = {
                "gaps": 8,
                "prefer_no_csd": True,
                "border": {
                    "on": True,
                    "width": 2,
                    "active_color": "#DE8636",
                    "inactive_color": "#766561"
                },
                "focus_ring": False,
                "blur": {
                    "passes": 2,
                    "offset": 2,
                    "noise": 0,
                    "saturation": 1.2
                },
                "animations": True
            }

        self._build()

    def _build(self):

        #
        # Disposicion
        #

        layout_group = Group("Disposicion")

        self.gaps_slider = SliderRow(
            title="Espacio entre ventanas",
            subtitle="Gaps (px)",
            value=float(self.values["gaps"]),
            minimum=0,
            maximum=32,
            step=1,
            callback=lambda *_: self._schedule_apply()
        )

        layout_group.add(self.gaps_slider)

        self.add(layout_group)

        #
        # Bordes
        #

        border_group = Group("Bordes de ventana")

        border = self.values["border"]

        self.border_switch = SwitchRow(
            title="Mostrar bordes",
            subtitle="Activa el borde coloreado alrededor de la ventana enfocada",
            active=border["on"],
            callback=lambda v: self._on_border_toggle(v)
        )

        border_group.add(self.border_switch)

        self.border_width_slider = SliderRow(
            title="Grosor del borde",
            subtitle="Ancho en pixeles",
            value=float(border["width"]),
            minimum=1,
            maximum=8,
            step=1,
            callback=lambda *_: self._schedule_apply()
        )

        border_group.add(self.border_width_slider)

        self.border_active_picker = ColorPickerRow(
            title="Color del borde activo",
            value=border["active_color"],
            callback=lambda c: self._schedule_apply()
        )

        border_group.add(self.border_active_picker)

        self.border_inactive_picker = ColorPickerRow(
            title="Color del borde inactivo",
            value=border["inactive_color"],
            callback=lambda c: self._schedule_apply()
        )

        border_group.add(self.border_inactive_picker)

        self.add(border_group)

        #
        # Focus ring
        #

        fr_group = Group("Anillo de foco")

        self.focus_ring_switch = SwitchRow(
            title="Anillo de foco",
            subtitle="Muestra un anillo alrededor de la ventana enfocada",
            active=self.values["focus_ring"],
            callback=lambda v: self._on_focus_ring_toggle(v)
        )

        fr_group.add(self.focus_ring_switch)

        self.add(fr_group)

        #
        # Blur
        #

        blur = self.values["blur"]

        blur_group = Group("Desenfoque (blur)")

        self.blur_passes_slider = SliderRow(
            title="Pasadas",
            subtitle="Mas pasadas = mas desenfoque (tambien mas coste GPU)",
            value=float(blur["passes"]),
            minimum=0,
            maximum=6,
            step=1,
            callback=lambda *_: self._schedule_apply()
        )

        blur_group.add(self.blur_passes_slider)

        self.blur_offset_slider = SliderRow(
            title="Desplazamiento",
            value=float(blur["offset"]),
            minimum=0,
            maximum=16,
            step=1,
            callback=lambda *_: self._schedule_apply()
        )

        blur_group.add(self.blur_offset_slider)

        self.blur_noise_slider = SliderRow(
            title="Ruido",
            subtitle="0 = sin ruido, 1 = maximo",
            value=float(blur["noise"]),
            minimum=0.0,
            maximum=1.0,
            step=0.05,
            callback=lambda *_: self._schedule_apply()
        )

        blur_group.add(self.blur_noise_slider)

        self.blur_saturation_slider = SliderRow(
            title="Saturacion",
            subtitle="1.0 = sin cambio",
            value=float(blur["saturation"]),
            minimum=0.0,
            maximum=2.0,
            step=0.05,
            callback=lambda *_: self._schedule_apply()
        )

        blur_group.add(self.blur_saturation_slider)

        self.add(blur_group)

        #
        # Animaciones
        #

        animations_group = Group("Animaciones")

        self.animations_switch = SwitchRow(
            title="Animaciones",
            subtitle="Desactiva todas las transiciones de niri (mas agil en hardware modesto)",
            active=self.values["animations"],
            callback=lambda v: self._on_animations_toggle(v)
        )

        animations_group.add(self.animations_switch)

        self.window_open_slider = SliderRow(
            title="Apertura de ventanas",
            subtitle="Duracion en ms (window-open)",
            value=float(NiriConfig.get_animation_duration("window-open", 250)),
            minimum=0,
            maximum=1000,
            step=50,
            callback=lambda *_: self._schedule_apply()
        )

        animations_group.add(self.window_open_slider)

        self.workspace_switch_slider = SliderRow(
            title="Cambio de workspace",
            subtitle="Duracion en ms (workspace-switch)",
            value=float(NiriConfig.get_animation_duration("workspace-switch", 250)),
            minimum=0,
            maximum=1000,
            step=50,
            callback=lambda *_: self._schedule_apply()
        )

        animations_group.add(self.workspace_switch_slider)

        self.add(animations_group)

        #
        # Ventanas
        #

        windows_group = Group("Ventanas")

        self.prefer_no_csd_switch = SwitchRow(
            title="Sin decoraciones del lado del cliente (CSD)",
            subtitle="Pide a las apps que omitan sus propias decoraciones de ventana",
            active=self.values["prefer_no_csd"],
            callback=lambda v: self._on_csd_toggle(v)
        )

        windows_group.add(self.prefer_no_csd_switch)

        self.add(windows_group)

        #
        # Acciones
        #

        actions_group = Group("Acciones")

        reload_row = Row(
            title="Recargar Niri",
            subtitle="Aplica los cambios forzando una transicion de pantalla",
            icon="niri.svg",
            callback=lambda *_: NiriConfig.reload()
        )

        actions_group.add(reload_row)

        self.add(actions_group)

    def _on_border_toggle(self, value):

        self.values["border"]["on"] = value

        NiriConfig.set_border(
            on=value,
            width=int(self.border_width_slider.get_value()),
            active_color=self.border_active_picker.get_value(),
            inactive_color=self.border_inactive_picker.get_value()
        )

        NiriConfig.reload()

    def _on_focus_ring_toggle(self, value):

        self.values["focus_ring"] = value

        NiriConfig.set_focus_ring(value)

        NiriConfig.reload()

    def _on_csd_toggle(self, value):

        self.values["prefer_no_csd"] = value

        NiriConfig.set_prefer_no_csd(value)

        NiriConfig.reload()

    def _on_animations_toggle(self, value):

        self.values["animations"] = value

        NiriConfig.set_animations(value)

        NiriConfig.reload()

    def _schedule_apply(self):

        if self._pending:

            return

        self._pending = True

        def apply():

            self._pending = False

            try:

                NiriConfig.set_gaps(
                    int(self.gaps_slider.get_value())
                )

                border = self.values["border"]

                NiriConfig.set_border(
                    on=border["on"],
                    width=int(self.border_width_slider.get_value()),
                    active_color=self.border_active_picker.get_value(),
                    inactive_color=self.border_inactive_picker.get_value()
                )

                NiriConfig.set_blur(
                    passes=int(self.blur_passes_slider.get_value()),
                    offset=int(self.blur_offset_slider.get_value()),
                    noise=float(self.blur_noise_slider.get_value()),
                    saturation=float(self.blur_saturation_slider.get_value())
                )

                NiriConfig.reload()

            except Exception as exc:

                print("[niri] apply fallo:", exc)

        GLib.timeout_add(400, apply)
