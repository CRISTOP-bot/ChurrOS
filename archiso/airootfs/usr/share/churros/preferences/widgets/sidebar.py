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

        self._catalog = []

        self._popover = None
        self._popover_results = None
        self._popover_matches = []

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

        self._build_popover()

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
                "datetime",
                "system.svg",
                "Fecha y hora"
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
                "keyboard",
                "input.svg",
                "Teclado"
            ),

            (
                "about",
                "about.svg",
                "Acerca de"
            )

        ]

        for page, icon, title in self.pages:

            self._catalog.append(
                (page, None, title, "", icon)
            )

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

    def _build_popover(self):

        self._popover = Gtk.Popover()
        self._popover.set_parent(self.search)
        self._popover.set_position(Gtk.PositionType.BOTTOM)
        self._popover.set_autohide(True)

        self._popover_results = Gtk.ListBox()
        self._popover_results.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self._popover_results.add_css_class("search-results")
        self._popover_results.set_size_request(260, -1)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_child(self._popover_results)
        scrolled.set_max_content_height(360)
        scrolled.set_propagate_natural_height(True)

        self._popover.set_child(scrolled)

    def register_subpage(
        self,
        page_id,
        parent_id,
        title,
        subtitle,
        icon=None
    ):

        self._catalog.append(
            (page_id, parent_id, title, subtitle, icon)
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

        self._update_popover(query)

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

    def _update_popover(
        self,
        query
    ):

        if self._popover is None:

            return

        while self._popover_results.get_first_child() is not None:

            self._popover_results.remove(
                self._popover_results.get_first_child()
            )

        self._popover_matches = []

        if not query:

            self._popover.popdown()

            return

        matches = []

        for entry in self._catalog:

            page_id, parent_id, title, subtitle, icon = entry

            haystack = (
                title + " " + (subtitle or "")
            ).lower()

            if query in haystack:

                matches.append(entry)

        if not matches:

            self._popover.popdown()

            return

        for idx, entry in enumerate(matches):

            row = self._build_result_row(entry)

            row.connect(
                "activated",
                self._on_popover_row,
                idx
            )

            self._popover_results.append(row)

        self._popover_matches = matches
        self._popover.popup()

    def _build_result_row(
        self,
        entry
    ):

        page_id, parent_id, title, subtitle, icon = entry

        row = Gtk.ListBoxRow()
        row.add_css_class("search-result")

        box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=2
        )

        box.set_margin_top(8)
        box.set_margin_bottom(8)
        box.set_margin_start(12)
        box.set_margin_end(12)

        title_label = Gtk.Label(
            label=title
        )
        title_label.set_xalign(0)
        title_label.set_hexpand(True)
        title_label.add_css_class("row-title")

        box.append(title_label)

        if subtitle:

            sub_label = Gtk.Label(
                label=subtitle
            )
            sub_label.set_xalign(0)
            sub_label.set_hexpand(True)
            sub_label.add_css_class("row-subtitle")

            box.append(sub_label)

        row.set_child(box)

        return row

    def _on_popover_row(
        self,
        row,
        idx
    ):

        if idx >= len(self._popover_matches):

            return

        page_id, parent_id, _, _, _ = self._popover_matches[idx]

        self._popover.popdown()

        self.search.set_text("")

        self.emit(
            "page-selected",
            page_id
        )