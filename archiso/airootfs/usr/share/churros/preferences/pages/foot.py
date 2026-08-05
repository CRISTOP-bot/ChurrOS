import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GLib

from widgets.page import Page
from widgets.group import Group
from widgets.combo_row import ComboRow
from widgets.slider_row import SliderRow
from widgets.switch_row import SwitchRow
from widgets.row import Row

from services.dotfiles.foot_config import FootConfig


class FootPage(Page):

    def __init__(self, navigator):

        super().__init__(
            navigator,
            "Foot",
            "Configura el terminal (fuente, cursor, padding, bell)",
            parent_page="appearance"
        )

        self._pending = False

        self.values = {
            "font": FootConfig.get_font(),
            "pad": FootConfig.get_pad(),
            "cursor_style": FootConfig.get_cursor_style(),
            "cursor_blink": FootConfig.get_cursor_blink(),
            "bell": FootConfig.get_bell(),
            "hide_when_typing": FootConfig.get_hide_when_typing(),
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

        sizes = [str(s) for s in range(8, 22)]

        try:
            current_font = self.values["font"]
            current_family, _, current_size_full = current_font.partition(":size=")
            current_size = current_size_full.split(":")[0] if current_size_full else "10"
        except Exception:
            current_family = font_families[0]
            current_size = "10"

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

        pad_group = Group("Padding")

        try:
            h, _, v = self.values["pad"].lower().partition("x")
            h_val = int(h)
            v_val = int(v) if v else h_val
        except Exception:
            h_val, v_val = 8, 8

        self.pad_h_slider = SliderRow(
            title="Padding horizontal",
            value=float(h_val),
            minimum=0,
            maximum=64,
            step=1,
            callback=lambda *_: self._schedule_apply()
        )

        self.pad_v_slider = SliderRow(
            title="Padding vertical",
            value=float(v_val),
            minimum=0,
            maximum=64,
            step=1,
            callback=lambda *_: self._schedule_apply()
        )

        pad_group.add(self.pad_h_slider)
        pad_group.add(self.pad_v_slider)
        self.add(pad_group)

        cursor_group = Group("Cursor")

        self.cursor_style_combo = ComboRow(
            title="Estilo",
            values=["block", "underline", "beam"],
            selected=self.values["cursor_style"],
            callback=lambda *_: self._schedule_apply()
        )

        self.cursor_blink_switch = SwitchRow(
            title="Parpadeo",
            active=self.values["cursor_blink"],
            callback=lambda *_: self._schedule_apply()
        )

        cursor_group.add(self.cursor_style_combo)
        cursor_group.add(self.cursor_blink_switch)
        self.add(cursor_group)

        behavior_group = Group("Comportamiento")

        self.bell_switch = SwitchRow(
            title="Campana urgente",
            subtitle="Notifica visualmente cuando llega un beep",
            active=self.values["bell"],
            callback=lambda *_: self._schedule_apply()
        )

        self.hide_when_typing_switch = SwitchRow(
            title="Ocultar raton al teclear",
            active=self.values["hide_when_typing"],
            callback=lambda *_: self._schedule_apply()
        )

        behavior_group.add(self.bell_switch)
        behavior_group.add(self.hide_when_typing_switch)
        self.add(behavior_group)

        actions_group = Group("Acciones")

        reload_row = Row(
            title="Recargar Foot",
            subtitle="Aplica los cambios a las terminales abiertas",
            icon="terminal.svg",
            callback=lambda *_: FootConfig.reload()
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

                FootConfig.set_font(font)
                FootConfig.set_pad(
                    "{}x{}".format(
                        int(self.pad_h_slider.get_value()),
                        int(self.pad_v_slider.get_value())
                    )
                )
                FootConfig.set_cursor(
                    self.cursor_style_combo.value(),
                    self.cursor_blink_switch.get_active()
                )
                FootConfig.set_bell(self.bell_switch.get_active())
                FootConfig.set_hide_when_typing(
                    self.hide_when_typing_switch.get_active()
                )

                FootConfig.reload()

            except Exception as exc:

                print("[foot] apply fallo:", exc)

        GLib.timeout_add(400, apply)
