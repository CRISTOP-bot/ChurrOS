import os
import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, Gdk

from window import PreferencesWindow


class PreferencesApplication(Gtk.Application):

    def __init__(self):

        super().__init__(
            application_id="org.churros.preferences"
        )

    def do_activate(self):

        #
        # Cargar CSS
        #

        provider = Gtk.CssProvider()

        css_path = os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)
            ),
            "style.css"
        )

        try:

            provider.load_from_path(
                css_path
            )

            Gtk.StyleContext.add_provider_for_display(

                Gdk.Display.get_default(),

                provider,

                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION

            )

            print(f"CSS cargado: {css_path}")

        except Exception as error:

            print(f"No se pudo cargar el CSS: {error}")

        #
        # Crear ventana
        #

        window = PreferencesWindow(
            self
        )

        window.present()


app = PreferencesApplication()

app.run()