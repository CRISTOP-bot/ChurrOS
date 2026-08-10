import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, Gio, GLib, Gdk

from services.theme import ThemeService
from services.settings import SettingsService

from widgets.sidebar import Sidebar
from widgets.navigator import Navigator

from pages.system import SystemPage
from pages.appearance import AppearancePage
from pages.accent import AccentPage
from pages.icons import IconsPage
from pages.cursor import CursorPage
from pages.fonts import FontsPage
from pages.wallpaper import WallpaperPage
from pages.waybar import WaybarPage
from pages.niri import NiriPage
from pages.foot import FootPage
from pages.fuzzel import FuzzelPage
from pages.mako import MakoPage
from pages.backup import BackupPage
from pages.logs import LogsPage
from pages.window_rules import WindowRulesPage
from pages.night_light import NightLightPage
from pages.lock_screen import LockScreenPage

from pages.audio import AudioPage
from pages.connectivity import ConnectivityPage
from pages.display import DisplayPage
from pages.input import InputPage
from pages.power import PowerPage
from pages.power_profile import PowerProfilePage
from pages.battery import BatteryPage
from pages.display_timeout import DisplayTimeoutPage
from pages.sleep import SleepPage
from pages.applications import ApplicationsPage
from pages.users import UsersPage
from pages.privacy import PrivacyPage
from pages.about import AboutPage
from pages.keyboard import KeyboardPage
from pages.datetime import DateTimePage


class PreferencesWindow(Gtk.ApplicationWindow):

    def __init__(self, app):

        super().__init__(
            application=app,
            title="Configuración"
        )

        self.set_default_size(
            1280,
            760
        )

        self.add_css_class(
            "preferences"
        )

        self._apply_theme_class()

        try:

            schema_source = Gio.SettingsSchemaSource.get_default()

            if schema_source is not None:

                schema = schema_source.lookup(
                    "org.gnome.desktop.interface",
                    False
                )

                if schema is not None:

                    gsettings = Gio.Settings.new_full(
                        schema,
                        None,
                        None
                    )

                    gsettings.connect(
                        "changed::color-scheme",
                        lambda *_: GLib.idle_add(self.refresh_theme)
                    )

        except Exception as exc:

            print(f"[preferences] gsettings setup: {exc}")

        #
        # Layout principal
        #

        root = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL
        )

        self.set_child(
            root
        )

        #
        # Sidebar
        #

        self.sidebar = Sidebar()

        self.sidebar_revealer = Gtk.Revealer()
        self.sidebar_revealer.set_transition_type(
            Gtk.RevealerTransitionType.SLIDE_RIGHT
        )
        self.sidebar_revealer.set_reveal_child(True)
        self.sidebar_revealer.set_child(self.sidebar)

        root.append(
            self.sidebar_revealer
        )

        #
        # Navegador con boton de toggle para modo estrecho
        #

        nav_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL
        )

        self._toggle_button = Gtk.Button.new_from_icon_name(
            "open-menu-symbolic"
        )
        self._toggle_button.add_css_class("flat")
        self._toggle_button.set_halign(Gtk.Align.END)
        self._toggle_button.set_margin_start(12)
        self._toggle_button.set_margin_end(12)
        self._toggle_button.set_margin_top(12)
        self._toggle_button.set_visible(False)
        self._toggle_button.connect(
            "clicked",
            lambda *_: self._toggle_sidebar()
        )

        nav_box.append(self._toggle_button)

        #
        # Navigator
        #

        self.navigator = Navigator()

        self.navigator.set_hexpand(True)
        self.navigator.set_vexpand(True)

        nav_box.append(
            self.navigator
        )

        #
        # Sidebar: cuando el navigator cambia (alta o back)
        #

        def on_navigated(navigator, name):
            if name in self.sidebar.buttons:
                self.sidebar.select(name)
            elif name in self.sidebar._catalog:
                for pid, parent_id, _, _, _ in self.sidebar._catalog:
                    if pid == name and parent_id in self.sidebar.buttons:
                        self.sidebar.select(parent_id)
                        break

        self.navigator.connect("navigated", on_navigated)

        #
        # Atajos de teclado globales
        #

        key_ctrl = Gtk.EventControllerKey()
        key_ctrl.set_propagation_phase(Gtk.PropagationPhase.BUBBLE)

        def on_key(controller, keyval, keycode, state):

            ctrl = (state & Gtk.GdkModifierType.CONTROL_MASK) != 0
            shift = (state & Gtk.GdkModifierType.SHIFT_MASK) != 0

            if ctrl and (keyval == ord('f') or keyval == ord('F')):

                try:
                    self.sidebar.search.grab_focus()
                except Exception:
                    pass

                return True

            if ctrl and (keyval == ord('b') or keyval == ord('B')):

                if self._is_narrow:
                    self._toggle_sidebar()

                return True

            if ctrl and shift and (
                keyval == ord('N') or keyval == ord('n')
            ):

                self._toggle_sidebar()

                return True

            return False

        key_ctrl.connect("key-pressed", on_key)

        self.add_controller(key_ctrl)

        root.append(
            nav_box
        )

        #
        # Responsive: en ventanas estrechas oculta el sidebar
        #

        self._narrow_threshold = 760
        self._is_narrow = False

        self.connect(
            "map",
            lambda *_: GLib.timeout_add(
                250,
                self._check_narrow
            )
        )

        self._is_maximized = False

        self.connect(
            "map",
            lambda *_: GLib.timeout_add(
                500,
                self._check_maximized
            )
        )

        #
        # Registrar páginas principales
        #

        self.navigator.add_page(
            "system",
            SystemPage(self.navigator)
        )

        self.navigator.add_page(
            "appearance",
            AppearancePage(self.navigator)
        )

        self.navigator.add_page(
            "datetime",
            DateTimePage(self.navigator)
        )

        self.navigator.add_page(
            "audio",
            AudioPage(self.navigator)
        )

        self.navigator.add_page(
            "connectivity",
            ConnectivityPage(self.navigator)
        )

        self.navigator.add_page(
            "display",
            DisplayPage(self.navigator)
        )

        self.navigator.add_page(
            "input",
            InputPage(self.navigator)
        )

        self.navigator.add_page(
            "power",
            PowerPage(self.navigator)
        )

        self.navigator.add_page(
            "applications",
            ApplicationsPage(self.navigator)
        )

        self.navigator.add_page(
            "users",
            UsersPage(self.navigator)
        )

        self.navigator.add_page(
            "privacy",
            PrivacyPage(self.navigator)
        )

        self.navigator.add_page(
            "about",
            AboutPage(self.navigator)
        )

        self.navigator.add_page(
            "keyboard",
            KeyboardPage(self.navigator)
        )

        #
        # Subpáginas de Apariencia
        #

        self.navigator.add_page(
            "accent",
            AccentPage(self.navigator)
        )
        self.sidebar.register_subpage(
            "accent", "appearance",
            "Colores", "Color de acento del sistema",
            "palette.svg"
        )

        self.navigator.add_page(
            "icons",
            IconsPage(self.navigator)
        )
        self.sidebar.register_subpage(
            "icons", "appearance",
            "Iconos", "Tema de iconos",
            "icons.svg"
        )

        self.navigator.add_page(
            "cursor",
            CursorPage(self.navigator)
        )
        self.sidebar.register_subpage(
            "cursor", "appearance",
            "Cursor", "Tema y tamano del cursor",
            "cursor.svg"
        )

        self.navigator.add_page(
            "fonts",
            FontsPage(self.navigator)
        )
        self.sidebar.register_subpage(
            "fonts", "appearance",
            "Fuentes", "Familia y tamano de fuente",
            "font.svg"
        )

        self.navigator.add_page(
            "waybar",
            WaybarPage(self.navigator)
        )
        self.sidebar.register_subpage(
            "waybar", "appearance",
            "Waybar", "Barra: posicion, colores, modulos",
            "waybar.svg"
        )

        self.navigator.add_page(
            "niri",
            NiriPage(self.navigator)
        )
        self.sidebar.register_subpage(
            "niri", "appearance",
            "Niri", "Compositor: disposicion, bordes, blur",
            "niri.svg"
        )

        self.navigator.add_page(
            "foot",
            FootPage(self.navigator)
        )
        self.sidebar.register_subpage(
            "foot", "appearance",
            "Foot", "Terminal: fuente, cursor, padding, bell",
            "terminal.svg"
        )

        self.navigator.add_page(
            "fuzzel",
            FuzzelPage(self.navigator)
        )
        self.sidebar.register_subpage(
            "fuzzel", "appearance",
            "Fuzzel", "Launcher: fuente, layout, iconos",
            "applications.svg"
        )

        self.navigator.add_page(
            "mako",
            MakoPage(self.navigator)
        )
        self.sidebar.register_subpage(
            "mako", "appearance",
            "Mako", "Notificaciones: fuente, colores, posicion, DND",
            "mako.svg"
        )

        self.navigator.add_page(
            "wallpaper",
            WallpaperPage(self.navigator)
        )
        self.sidebar.register_subpage(
            "wallpaper", "appearance",
            "Fondo", "Cambiar el fondo de pantalla",
            "wallpaper.svg"
        )

        self.navigator.add_page(
            "night-light",
            NightLightPage(self.navigator)
        )
        self.sidebar.register_subpage(
            "night-light", "appearance",
            "Luz nocturna",
            "Temperatura de color y filtro de luz azul",
            "night_light.svg"
        )

        self.navigator.add_page(
            "lock-screen",
            LockScreenPage(self.navigator)
        )
        self.sidebar.register_subpage(
            "lock-screen", "appearance",
            "Pantalla de bloqueo",
            "swaylock + swayidle: estilo y bloqueo automatico",
            "lock_screen.svg"
        )

        #
        # Subpáginas de Energía
        #

        self.navigator.add_page(
            "power-profile",
            PowerProfilePage(self.navigator)
        )
        self.sidebar.register_subpage(
            "power-profile", "power",
            "Perfiles de energia", "Performance, balanced o power-saver"
        )

        self.navigator.add_page(
            "battery",
            BatteryPage(self.navigator)
        )
        self.sidebar.register_subpage(
            "battery", "power",
            "Bateria", "Estado, nivel y opciones de bateria"
        )

        self.navigator.add_page(
            "display-timeout",
            DisplayTimeoutPage(self.navigator)
        )
        self.sidebar.register_subpage(
            "display-timeout", "display",
            "Apagado de pantalla", "Tiempo antes de apagar la pantalla"
        )

        self.navigator.add_page(
            "sleep",
            SleepPage(self.navigator)
        )
        self.sidebar.register_subpage(
            "sleep", "power",
            "Suspension", "Tiempo antes de suspender el sistema"
        )

        #
        # Otros
        #

        self.navigator.add_page(
            "backup",
            BackupPage(self.navigator)
        )
        self.sidebar.register_subpage(
            "backup", "system",
            "Copia de seguridad",
            "Exportar, importar o restablecer la configuracion",
            "backup.svg"
        )

        self.navigator.add_page(
            "logs",
            LogsPage(self.navigator)
        )
        self.sidebar.register_subpage(
            "logs", "system",
            "Logs de Niri", "Registros del compositor y validacion",
            "logs.svg"
        )

        self.navigator.add_page(
            "window-rules",
            WindowRulesPage(self.navigator)
        )
        self.sidebar.register_subpage(
            "window-rules", "appearance",
            "Reglas de ventana", "Opacidad, flotantes, esquinas, blur",
            "window_rules.svg"
        )

        #
        # Página inicial
        #

        last_page = SettingsService.get(
            "preferences.last_page",
            "system"
        )

        self.navigator.show_page(
            last_page
        )

        self.sidebar.select(
            last_page
        )

        #
        # Sidebar
        #

        self.sidebar.connect(
            "page-selected",
            self.on_page_selected
        )

    def on_page_selected(
        self,
        sidebar,
        page
    ):

        SettingsService.set(
            "preferences.last_page",
            page
        )

        self.navigator.show_page(
            page
        )

        if self._is_narrow:

            self.sidebar_revealer.set_reveal_child(False)

    def _apply_theme_class(self):
        """Cambia la clase CSS .light segun el modo del ThemeService."""

        try:

            want_light = not ThemeService.is_dark()

            has_light = "light" in self.get_css_classes()

            if want_light and not has_light:

                self.add_css_class("light")

            elif not want_light and has_light:

                self.remove_css_class("light")

        except Exception as exc:

            import sys
            print(f"[preferences] apply_theme_class: {exc}", file=sys.stderr)

    def refresh_theme(self):

        """Aplica la clase .light/.dark segun el modo.

        Las variables CSS ya estan definidas en churros.css y style.css
        con selectores window (dark) y window.light (light).
        Cambiar la clase en la ventana re-evalua todas las variables
        automaticamente, SIN recargar los archivos CSS (que crashea GTK4).
        """

        self._apply_theme_class()

        try:

            context = self.get_style_context()

            context.invalidate()

            context.add_class("needs-style-refresh")
            context.remove_class("needs-style-refresh")

        except Exception:

            pass

        try:

            self.queue_draw()
            self.queue_resize()

        except Exception:

            pass

    def _check_narrow(self):

        try:

            width = self.get_width()

        except Exception:

            return True

        new_narrow = width < self._narrow_threshold

        if new_narrow == self._is_narrow:

            return True

        self._is_narrow = new_narrow

        if new_narrow:

            self.sidebar_revealer.set_reveal_child(False)

            self._toggle_button.set_visible(True)

            self.sidebar_revealer.set_transition_type(
                Gtk.RevealerTransitionType.SLIDE_RIGHT
            )

        else:

            self.sidebar_revealer.set_reveal_child(True)

            self._toggle_button.set_visible(False)

        return True

    def _toggle_sidebar(self):

        revealed = self.sidebar_revealer.get_reveal_child()

        self.sidebar_revealer.set_reveal_child(not revealed)

    def _check_maximized(self):

        try:

            maximized = self.is_maximized()
            fullscreen = self.is_fullscreen()

            active = maximized or fullscreen

            if active == self._is_maximized:

                return True

            self._is_maximized = active

            if active:

                self.add_css_class("maximized")

            else:

                self.remove_css_class("maximized")

        except Exception:

            pass

        return True

