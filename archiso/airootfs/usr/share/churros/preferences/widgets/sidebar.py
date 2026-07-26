import os
import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GObject

from widgets.search import Search
from widgets.sidebar_item import SidebarItem


class Sidebar(Gtk.Box):

    __gsignals__ = {

        "page-selected": (

            GObject.SignalFlags.RUN_FIRST,

            None,

            (str,)

        )

    }

    def __init__(self):

        super().__init__(
            orientation=Gtk.Orientation.VERTICAL
        )

        self.set_size_request(
            280,
            -1
        )

        self.add_css_class(
            "sidebar"
        )

        self.buttons = {}

        #
        # Logo
        #

        logo = Gtk.Image.new_from_file(

            os.path.join(
                os.path.dirname(__file__),
                "..",
                "assets",
                "logo.svg"
            )

        )

        logo.set_pixel_size(56)

        logo.set_margin_top(20)
        logo.set_margin_bottom(16)

        self.append(
            logo
        )

        #
        # Buscador
        #

        self.search = Search()

        self.search.set_margin_start(16)
        self.search.set_margin_end(16)
        self.search.set_margin_bottom(20)

        self.append(
            self.search
        )

        #
        # Lista
        #

        self.menu = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=6
        )

        self.menu.set_margin_start(10)
        self.menu.set_margin_end(10)

        self.append(
            self.menu
        )

        self.pages = [

            (
                "system",
                "system.svg",
                "Sistema"
            ),

            (
                "appearance",
                "appearance.svg",
                "Apariencia"
            ),

            (
                "display",
                "display.svg",
                "Pantalla"
            ),

            (
                "input",
                "input.svg",
                "Entrada"
            ),

            (
                "audio",
                "audio.svg",
                "Audio"
            ),

            (
                "connectivity",
                "connectivity.svg",
                "Conectividad"
            ),

            (
                "power",
                "power.svg",
                "Energía"
            ),

            (
                "users",
                "users.svg",
                "Usuarios"
            ),

            (
                "privacy",
                "privacy.svg",
                "Privacidad"
            ),

            (
                "applications",
                "applications.svg",
                "Aplicaciones"
            ),

            (
                "about",
                "about.svg",
                "Acerca de"
            )

        ]

        for page, icon, title in self.pages:

            item = SidebarItem(

                page,

                icon,

                title

            )

            item.connect(

                "clicked",

                self.on_clicked,

                page

            )

            self.menu.append(
                item
            )

            self.buttons[page] = item

        self.search.connect(
            "search",
            self.on_search
        )

        self.select(
            "system"
        )

    def on_search(
        self,
        search,
        query
    ):

        query = (query or "").lower()

        for page_id, item in self.buttons.items():

            title = ""

            for pid, _, title in self.pages:

                if pid == page_id:
                    break

            visible = query == "" or query in title.lower()

            item.set_visible(
                visible
            )

    def on_clicked(
        self,
        button,
        page
    ):

        self.select(
            page
        )

        self.emit(
            "page-selected",
            page
        )

    def select(
        self,
        page
    ):

        for item in self.buttons.values():

            item.deactivate()

        if page in self.buttons:

            self.buttons[page].activate()