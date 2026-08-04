import os
import sys
import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, Gdk

# Resolve dirs
APP_DIR = os.path.dirname(os.path.abspath(__file__))
CHURROS_ROOT = os.path.abspath(os.path.join(APP_DIR, ".."))
PREFS_DIR = os.path.join(CHURROS_ROOT, "preferences")

# Order matters: APP_DIR must be FIRST so 'window' resolves to ours,
# not to preferences/window.py. Then we add prefs for the i18n module,
# and CHURROS_ROOT for the 'services' namespace package.
for p in (APP_DIR, PREFS_DIR, CHURROS_ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)

# But inserting at 0 reverses order; rebuild the slice so APP_DIR wins.
sys.path.remove(APP_DIR)
sys.path.insert(0, APP_DIR)

from window import ControlCenterWindow


class ControlCenterApp(Gtk.Application):

    def __init__(self):

        super().__init__(
            application_id="org.churros.controlcenter"
        )

    def do_activate(self):

        display = Gdk.Display.get_default()

        shared_path = "/usr/share/churros/styles/churros.css"

        if os.path.exists(shared_path):

            shared = Gtk.CssProvider()

            shared.load_from_path(shared_path)

            Gtk.StyleContext.add_provider_for_display(
                display,
                shared,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )

        css = Gtk.CssProvider()

        css.load_from_path(
            os.path.join(
                APP_DIR,
                "style.css"
            )
        )

        Gtk.StyleContext.add_provider_for_display(
            display,
            css,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION + 1
        )

        window = ControlCenterWindow(self)

        window.present()


app = ControlCenterApp()

app.run()
