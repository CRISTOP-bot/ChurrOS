import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from widgets.sidebar import Sidebar
from widgets.navigator import Navigator

from pages.system import SystemPage
from pages.appearance import AppearancePage
from pages.accent import AccentPage
from pages.icons import IconsPage
from pages.cursor import CursorPage
from pages.fonts import FontsPage
from pages.wallpaper import WallpaperPage

from pages.audio import AudioPage
from pages.connectivity import ConnectivityPage
from pages.display import DisplayPage
from pages.power import PowerPage
from pages.applications import ApplicationsPage
from pages.users import UsersPage
from pages.privacy import PrivacyPage
from pages.about import AboutPage


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
            "wallpaper",
            WallpaperPage(self.navigator)
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