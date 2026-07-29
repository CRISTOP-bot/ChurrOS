import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PREF = os.path.abspath(os.path.join(ROOT, "..", "preferences"))

sys.path.insert(0, ROOT)
sys.path.insert(0, PREF)

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, Gdk

from services.store import StoreService

from ui.list_view import ListView
from ui.detail_view import DetailView


def _load_css():

    display = Gdk.Display.get_default()
    if display is None:
        return

    tokens_path = "/usr/share/churros/theme/tokens.css"

    if os.path.exists(tokens_path):

        tokens = Gtk.CssProvider()
        tokens.load_from_path(tokens_path)

        Gtk.StyleContext.add_provider_for_display(
            display,
            tokens,
            Gtk.STYLE_PROVIDER_PRIORITY_USER
        )

    css_path = os.path.join(ROOT, "assets", "style.css")

    if os.path.exists(css_path):

        provider = Gtk.CssProvider()
        provider.load_from_path(css_path)

        Gtk.StyleContext.add_provider_for_display(
            display,
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )


CATEGORIES = [
    ("discover",    "Descubrir",  "discover.svg"),
    ("apps",        "Apps",       "apps.svg"),
    ("games",       "Juegos",     "games.svg"),
    ("productivity","Productividad", "productivity.svg"),
    ("creativity",  "Creatividad", "creativity.svg"),
    ("tools",       "Herramientas", "tools.svg"),
    ("updates",     "Actualizaciones", "updates.svg"),
    ("installed",   "Instalados", "installed.svg"),
]


class StoreWindow(Gtk.ApplicationWindow):

    def __init__(self, app):

        super().__init__(application=app)

        self.set_title("ChurroStore")
        self.set_default_size(1280, 820)
        self.add_css_class("store-window")

        _load_css()

        self._build()

        controller = Gtk.EventControllerKey()
        controller.connect("key-pressed", self.on_key)
        self.add_controller(controller)

        self._go_to("discover")

    def _build(self):

        outer = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=0
        )
        self.set_child(outer)

        self._build_top_bar(outer)

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(220)
        self.stack.set_vexpand(True)

        outer.append(self.stack)

        self.list_view = ListView(self, query="", source="all", category="discover")
        self.stack.add_named(self.list_view, "list")

    def _build_top_bar(self, parent):

        bar = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=0
        )
        bar.add_css_class("store-top-bar")

        title_bar = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=12
        )
        title_bar.add_css_class("store-title-bar")

        brand = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=8
        )
        brand.add_css_class("store-brand")

        brand_icon = Gtk.Image.new_from_file(
            os.path.join(ROOT, "assets", "icons", "store.svg")
        )
        brand_icon.set_pixel_size(28)
        brand.append(brand_icon)

        brand_label = Gtk.Label(label="ChurroStore")
        brand_label.add_css_class("store-brand-label")

        brand.append(brand_label)

        title_bar.append(brand)

        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Buscar apps, juegos y mas...")
        self.search_entry.set_hexpand(True)
        self.search_entry.set_halign(Gtk.Align.CENTER)
        self.search_entry.set_size_request(360, -1)
        self.search_entry.connect(
            "search-changed",
            lambda *_: self._on_search_changed()
        )
        title_bar.append(self.search_entry)

        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        title_bar.append(spacer)

        bar.append(title_bar)

        nav_bar = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=4
        )
        nav_bar.add_css_class("store-nav-bar")

        nav_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=4
        )
        nav_box.set_halign(Gtk.Align.CENTER)
        nav_box.set_hexpand(True)

        self.nav_buttons = {}

        for cat_id, label, icon_name in CATEGORIES:

            btn = self._make_nav_button(cat_id, label, icon_name)
            nav_box.append(btn)
            self.nav_buttons[cat_id] = btn

        nav_bar.append(nav_box)
        bar.append(nav_bar)

        parent.append(bar)

    def _make_nav_button(self, cat_id, label, icon_name):

        btn = Gtk.ToggleButton()
        btn.set_has_frame(False)
        btn.add_css_class("store-nav-button")

        box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=6
        )
        box.set_margin_top(8)
        box.set_margin_bottom(8)
        box.set_margin_start(12)
        box.set_margin_end(12)

        icon_path = os.path.join(ROOT, "assets", "icons", icon_name)

        if os.path.exists(icon_path):
            icon = Gtk.Image.new_from_file(icon_path)
            icon.set_pixel_size(16)
            box.append(icon)

        lbl = Gtk.Label(label=label)
        lbl.add_css_class("store-nav-label")
        box.append(lbl)

        btn.set_child(box)
        btn._toggle_handler_id = btn.connect("toggled", self._on_nav_toggled, cat_id)

        return btn

    def _on_nav_toggled(self, btn, cat_id):

        if not btn.get_active():
            btn.set_active(True)
            return

        for other_id, other_btn in self.nav_buttons.items():
            if other_id != cat_id and other_btn.get_active():
                handler_id = other_btn._toggle_handler_id
                if handler_id is not None:
                    other_btn.handler_block(handler_id)
                other_btn.set_active(False)
                if handler_id is not None:
                    other_btn.handler_unblock(handler_id)

        self._go_to(cat_id)

    def _go_to(self, cat_id):

        self.stack.set_visible_child_name("list")

        for btn_id, btn in self.nav_buttons.items():
            btn.set_active(btn_id == cat_id)

        self.list_view.set_category(cat_id)

        self.search_entry.set_text("")

    def _on_search_changed(self):

        query = self.search_entry.get_text().strip()

        if not query:

            active = None

            for btn_id, btn in self.nav_buttons.items():
                if btn.get_active():
                    active = btn_id
                    break

            self.list_view.set_category(active or "discover", query="")
            return

        self.list_view.set_category("discover", query=query)

    def show_detail(self, package):

        def go_back():

            self.stack.set_visible_child_name("list")
            self.list_view.refresh()

            if self.stack.get_child_by_name("detail"):
                self.stack.remove(
                    self.stack.get_child_by_name("detail")
                )

        if self.stack.get_child_by_name("detail"):
            self.stack.remove(
                self.stack.get_child_by_name("detail")
            )

        detail = DetailView(self, package, go_back)
        self.stack.add_named(detail, "detail")
        self.stack.set_visible_child_name("detail")

    def on_key(self, controller, keyval, keycode, state):

        if keyval == Gdk.KEY_Escape:

            current = self.stack.get_visible_child_name()

            if current == "detail":
                self.stack.set_visible_child_name("list")
                self.list_view.refresh()
                return True

        return False


class StoreApp(Gtk.Application):

    def __init__(self):

        super().__init__(
            application_id="org.churros.store"
        )

    def do_activate(self):

        win = StoreWindow(self)
        win.present()


app = StoreApp()
app.run()
