import os
import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GLib

from widgets.page import Page
from widgets.group import Group
from widgets.row import Row
from widgets.switch_row import SwitchRow
from widgets.slider_row import SliderRow
from widgets.combo_row import ComboRow
from widgets.color_picker import ColorPickerRow

from services.lock_screen import LockScreenService


class LockScreenPage(Page):

    def __init__(self, navigator):

        super().__init__(
            navigator,
            "Pantalla de bloqueo",
            "swaylock + swayidle: bloqueo automatico y estilo",
            parent_page="appearance"
        )

        self._pending = False

        self._build()

    def _build(self):

        if not LockScreenService.is_available():

            warn = Group("No disponible")

            warn.add(
                Row(
                    title="swaylock no esta instalado",
                    subtitle="Para personalizar el bloqueo instala el paquete swaylock",
                    icon="lock_screen.svg"
                )
            )

            self.add(warn)

            return

        #
        # Estado
        #

        state_group = Group("Estado")

        self.enabled_switch = SwitchRow(
            title="Bloqueo automatico",
            subtitle="Bloquea la pantalla tras un periodo de inactividad",
            active=LockScreenService.is_enabled(),
            callback=lambda v: self._on_enable_toggle(v)
        )

        state_group.add(self.enabled_switch)

        self.timeout_slider = SliderRow(
            title="Tiempo de inactividad",
            subtitle="Segundos hasta que se bloquee",
            value=float(LockScreenService.get("timeout_seconds", 600)),
            minimum=30,
            maximum=3600,
            step=30,
            callback=lambda *_: self._schedule_apply()
        )

        state_group.add(self.timeout_slider)

        self.lock_now_row = Row(
            title="Bloquear ahora",
            subtitle="Lanza swaylock al instante",
            icon="lock_screen.svg",
            callback=lambda *_: LockScreenService.lock_now()
        )

        state_group.add(self.lock_now_row)

        self.preview_row = Row(
            title="Previsualizar estilo",
            subtitle="Lanza swaylock con la configuracion actual",
            icon="lock_screen.svg",
            callback=lambda *_: LockScreenService.preview()
        )

        state_group.add(self.preview_row)

        self.add(state_group)

        #
        # Indicador
        #

        ind_group = Group("Indicador de progreso")

        self.indicator_combo = ComboRow(
            title="Tipo de indicador",
            subtitle="Como se muestra el estado al escribir",
            values=list(LockScreenService.INDICATORS),
            selected=LockScreenService.get("indicator", "auto"),
            callback=lambda *_: self._schedule_apply()
        )

        ind_group.add(self.indicator_combo)

        self.add(ind_group)

        #
        # Imagen de fondo
        #

        bg_group = Group("Fondo")

        self.use_current_row = Row(
            title="Usar fondo actual",
            subtitle="Pasa el wallpaper activo a swaylock (-i)",
            icon="wallpaper.svg"
        )

        self.current_wallpaper = LockScreenService.get("wallpaper_path", "")

        if self.current_wallpaper:

            self.use_current_row.set_subtitle(
                "Actual: " + self.current_wallpaper
            )

        self.use_current_row.connect(
            "clicked",
            lambda *_: self._on_use_current_wallpaper()
        )

        bg_group.add(self.use_current_row)

        self.custom_path_entry = Gtk.Entry()
        self.custom_path_entry.set_placeholder_text(
            "Ruta a una imagen personalizada"
        )
        self.custom_path_entry.set_margin_start(14)
        self.custom_path_entry.set_margin_end(14)
        self.custom_path_entry.set_margin_top(8)
        self.custom_path_entry.set_margin_bottom(8)

        bg_group.add(self.custom_path_entry)

        self.apply_path_row = Row(
            title="Aplicar ruta personalizada",
            subtitle="swaylock usara esta imagen al bloquear",
            icon="lock_screen.svg"
        )

        self.apply_path_row.connect(
            "clicked",
            lambda *_: self._on_apply_custom_path()
        )

        bg_group.add(self.apply_path_row)

        self.screenshot_switch = SwitchRow(
            title="Captura con blur",
            subtitle="swaylock captura el escritorio y difumina el fondo",
            active=bool(LockScreenService.get("screenshot", False)),
            callback=lambda *_: self._schedule_apply()
        )

        bg_group.add(self.screenshot_switch)

        self.add(bg_group)

        #
        # Animacion
        #

        anim_group = Group("Animacion")

        self.fade_in_slider = SliderRow(
            title="Fade-in",
            subtitle="Milisegundos hasta que aparezca el fondo",
            value=float(LockScreenService.get("fade_in", 200)),
            minimum=0,
            maximum=2000,
            step=50,
            callback=lambda *_: self._schedule_apply()
        )

        anim_group.add(self.fade_in_slider)

        self.grace_slider = SliderRow(
            title="Grace",
            subtitle="Milisegundos antes de empezar a autenticar",
            value=float(LockScreenService.get("grace", 0)),
            minimum=0,
            maximum=5000,
            step=50,
            callback=lambda *_: self._schedule_apply()
        )

        anim_group.add(self.grace_slider)

        self.add(anim_group)

        #
        # Tipografia
        #

        font_group = Group("Tipografia")

        fonts = [
            "JetBrainsMono Nerd Font",
            "JetBrains Mono",
            "FiraCode Nerd Font",
            "Inter",
            "Cantarell",
            "Hack",
            "Monospace",
        ]

        self.font_combo = ComboRow(
            title="Familia",
            values=fonts,
            selected=LockScreenService.get("font", "JetBrainsMono Nerd Font"),
            callback=lambda *_: self._schedule_apply()
        )

        font_group.add(self.font_combo)

        self.font_size_slider = SliderRow(
            title="Tamano",
            value=float(LockScreenService.get("font_size", 24)),
            minimum=12,
            maximum=64,
            step=1,
            callback=lambda *_: self._schedule_apply()
        )

        font_group.add(self.font_size_slider)

        self.add(font_group)

        #
        # Colores
        #

        colors_group = Group("Colores")

        self.ring_picker = ColorPickerRow(
            title="Anillo",
            subtitle="Color del indicador",
            value="#" + LockScreenService.get("ring_color", "7aa2f7ff"),
            callback=lambda *_: self._schedule_apply()
        )

        colors_group.add(self.ring_picker)

        self.inside_picker = ColorPickerRow(
            title="Interior",
            subtitle="Color dentro del indicador",
            value="#" + LockScreenService.get("inside_color", "00000088"),
            callback=lambda *_: self._schedule_apply()
        )

        colors_group.add(self.inside_picker)

        self.key_hl_picker = ColorPickerRow(
            title="Tecla resaltada",
            subtitle="Color al pulsar una tecla correcta",
            value="#" + LockScreenService.get("key_hl_color", "bb9af7ff"),
            callback=lambda *_: self._schedule_apply()
        )

        colors_group.add(self.key_hl_picker)

        self.bs_picker = ColorPickerRow(
            title="Backspace",
            subtitle="Color al pulsar backspace",
            value="#" + LockScreenService.get("bs_color", "f7768eff"),
            callback=lambda *_: self._schedule_apply()
        )

        colors_group.add(self.bs_picker)

        self.sep_picker = ColorPickerRow(
            title="Separador",
            subtitle="Borde del indicador",
            value="#" + LockScreenService.get("separator_color", "00000000"),
            callback=lambda *_: self._schedule_apply()
        )

        colors_group.add(self.sep_picker)

        self.add(colors_group)

    def _on_enable_toggle(self, value):

        LockScreenService.set_all(enabled=value)
        LockScreenService.apply()

    def _on_use_current_wallpaper(self):

        try:

            from services.wallpaper import WallpaperService

            current = WallpaperService.current()

            if not current or not os.path.isfile(current):

                self.use_current_row.set_subtitle(
                    "No hay wallpaper activo. Selecciona uno primero."
                )

                return

            LockScreenService.set_all(wallpaper_path=current)

            self.use_current_row.set_subtitle("Actual: " + current)

        except Exception as exc:

            self.use_current_row.set_subtitle("Error: " + str(exc))

    def _on_apply_custom_path(self):

        path = self.custom_path_entry.get_text().strip()

        if not path or not os.path.isfile(path):

            self.apply_path_row.set_subtitle(
                "La ruta no apunta a un archivo valido"
            )

            return

        LockScreenService.set_all(wallpaper_path=path)

        self.apply_path_row.set_subtitle("Aplicado: " + path)

    def _schedule_apply(self):

        if self._pending:
            return

        self._pending = True

        def apply():

            self._pending = False

            try:

                LockScreenService.set_all(

                    timeout_seconds=int(self.timeout_slider.get_value()),
                    indicator=self.indicator_combo.value() or "auto",
                    fade_in=int(self.fade_in_slider.get_value()),
                    grace=int(self.grace_slider.get_value()),
                    font=self.font_combo.value(),
                    font_size=int(self.font_size_slider.get_value()),
                    ring_color=self.ring_picker.get_value().lstrip("#"),
                    inside_color=self.inside_picker.get_value().lstrip("#"),
                    key_hl_color=self.key_hl_picker.get_value().lstrip("#"),
                    bs_color=self.bs_picker.get_value().lstrip("#"),
                    separator_color=self.sep_picker.get_value().lstrip("#"),
                    screenshot=self.screenshot_switch.get_active(),
                )

                LockScreenService.apply()

            except Exception as exc:

                print("[lock-screen] apply fallo:", exc)

        GLib.timeout_add(400, apply)
