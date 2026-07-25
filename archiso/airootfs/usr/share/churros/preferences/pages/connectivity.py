import threading
import gi

gi.require_version("Gtk", "4.0")

from gi.repository import GLib

from widgets.page import Page
from widgets.group import Group
from widgets.row import Row
from widgets.switch_row import SwitchRow

from services.connectivity import ConnectivityService


class ConnectivityPage(Page):

    def __init__(
        self,
        navigator
    ):

        super().__init__(

            navigator,

            "Conectividad",

            "Wi-Fi y Bluetooth"

        )

        self.wifi_group = Group(
            "Wi-Fi"
        )

        self.bluetooth_group = Group(
            "Bluetooth"
        )

        self.add(
            self.wifi_group
        )

        self.add(
            self.bluetooth_group
        )

        self.wifi_group.add(

            Row(

                title="Cargando..."

            )

        )

        self.bluetooth_group.add(

            Row(

                title="Cargando..."

            )

        )

        threading.Thread(

            target=self.load,

            daemon=True

        ).start()

    #
    # Cargar información
    #

    def load(
        self
    ):

        data = {

            "wifi_available": ConnectivityService.wifi_available(),

            "wifi_enabled": ConnectivityService.wifi_enabled(),

            "current_network": ConnectivityService.current_network(),

            "wifi_networks": ConnectivityService.wifi_networks(),

            "bluetooth_available": ConnectivityService.bluetooth_available(),

            "bluetooth_enabled": ConnectivityService.bluetooth_enabled(),

            "bluetooth_devices": ConnectivityService.bluetooth_devices()

        }

        GLib.idle_add(

            self.populate,

            data

        )

    #
    # Actualizar UI
    #

    def populate(
        self,
        data
    ):

        #
        # Wi-Fi
        #

        self.wifi_group.clear()

        if not data["wifi_available"]:

            self.wifi_group.add(

                Row(

                    title="No se encontró un adaptador Wi-Fi"

                )

            )

        else:

            self.wifi_group.add(

                SwitchRow(

                    title="Activar Wi-Fi",

                    active=data["wifi_enabled"],

                    callback=self.on_wifi

                )

            )

            self.wifi_group.add(

                Row(

                    title="Red actual",

                    subtitle=data["current_network"] or "No conectado"

                )

            )

            if data["wifi_networks"]:

                for network in data["wifi_networks"]:

                    self.wifi_group.add(

                        Row(

                            title=network["ssid"],

                            subtitle=f'Señal: {network["signal"]}%'

                        )

                    )

            else:

                self.wifi_group.add(

                    Row(

                        title="No se encontraron redes"

                    )

                )

        #
        # Bluetooth
        #

        self.bluetooth_group.clear()

        if not data["bluetooth_available"]:

            self.bluetooth_group.add(

                Row(

                    title="No se encontró un adaptador Bluetooth"

                )

            )

        else:

            self.bluetooth_group.add(

                SwitchRow(

                    title="Activar Bluetooth",

                    active=data["bluetooth_enabled"],

                    callback=self.on_bluetooth

                )

            )

            if data["bluetooth_devices"]:

                for device in data["bluetooth_devices"]:

                    self.bluetooth_group.add(

                        Row(

                            title=device["name"],

                            subtitle=device["mac"]

                        )

                    )

            else:

                self.bluetooth_group.add(

                    Row(

                        title="No hay dispositivos"

                    )

                )

        return False

    #
    # Eventos
    #

    def on_wifi(
        self,
        active
    ):

        ConnectivityService.set_wifi(
            active
        )

    def on_bluetooth(
        self,
        active
    ):

        ConnectivityService.set_bluetooth(
            active
        )