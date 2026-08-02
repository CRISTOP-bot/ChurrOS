import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, Gio, GLib, Gdk

from services.theme import ThemeService

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

        root.append(
            self.sidebar
        )

        #
        # Navigator
        #

        self.navigator = Navigator()

        root.append(
            self.navigator
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

        self.navigator.add_page(
            "icons",
            IconsPage(self.navigator)
        )

        self.navigator.add_page(
            "cursor",
            CursorPage(self.navigator)
        )

        self.navigator.add_page(
            "fonts",
            FontsPage(self.navigator)
        )

        self.navigator.add_page(
            "waybar",
            WaybarPage(self.navigator)
        )

        self.navigator.add_page(
            "wallpaper",
            WallpaperPage(self.navigator)
        )

        #
        # Subpáginas de Energía
        #

        self.navigator.add_page(
            "power-profile",
            PowerProfilePage(self.navigator)
        )

        self.navigator.add_page(
            "battery",
            BatteryPage(self.navigator)
        )

        self.navigator.add_page(
            "display-timeout",
            DisplayTimeoutPage(self.navigator)
        )

        self.navigator.add_page(
            "sleep",
            SleepPage(self.navigator)
        )

        #
        # Página inicial
        #

        self.navigator.show_page(
            "system"
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

        self.navigator.show_page(
            page
        )

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

        """Recarga CSS desde disco y re-aplica la clase .light.

        GTK4 con variables CSS en runtime requiere recargar el provider
        completo para que las variables se re-evaluen en todo el arbol.
        """

        self._apply_theme_class()

        self._reload_css_providers()

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

    def _reload_css_providers(self):

        """Recarga style.css en providers registrados y refresca accent.css."""

        import os

        try:

            gi = __import__("gi")

            gi.require_version("Gtk", "4.0")

            from gi.repository import Gtk, Gdk

        except Exception:

            return

        try:

            display = Gdk.Display.get_default()

            if display is None:
                return

            style_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "style.css"
            )

            accent_path = os.path.expanduser(
                "~/.config/churros/accent.css"
            )

            providers = Gtk.StyleContext.list_providers(display) or []

            for entry in providers:

                try:

                    _, provider = entry

                except Exception:

                    provider = entry

                try:

                    provider.load_from_path(style_path)

                except Exception:

                    pass

            if os.path.exists(accent_path):

                try:

                    accent_provider = Gtk.CssProvider()
                    accent_provider.load_from_path(accent_path)

                    Gtk.StyleContext.add_provider_for_display(
                        display,
                        accent_provider,
                        Gtk.STYLE_PROVIDER_PRIORITY_USER + 1
                    )

                except Exception:

                    pass

        except Exception:

            pass