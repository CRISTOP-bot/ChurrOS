import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GObject


class Search(Gtk.SearchEntry):

    __gsignals__ = {

        "search": (

            GObject.SignalFlags.RUN_FIRST,

            None,

            (str,)

        )

    }

    def __init__(self):

        super().__init__()

        self.set_placeholder_text(
            "Buscar configuración..."
        )

        self.add_css_class(
            "preferences-search"
        )

        self.connect(
            "search-changed",
            self.on_search
        )

    def on_search(self, *_):

        self.emit(

            "search",

            self.get_text()

        )