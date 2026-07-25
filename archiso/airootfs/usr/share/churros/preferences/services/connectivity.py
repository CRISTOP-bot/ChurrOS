from services.backends.networkmanager import NetworkManagerBackend
from services.backends.bluetooth import BluetoothBackend


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