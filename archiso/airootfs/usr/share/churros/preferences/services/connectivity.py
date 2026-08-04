from services.backends.networkmanager import NetworkManagerBackend
from services.backends.bluetooth import BluetoothBackend

import sys
import os

try:

    sys.path.insert(
        0,
        os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "..",
                "services"
            )
        )
    )

    from wifi import WifiService as _WifiService

except Exception:

    _WifiService = None


class ConnectivityService:

    #
    # Wi-Fi
    #

    @classmethod
    def wifi_available(cls):

        return NetworkManagerBackend.wifi_available()

    @classmethod
    def wifi_enabled(cls):

        return NetworkManagerBackend.wifi_enabled()

    @classmethod
    def set_wifi(
        cls,
        enabled
    ):

        NetworkManagerBackend.set_wifi(
            enabled
        )

    @classmethod
    def current_network(cls):

        return NetworkManagerBackend.current_network()

    @classmethod
    def wifi_networks(cls):

        return NetworkManagerBackend.networks()

    @classmethod
    def wifi_networks_full(cls):

        """Lista de redes con ssid, signal, security, connected y saved.

        Usa el WifiService completo (que parsea SECURITY y ACTIVE) si
        esta disponible; si no, hace fallback al NetworkManagerBackend
        basico que solo devuelve ssid y signal.
        """

        if _WifiService is not None:

            try:

                data = _WifiService.get()

                return data["networks"]

            except Exception:

                return []

        networks = NetworkManagerBackend.networks()

        return [
            {
                "ssid": n["ssid"],
                "signal": n["signal"],
                "security": "",
                "connected": False,
                "saved": False
            }
            for n in networks
        ]

    @classmethod
    def wifi_connect(
        cls,
        ssid,
        password=None
    ):

        if _WifiService is None:

            cmd = ["nmcli", "device", "wifi", "connect", ssid]

            if password:

                cmd.extend(["password", password])

            try:

                import subprocess

                return subprocess.call(cmd) == 0, ""

            except Exception as exc:

                return False, str(exc)

        return _WifiService.connect(ssid, password)

    @classmethod
    def wifi_disconnect(cls):

        if _WifiService is None:

            try:

                import subprocess

                subprocess.call(
                    [
                        "nmcli",
                        "device",
                        "disconnect",
                        "wlan0"
                    ]
                )

            except Exception:

                pass

            return

        _WifiService.disconnect()

    @classmethod
    def wifi_forget(
        cls,
        ssid
    ):

        if _WifiService is None:

            try:

                import subprocess

                subprocess.call(
                    [
                        "nmcli",
                        "connection",
                        "delete",
                        ssid
                    ]
                )

            except Exception:

                pass

            return

        _WifiService.forget(ssid)

    #
    # Bluetooth
    #

    @classmethod
    def bluetooth_available(cls):

        return BluetoothBackend.adapter_available()

    @classmethod
    def bluetooth_enabled(cls):

        return BluetoothBackend.enabled()

    @classmethod
    def set_bluetooth(
        cls,
        enabled
    ):

        BluetoothBackend.set_enabled(
            enabled
        )

    @classmethod
    def bluetooth_devices(cls):

        return BluetoothBackend.devices()