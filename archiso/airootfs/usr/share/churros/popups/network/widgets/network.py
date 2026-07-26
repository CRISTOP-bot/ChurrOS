from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
PREFERENCES = Path(__file__).resolve().parents[5] / "preferences"

sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(PREFERENCES))

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from i18n import _

from widgets.wifi import WifiWidget
from widgets.ethernet import EthernetWidget


class NetworkWidget(Gtk.Box):

    def __init__(self):

        super().__init__(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=18
        )

        self.add_css_class("network-widget")

        self.append(
            WifiWidget()
        )

        separator = Gtk.Separator(
            orientation=Gtk.Orientation.HORIZONTAL
        )
        separator.add_css_class("network-separator")

        self.append(separator)

        self.append(
            EthernetWidget()
        )
