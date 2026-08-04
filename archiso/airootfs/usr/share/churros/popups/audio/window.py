from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, Gdk

from common.popup import PopupWindow

from widgets.volume import VolumeWidget
from widgets.mute import MuteWidget
from widgets.device import DeviceWidget


def _section_label(text):

    label = Gtk.Label(label=text)
    label.add_css_class("audio-section-label")
    label.set_xalign(0)
    return label


class AudioWindow(PopupWindow):

    def __init__(self, app):

        super().__init__(
            app,
            title="Audio",
            icon="󰕾"
        )

        self.load_audio_css()

        self.add(_section_label("Output"))
        self.add(VolumeWidget(source=False))
        self.add(DeviceWidget(source=False))
        self.add(MuteWidget(source=False))

        self.add(Gtk.Separator())

        self.add(_section_label("Input"))
        self.add(VolumeWidget(source=True))
        self.add(DeviceWidget(source=True))
        self.add(MuteWidget(source=True))

    def load_audio_css(self):

        display = Gdk.Display.get_default()

        shared = "/usr/share/churros/styles/churros.css"

        if Path(shared).exists() or True:

            shared_provider = Gtk.CssProvider()

            shared_provider.load_from_path(shared)

            Gtk.StyleContext.add_provider_for_display(

                display,

                shared_provider,

                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION

            )

        provider = Gtk.CssProvider()

        provider.load_from_path(
            str(Path(__file__).parent / "style.css")
        )

        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
