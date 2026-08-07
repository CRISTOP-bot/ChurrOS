import os

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GLib

from widgets.page import Page
from widgets.group import Group
from widgets.row import Row
from widgets.switch_row import SwitchRow
from widgets.navigation_row import NavigationRow

from services.theme import ThemeService
from services.settings import SettingsService
from services.pywal_service import PywalService
from services.wallpaper import WallpaperService
from services.dotfiles.niri_config import NiriConfig


class AppearancePage(Page):

    def __init__(self, navigator):

        super().__init__(

            navigator,

            "Apariencia",

            "Personaliza el aspecto de ChurrOS"

        )

        self.navigator = navigator

        self._feedback_label = None

        self._pending_pywal = False

        self._build()

    def _build(self):

        self._build_theme()
        self._build_wallpaper()
        self._build_desktop()
        self._build_components()
        self._build_compositor()
        self._build_screen()
        self._build_personalization()
        self._build_window_rules()
        self._build_status()

    #
    # Tema
    #

    def _build_theme(self):

        group = Group("Tema")

        group.add(
            SwitchRow(
                title="Modo oscuro",
                subtitle="Usar el tema oscuro",
                icon="appearance.svg",
                active=ThemeService.is_dark(),
                callback=self.on_dark_changed
            )
        )

        group.add(
            SwitchRow(
                title="Colores dinámicos",
                subtitle="Generar paleta desde el wallpaper (pywal)",
                icon="appearance.svg",
                active=SettingsService.get(
                    "theme.dynamic_colors",
                    True
                ),
                callback=self.on_dynamic_changed
            )
        )

        self.add(group)

    #
    # Fondo
    #

    def _build_wallpaper(self):

        group = Group("Fondo de pantalla")

        try:

            current = WallpaperService.current()

            if current and os.path.isfile(current):

                subtitle = "Actual: " + current
                value = None

            else:

                subtitle = "Sin wallpaper configurado"
                value = "Sin fondo"

        except Exception as exc:

            subtitle = "Error leyendo wallpaper: " + str(exc)
            value = "Error"

        preview_row = Row(
            title="Wallpaper actual",
            subtitle=subtitle,
            icon="wallpaper.svg",
            value=value
        )

        group.add(preview_row)

        group.add(
            NavigationRow(
                navigator=self.navigator,
                title="Cambiar fondo",
                subtitle="Elegir entre los fondos disponibles",
                icon="wallpaper.svg",
                page_name="wallpaper"
            )
        )

        self.add(group)

    #
    # Escritorio (switches globales)
    #

    def _build_desktop(self):

        group = Group("Escritorio")

        try:
            animations_on = NiriConfig.get_animations()
        except Exception:
            animations_on = True

        group.add(
            SwitchRow(
                title="Animaciones de niri",
                subtitle="Desactiva todas las transiciones (mas agil en hardware modesto)",
                icon="appearance.svg",
                active=animations_on,
                callback=self.on_animations_changed
            )
        )

        try:
            prefer_no_csd = NiriConfig.get_prefer_no_csd()
        except Exception:
            prefer_no_csd = True

        group.add(
            SwitchRow(
                title="Sin decoraciones de cliente (CSD)",
                subtitle="Las apps omiten sus propios marcos de ventana",
                icon="appearance.svg",
                active=prefer_no_csd,
                callback=self.on_csd_changed
            )
        )

        self.add(group)

    #
    # Componentes
    #

    def _build_components(self):

        group = Group("Componentes de UI")

        group.add(
            NavigationRow(
                navigator=self.navigator,
                title="Waybar",
                subtitle="Barra superior: posicion, colores y modulos",
                icon="waybar.svg",
                page_name="waybar"
            )
        )

        group.add(
            NavigationRow(
                navigator=self.navigator,
                title="Foot",
                subtitle="Terminal: fuente, cursor, padding, bell",
                icon="terminal.svg",
                page_name="foot"
            )
        )

        group.add(
            NavigationRow(
                navigator=self.navigator,
                title="Fuzzel",
                subtitle="Launcher: fuente, layout, iconos",
                icon="applications.svg",
                page_name="fuzzel"
            )
        )

        group.add(
            NavigationRow(
                navigator=self.navigator,
                title="Mako",
                subtitle="Notificaciones: fuente, colores, posicion, DND",
                icon="mako.svg",
                page_name="mako"
            )
        )

        self.add(group)

    #
    # Compositor
    #

    def _build_compositor(self):

        group = Group("Compositor")

        group.add(
            NavigationRow(
                navigator=self.navigator,
                title="Niri",
                subtitle="Layout, bordes, focus-ring, blur, prefer-no-csd",
                icon="niri.svg",
                page_name="niri"
            )
        )

        self.add(group)

    #
    # Pantalla
    #

    def _build_screen(self):

        group = Group("Pantalla")

        group.add(
            NavigationRow(
                navigator=self.navigator,
                title="Luz nocturna",
                subtitle="Temperatura de color y filtro de luz azul (wlsunset)",
                icon="night_light.svg",
                page_name="night-light"
            )
        )

        group.add(
            NavigationRow(
                navigator=self.navigator,
                title="Pantalla de bloqueo",
                subtitle="swaylock + swayidle: estilo y bloqueo automatico",
                icon="lock_screen.svg",
                page_name="lock-screen"
            )
        )

        self.add(group)

    #
    # Personalización
    #

    def _build_personalization(self):

        group = Group("Personalización básica")

        group.add(
            NavigationRow(
                navigator=self.navigator,
                title="Colores",
                subtitle="Color de acento (manual o desde paleta)",
                icon="palette.svg",
                page_name="accent"
            )
        )

        group.add(
            NavigationRow(
                navigator=self.navigator,
                title="Iconos",
                subtitle="Tema de iconos del sistema",
                icon="icons.svg",
                page_name="icons"
            )
        )

        group.add(
            NavigationRow(
                navigator=self.navigator,
                title="Cursor",
                subtitle="Tema y tamano del cursor",
                icon="cursor.svg",
                page_name="cursor"
            )
        )

        group.add(
            NavigationRow(
                navigator=self.navigator,
                title="Fuentes",
                subtitle="Familia y tamano de fuente del sistema",
                icon="font.svg",
                page_name="fonts"
            )
        )

        self.add(group)

    #
    # Reglas de ventana
    #

    def _build_window_rules(self):

        group = Group("Reglas de ventana")

        group.add(
            NavigationRow(
                navigator=self.navigator,
                title="Reglas de ventana",
                subtitle="Opacidad, floatantes, esquinas, blur por app",
                icon="window_rules.svg",
                page_name="window-rules"
            )
        )

        self.add(group)

    #
    # Estado de regeneracion
    #

    def _build_status(self):

        group = Group("Estado")

        self._feedback_label = Row(
            title="Cambios en vivo",
            subtitle="Los cambios se aplican al instante",
            icon="appearance.svg"
        )

        group.add(self._feedback_label)

        self.add(group)

    #
    # Callbacks
    #

    def _set_feedback(self, text):

        if self._feedback_label is not None:
            try:
                self._feedback_label.set_subtitle(text)
            except Exception:
                pass

    def _refresh_root_theme(self):

        try:
            window = self.get_root()
            if hasattr(window, "refresh_theme"):
                GLib.idle_add(window.refresh_theme)
        except Exception:
            pass

    def on_dark_changed(self, active):

        ThemeService.set(active)

        if active:
            self._set_feedback("Modo oscuro activado")
        else:
            self._set_feedback("Modo claro activado")

        self._refresh_root_theme()

    def on_dynamic_changed(self, active):

        if active:

            self._pending_pywal = True
            self._set_feedback("Generando paleta con pywal...")

            def worker():

                ok = PywalService.enable()
                self._pending_pywal = False

                GLib.idle_add(
                    self._on_pywal_done,
                    ok
                )

            import threading

            threading.Thread(target=worker, daemon=True).start()

        else:

            PywalService.disable()
            self._set_feedback("Colores dinámicos desactivados")

        self._refresh_root_theme()

    def _on_pywal_done(self, ok):

        if ok:
            self._set_feedback("Paleta aplicada: accent actualizado")
        else:
            self._set_feedback(
                "pywal no disponible o wallpaper invalido"
            )

        self._refresh_root_theme()

    def on_animations_changed(self, value):

        try:
            NiriConfig.set_animations(value)
            NiriConfig.reload()
            self._set_feedback(
                "Animaciones desactivadas" if not value
                else "Animaciones activadas"
            )
        except Exception as exc:
            self._set_feedback("Error: " + str(exc))

    def on_csd_changed(self, value):

        try:
            NiriConfig.set_prefer_no_csd(value)
            NiriConfig.reload()
            self._set_feedback(
                "CSD deshabilitado" if value
                else "CSD permitido"
            )
        except Exception as exc:
            self._set_feedback("Error: " + str(exc))
