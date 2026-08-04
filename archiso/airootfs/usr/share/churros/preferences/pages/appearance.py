from widgets.page import Page
from widgets.group import Group
from widgets.switch_row import SwitchRow
from widgets.navigation_row import NavigationRow

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import GLib

from services.theme import ThemeService
from services.settings import SettingsService


class AppearancePage(Page):

    def __init__(self, navigator):

        super().__init__(

            navigator,

            "Apariencia",

            "Personaliza el aspecto de ChurrOS"

        )

        #
        # Tema
        #

        theme = Group(

            "Tema"

        )

        theme.add(

            SwitchRow(

                title="Modo oscuro",

                subtitle="Usar el tema oscuro",

                icon="appearance.svg",

                active=ThemeService.is_dark(),

                callback=self.on_dark_changed

            )

        )

        theme.add(

            SwitchRow(

                title="Colores dinámicos",

                subtitle="Generar colores desde el fondo",

                icon="appearance.svg",

                active=SettingsService.get(

                    "theme.dynamic_colors",

                    True

                ),

                callback=self.on_dynamic_changed

            )

        )

        self.add(

            theme

        )

        #
        # Fondo
        #

        wallpaper = Group(

            "Fondo"

        )

        wallpaper.add(

            NavigationRow(

                navigator=navigator,

                title="Cambiar fondo",

                subtitle="Elegir un fondo de pantalla",

                icon="wallpaper.svg",

                page_name="wallpaper"

            )

        )

        self.add(

            wallpaper

        )

        #
        # Personalización
        #

        personalization = Group(

            "Personalización"

        )

        personalization.add(

            NavigationRow(

                navigator=navigator,

                title="Colores",

                subtitle="Cambiar el color de acento",

                icon="palette.svg",

                page_name="accent"

            )

        )

        personalization.add(

            NavigationRow(

                navigator=navigator,

                title="Iconos",

                subtitle="Seleccionar tema de iconos",

                icon="icons.svg",

                page_name="icons"

            )

        )

        personalization.add(

            NavigationRow(

                navigator=navigator,

                title="Cursor",

                subtitle="Seleccionar tema del cursor",

                icon="cursor.svg",

                page_name="cursor"

            )

        )

        personalization.add(

            NavigationRow(

                navigator=navigator,

                title="Fuentes",

                subtitle="Seleccionar la fuente del sistema",

                icon="font.svg",

                page_name="fonts"

            )

        )

        personalization.add(

            NavigationRow(

                navigator=navigator,

                title="Waybar",

                subtitle="Barra superior: posicion, colores y modulos",

                icon="waybar.svg",

                page_name="waybar"

            )

        )

        personalization.add(

            NavigationRow(

                navigator=navigator,

                title="Niri",

                subtitle="Compositor: disposicion, bordes, blur",

                icon="niri.svg",

                page_name="niri"

            )

        )

        self.add(

            personalization

        )

    #
    # Callbacks
    #

    def on_dark_changed(

        self,

        active

    ):

        ThemeService.set(

            active

        )

        try:

            window = self.get_root()

            if hasattr(window, "refresh_theme"):

                GLib.idle_add(window.refresh_theme)

        except Exception:

            pass

    def on_dynamic_changed(

        self,

        active

    ):

        SettingsService.set(

            "theme.dynamic_colors",

            active

        )