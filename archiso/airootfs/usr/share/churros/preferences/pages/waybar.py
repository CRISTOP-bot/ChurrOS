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
from widgets.combo_row import ComboRow
from widgets.slider_row import SliderRow
from widgets.switch_row import SwitchRow
from widgets.row import Row
from widgets.color_picker import ColorPickerRow

from services.waybar import WaybarService


AVAILABLE_MODULES = [
    "niri/workspaces",
    "clock",
    "cpu",
    "memory",
    "disk",
    "battery",
    "backlight",
    "network",
    "bluetooth",
    "pulseaudio",
    "tray",
    "idle_inhibitor",
    "mpris",
    "custom/launcher",
    "custom/control-center",
    "custom/settings",
    "custom/dnd",
    "custom/screenrecording-indicator",
    "custom/screenrecording-toggle",
    "custom/sep",
]


class WaybarPage(Page):

    def __init__(self, navigator):

        super().__init__(
            navigator,
            "Waybar",
            "Personaliza la barra superior",
            parent_page="appearance"
        )

        self._pending = False

        self.module_popovers = {}

        try:
            self.values = WaybarService.get()
        except Exception:
            self.values = WaybarService.defaults()

        self._build()

    def _build(self):

        layout_group = Group("Posicion y tamano")

        self.layer_combo = ComboRow(
            title="Capa",
            values=["top", "overlay", "bottom"],
            selected=self.values["layer"],
            callback=lambda *_: self._on_change("full")
        )

        self.position_combo = ComboRow(
            title="Posicion",
            values=["top", "bottom", "left", "right"],
            selected=self.values["position"],
            callback=lambda *_: self._on_change("full")
        )

        self.height_slider = SliderRow(
            title="Altura",
            value=float(self.values["height"]),
            minimum=20,
            maximum=80,
            step=1,
            callback=lambda *_: self._on_change("full")
        )

        self.spacing_slider = SliderRow(
            title="Espaciado",
            subtitle="Espacio entre modulos",
            value=float(self.values["spacing"]),
            minimum=0,
            maximum=16,
            step=1,
            callback=lambda *_: self._on_change("full")
        )

        layout_group.add(self.layer_combo)
        layout_group.add(self.position_combo)
        layout_group.add(self.height_slider)
        layout_group.add(self.spacing_slider)

        self.add(layout_group)

        typography_group = Group("Tipografia")

        self.font_size_slider = SliderRow(
            title="Tamano de fuente",
            value=float(self.values["font-size"]),
            minimum=10,
            maximum=24,
            step=1,
            callback=lambda *_: self._on_change("style")
        )

        font_families = [
            "JetBrainsMono Nerd Font",
            "JetBrains Mono",
            "Inter",
            "Cantarell",
            "Noto Sans",
            "DejaVu Sans",
            "Monospace",
        ]

        self.font_family_combo = ComboRow(
            title="Familia tipografica",
            values=font_families,
            selected=self.values.get("font-family", font_families[0]),
            callback=lambda *_: self._on_change("style")
        )

        typography_group.add(self.font_size_slider)
        typography_group.add(self.font_family_combo)

        self.add(typography_group)

        colors_group = Group("Colores")

        self.bg_picker = ColorPickerRow(
            title="Fondo",
            value=self.values["background"],
            callback=lambda c: self._on_change("style")
        )

        self.fg_picker = ColorPickerRow(
            title="Texto",
            value=self.values["foreground"],
            callback=lambda c: self._on_change("style")
        )

        self.accent_picker = ColorPickerRow(
            title="Acento",
            value=self.values["accent"],
            callback=lambda c: self._on_change("style")
        )

        self.bg_alpha_slider = SliderRow(
            title="Opacidad del fondo",
            subtitle="0 = transparente, 1 = solido",
            value=float(self.values.get("background-alpha", 0.9)),
            minimum=0.0,
            maximum=1.0,
            step=0.05,
            callback=lambda *_: self._on_change("style")
        )

        colors_group.add(self.bg_picker)
        colors_group.add(self.fg_picker)
        colors_group.add(self.accent_picker)
        colors_group.add(self.bg_alpha_slider)

        self.add(colors_group)

        modules_group = Group("Modulos (clic para mover)")

        self.module_states = {
            "left": list(self.values.get("modules-left", [])),
            "center": list(self.values.get("modules-center", [])),
            "right": list(self.values.get("modules-right", [])),
        }

        self.module_rows = {}

        for position in ("left", "center", "right"):

            for module in self.module_states[position]:

                row = Row(
                    title=module,
                    subtitle=position,
                    icon="waybar.svg",
                    callback=lambda *_, m=module: self._show_module_menu(m)
                )

                modules_group.add(row)
                self.module_rows[module] = (row, position)

        self.add(modules_group)

        actions_group = Group("Acciones")

        reload_row = Row(
            title="Recargar waybar",
            subtitle="Aplica los cambios",
            icon="waybar.svg",
            callback=lambda *_: WaybarService.reload()
        )

        reset_row = Row(
            title="Restablecer defaults",
            subtitle="Vuelve a la configuracion original de ChurrOS",
            icon="waybar.svg",
            callback=lambda *_: self._reset_defaults()
        )

        actions_group.add(reload_row)
        actions_group.add(reset_row)

        self.add(actions_group)

    def _show_module_menu(self, module):

        row, current = self.module_rows.get(module, (None, None))

        if row is None:
            return

        for old in list(self.module_popovers.values()):

            try:
                old.popdown()

            except Exception:
                pass

        menu = Gtk.Popover()
        menu.set_has_arrow(True)
        menu.set_autohide(True)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        vbox.set_margin_top(8)
        vbox.set_margin_bottom(8)
        vbox.set_margin_start(8)
        vbox.set_margin_end(8)

        positions = [
            ("left",   "Mover a izquierda"),
            ("center", "Mover a centro"),
            ("right",  "Mover a derecha"),
            ("remove", "Quitar de la barra"),
        ]

        has_action = False

        for target, label in positions:

            if target == current:
                continue

            btn = Gtk.Button(label=label)
            btn.set_has_frame(False)
            btn.set_halign(Gtk.Align.FILL)

            btn.connect(
                "clicked",
                lambda *_, t=target, m=module: (menu.popdown(), self._move_module(m, t))
            )

            vbox.append(btn)
            has_action = True

        if not has_action and current is not None:

            noop = Gtk.Label(label="Sin acciones")
            noop.set_margin_top(8)
            noop.set_margin_bottom(8)
            vbox.append(noop)

        if current is None:

            btn = Gtk.Button(label="Agregar a la barra")
            btn.set_has_frame(False)
            btn.set_halign(Gtk.Align.FILL)
            btn.connect("clicked", lambda *_, m=module: (menu.popdown(), self._move_module(m, "left")))
            vbox.append(btn)

        menu.set_child(vbox)

        try:
            menu.set_parent(row)
        except Exception:
            pass

        try:
            menu.popup()
        except Exception as exc:
            print("[waybar] popover fallo:", exc)
            return

        self.module_popovers[module] = menu

    def _move_module(self, module, target):

        for position in list(self.module_states.keys()):

            if module in self.module_states[position]:

                self.module_states[position].remove(module)

                break

        if target in ("left", "center", "right"):

            if module not in self.module_states[target]:
                self.module_states[target].append(module)

        self._on_change("full")

        self._on_change()

    def _on_change(self, reload_kind="style"):

        if self._pending:
            return

        self._pending = True

        def apply():

            self._pending = False

            values = {
                "layer": self.layer_combo.value(),
                "position": self.position_combo.value(),
                "spacing": int(self.spacing_slider.get_value()),
                "height": int(self.height_slider.get_value()),
                "font-size": int(self.font_size_slider.get_value()),
                "font-family": self.font_family_combo.value(),
                "background": self.bg_picker.get_value(),
                "foreground": self.fg_picker.get_value(),
                "accent": self.accent_picker.get_value(),
                "background-alpha": self.bg_alpha_slider.get_value(),
                "modules-left": self.module_states["left"],
                "modules-center": self.module_states["center"],
                "modules-right": self.module_states["right"],
            }

            try:
                WaybarService.set(values, reload_kind=reload_kind)
            except Exception as exc:
                print("[waybar] apply fallo:", exc)

        GLib.timeout_add(400, apply)

    def _reset_defaults(self):

        for old in list(self.module_popovers.values()):

            try:
                old.popdown()

            except Exception:
                pass

        self.module_popovers.clear()

        WaybarService.reset()

        try:
            self.values = WaybarService.get()
        except Exception:
            self.values = WaybarService.defaults()

        content = self.content
        child = content.get_first_child()
        while child is not None:
            nxt = child.get_next_sibling()
            content.remove(child)
            child = nxt

        self._build()

        WaybarService.reload(full_restart=True)
