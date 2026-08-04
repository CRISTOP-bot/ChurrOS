import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, Gdk

from services.accent import AccentService
from window import PreferencesWindow


class PreferencesApplication(Gtk.Application):

    def __init__(self):

        super().__init__(
            application_id="org.churros.preferences"
        )

    def _load_css(
        self,
        path,
        priority=Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    ):

        provider = Gtk.CssProvider()

        try:

            provider.load_from_path(
                path
            )

            Gtk.StyleContext.add_provider_for_display(

                Gdk.Display.get_default(),

                provider,

                priority

            )

            print(f"CSS cargado: {path}")

        except Exception as error:

            print(f"No se pudo cargar el CSS: {error}")

    def do_activate(self):

        print("[preferences] do_activate")

        try:
            AccentService.ensure()
        except Exception as e:
            print(f"[preferences] AccentService fallo: {e}")

        base = os.path.dirname(
            os.path.abspath(__file__)
        )

        shared = "/usr/share/churros/styles/churros.css"

        if os.path.exists(shared):

            self._load_css(shared, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self._load_css(
            os.path.join(base, "style.css"),
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION + 1
        )

        accent_css = AccentService.ACCENT_CSS

        if os.path.exists(accent_css):
            self._load_css(accent_css, Gtk.STYLE_PROVIDER_PRIORITY_USER)

        try:
            window = PreferencesWindow(self)
            window.present()
            print("[preferences] ventana abierta")
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"[preferences] ventana fallo: {e}")


app = PreferencesApplication()

try:
    app.run()
except KeyboardInterrupt:
    sys.exit(0)
except Exception as e:
    import traceback
    traceback.print_exc()
