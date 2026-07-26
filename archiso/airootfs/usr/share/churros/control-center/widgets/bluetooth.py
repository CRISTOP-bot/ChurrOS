from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
PREFERENCES = Path(__file__).resolve().parents[5] / "preferences"

sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(PREFERENCES))

from widgets.card import Card
from popup_launcher import open_bluetooth

from i18n import _
from services.bluetooth import BluetoothService


class BluetoothCard(Card):

    def __init__(self):

        super().__init__(
            "bluetooth.svg",
            _("Bluetooth"),
            _("Unavailable")
        )

        self.connect(
            "clicked",
            self.on_clicked
        )

    def on_clicked(self, *_):

        open_bluetooth(
            self.get_root()
        )

    def update(self):

        if not BluetoothService.available():

            self.set_state(
                subtitle=_("Unavailable"),
                icon="bluetooth_disabled.svg"
            )

            return

        if BluetoothService.is_blocked():

            self.set_state(
                subtitle=_("Blocked"),
                icon="bluetooth_disabled.svg"
            )

            return

        if BluetoothService.is_enabled():

            devices = BluetoothService.list_devices()

            connected = [d for d in devices if d["connected"]]

            if connected:

                self.set_state(
                    subtitle=f"{len(connected)} {_('Connected')}",
                    icon="bluetooth.svg"
                )

            else:

                self.set_state(
                    subtitle=_("On"),
                    icon="bluetooth.svg"
                )

        else:

            self.set_state(
                subtitle=_("Off"),
                icon="bluetooth_disabled.svg"
            )
