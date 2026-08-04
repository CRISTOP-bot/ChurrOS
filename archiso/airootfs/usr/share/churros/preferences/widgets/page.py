import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

import sys
import os

_CHURROS = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

if _CHURROS not in sys.path:

    sys.path.insert(0, _CHURROS)

try:

    from i18n import _ as _i18n

except Exception:

    def _i18n(s):
        return s


class Page(Gtk.ScrolledWindow):

    def __init__(
        self,
        navigator,
        title,
        subtitle=None,
        parent_page=None
    ):

        super().__init__()

        self.navigator = navigator
        self.parent_page = parent_page

        self.set_hexpand(True)
        self.set_vexpand(True)

        self.set_policy(
            Gtk.PolicyType.NEVER,
            Gtk.PolicyType.AUTOMATIC
        )

        #
        # Contenedor principal
        #

        root = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=18
        )

        root.set_margin_top(24)
        root.set_margin_bottom(24)
        root.set_margin_start(24)
        root.set_margin_end(24)

        self.set_child(root)

        #
        # Boton de retroceso (subpaginas)
        #

        if parent_page is not None:

            back_btn = Gtk.Button.new_from_icon_name(
                "go-previous-symbolic"
            )

            back_btn.set_label(" " + _i18n("Atras"))
            back_btn.set_halign(Gtk.Align.START)
            back_btn.add_css_class("back-button")
            back_btn.set_has_frame(False)
            back_btn.connect("clicked", self.on_back)

            root.append(back_btn)

        #
        # Cabecera
        #

        header = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=4
        )

        title_label = Gtk.Label(
            label=_i18n(title),
            xalign=0
        )

        title_label.add_css_class(
            "page-title"
        )

        header.append(title_label)

        if subtitle:

            subtitle_label = Gtk.Label(
                label=_i18n(subtitle),
                xalign=0
            )

            subtitle_label.add_css_class(
                "page-subtitle"
            )

            header.append(
                subtitle_label
            )

        root.append(
            header
        )

        #
        # Contenido
        #

        self.content = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=18
        )

        root.append(
            self.content
        )

    def on_back(self, *_):

        if self.parent_page is not None:

            self.navigator.show_page(self.parent_page)

    def add(
        self,
        widget
    ):

        self.content.append(
            widget
        )
