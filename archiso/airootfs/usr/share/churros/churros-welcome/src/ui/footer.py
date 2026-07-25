import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from config.metadata import VERSION


def build_footer():

    footer = Gtk.Label(
        label=f"Linux • Niri • ChurrOS {VERSION}"
    )

    footer.add_css_class("footer")

    footer.set_halign(Gtk.Align.CENTER)

    return footer