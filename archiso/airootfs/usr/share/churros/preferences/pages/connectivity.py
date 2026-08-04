import threading
import gi

gi.require_version("Gtk", "4.0")

from gi.repository import GLib, Gtk

from widgets.page import Page
from widgets.group import Group
from widgets.row import Row
from widgets.switch_row import SwitchRow

from services.connectivity import ConnectivityService


class ConnectivityPage(Page):

    def __init__(self, navigator):

        super().__init__(
            navigator,
            "Conectividad",
            "Wi-Fi y Bluetooth"
        )

        self.wifi_group = Group("Wi-Fi")
        self.bluetooth_group = Group("Bluetooth")

        self.add(self.wifi_group)
        self.add(self.bluetooth_group)

        self.wifi_group.add(Row(title="Cargando..."))
        self.bluetooth_group.add(Row(title="Cargando..."))

        threading.Thread(target=self.load, daemon=True).start()

    def load(self):

        data = {
            "wifi_available": ConnectivityService.wifi_available(),
            "wifi_enabled": ConnectivityService.wifi_enabled(),
            "current_network": ConnectivityService.current_network(),
            "wifi_networks": ConnectivityService.wifi_networks_full(),
            "bluetooth_available": ConnectivityService.bluetooth_available(),
            "bluetooth_enabled": ConnectivityService.bluetooth_enabled(),
            "bluetooth_devices": ConnectivityService.bluetooth_devices(),
        }

        GLib.idle_add(self.populate, data)

    def populate(self, data):

        self.wifi_group.clear()

        if not data["wifi_available"]:
            self.wifi_group.add(
                Row(title="No se encontró un adaptador Wi-Fi")
            )
        else:
            self.wifi_group.add(
                SwitchRow(
                    title="Activar Wi-Fi",
                    active=data["wifi_enabled"],
                    callback=self.on_wifi
                )
            )

            current = data["current_network"]

            if current:
                current_row = Row(
                    title="Red actual",
                    subtitle=current,
                    callback=lambda *_: self._prompt_forget(current)
                )
                self.wifi_group.add(current_row)

            networks = data["wifi_networks"]

            if networks:
                for net in networks:
                    self.wifi_group.add(self._make_network_row(net, current))
            else:
                self.wifi_group.add(
                    Row(title="No se encontraron redes")
                )

            self.wifi_group.add(
                Row(
                    title="Recargar redes",
                    subtitle="Forzar un nuevo escaneo",
                    callback=lambda *_: GLib.timeout_add(250, self.reload)
                )
            )

        #
        # Bluetooth
        #

        self.bluetooth_group.clear()

        if not data["bluetooth_available"]:
            self.bluetooth_group.add(
                Row(title="No se encontró un adaptador Bluetooth")
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
                    Row(title="No hay dispositivos")
                )

        return False

    def _make_network_row(self, net, current):

        ssid = net.get("ssid", "?")
        signal = net.get("signal", 0)
        security = net.get("security", "")
        connected = net.get("connected", False) or ssid == current
        saved = net.get("saved", False)

        subtitle_parts = ["Señal: {}%".format(signal)]

        if security:
            subtitle_parts.append(security)

        if connected:
            subtitle_parts.append("conectado")
        elif saved:
            subtitle_parts.append("guardada")

        subtitle = " · ".join(subtitle_parts)

        row = Row(
            title=ssid,
            subtitle=subtitle,
            callback=lambda *_, s=ssid, sec=security: self._on_network_clicked(s, sec)
        )

        gesture = Gtk.GestureClick()
        gesture.set_button(3)
        gesture.connect(
            "pressed",
            lambda *_, s=ssid: self._prompt_forget(s)
        )
        row.add_controller(gesture)

        return row

    def _on_network_clicked(self, ssid, security):

        if not security:
            self._do_connect(ssid, None)
            return

        self._prompt_password(ssid)

    def _prompt_password(self, ssid):

        dialog = Gtk.AlertDialog()
        dialog.set_heading("Conectar a {}".format(ssid))
        dialog.set_modal(True)
        dialog.set_buttons(["Cancelar", "Conectar"])

        label = Gtk.Label(
            label="Introduce la contraseña de la red Wi-Fi:"
        )
        label.set_margin_top(14)
        label.set_margin_start(14)
        label.set_margin_end(14)

        entry = Gtk.PasswordEntry()
        entry.set_show_peek_icon(True)
        entry.set_margin_start(14)
        entry.set_margin_end(14)
        entry.set_margin_bottom(14)

        box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=12
        )
        box.append(label)
        box.append(entry)

        dialog.set_extra_child(box)

        entry.connect("activate", lambda *_: dialog.choose_finish(dialog.choose(self.get_root())))

        dialog.choose(
            self.get_root(),
            None,
            lambda d, r: self._on_password_response(d, r, ssid, entry)
        )

    def _on_password_response(self, dialog, result, ssid, entry):

        try:

            response = dialog.choose_finish(result)

        except Exception:

            return

        if response != 1:
            return

        password = entry.get_text() or ""

        if not password:
            self._show_toast("Se requiere contraseña para esa red.")
            return

        self._do_connect(ssid, password)

    def _do_connect(self, ssid, password):

        def work():

            ok, err = ConnectivityService.wifi_connect(ssid, password)

            if ok:
                GLib.idle_add(self.reload)
            else:
                GLib.idle_add(self._show_toast, "No se pudo conectar: " + (err or "error desconocido"))

        threading.Thread(target=work, daemon=True).start()

    def _prompt_forget(self, ssid):

        dialog = Gtk.AlertDialog()
        dialog.set_heading("Olvidar red")
        dialog.set_message("¿Olvidar la configuración de la red '{}'?".format(ssid))
        dialog.set_modal(True)
        dialog.set_buttons(["Cancelar", "Olvidar"])

        dialog.choose(
            self.get_root(),
            None,
            lambda d, r: self._on_forget_response(d, r, ssid)
        )

    def _on_forget_response(self, dialog, result, ssid):

        try:

            response = dialog.choose_finish(result)

        except Exception:

            return

        if response != 1:
            return

        def work():

            ConnectivityService.wifi_forget(ssid)
            GLib.idle_add(self.reload)

        threading.Thread(target=work, daemon=True).start()

    def _show_toast(self, message):

        try:

            root = self.get_root()

            if root is not None and hasattr(root, "toast"):

                root.toast.add_notification(message)

                return

        except Exception:

            pass

        print("[connectivity]", message)

    def reload(self):

        threading.Thread(target=self.load, daemon=True).start()

        return False

    def on_wifi(self, active):

        ConnectivityService.set_wifi(active)

        if active:
            GLib.timeout_add(1000, self.reload)
        else:
            GLib.timeout_add(250, self.reload)

    def on_bluetooth(self, active):

        ConnectivityService.set_bluetooth(active)
