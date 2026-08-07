import subprocess
from datetime import datetime

import gi

gi.require_version("Gtk", "4.0")

from widgets.page import Page
from widgets.group import Group
from widgets.row import Row


class DateTimePage(Page):

    def __init__(self, navigator):

        super().__init__(
            navigator,
            "Fecha y hora",
            "Configura la hora, fecha y zona horaria del sistema",
        )

        self._build()

    def _build(self):

        info = Group("Estado actual")

        info.add(
            Row(
                title="Hora del sistema",
                subtitle=datetime.now().strftime("%H:%M:%S"),
                icon="system.svg",
            )
        )

        info.add(
            Row(
                title="Fecha",
                subtitle=datetime.now().strftime("%A %d de %B de %Y"),
                icon="system.svg",
            )
        )

        info.add(
            Row(
                title="Zona horaria",
                subtitle=self._get_timezone(),
                icon="system.svg",
            )
        )

        info.add(
            Row(
                title="Reloj hardware (RTC)",
                subtitle=self._get_rtc_date(),
                icon="system.svg",
            )
        )

        self.add(info)

        actions = Group("Acciones")

        actions.add(
            Row(
                title="Sincronizar hora con internet",
                subtitle="Ejecuta timedatectl set-ntp true (requiere systemd-timesyncd)",
                icon="system.svg",
                callback=lambda *_: self._sync_ntp(),
            )
        )

        self.add(actions)

        zones = Group("Cambiar zona horaria")

        zones.add(
            Row(
                title="timedatectl list-timezones",
                subtitle="Abre un selector interactivo de zonas horarias en la terminal",
                icon="system.svg",
                callback=lambda *_: self._change_timezone(),
            )
        )

        self.add(zones)

    @staticmethod
    def _get_timezone():

        try:
            r = subprocess.run(
                ["timedatectl", "show", "--property=Timezone", "--value"],
                capture_output=True, text=True, timeout=3
            )
            return r.stdout.strip()
        except Exception:
            return "Desconocida"

    @staticmethod
    def _get_rtc_date():

        try:
            r = subprocess.run(
                ["timedatectl", "show", "--property=RTCTime", "--value"],
                capture_output=True, text=True, timeout=3
            )
            raw = r.stdout.strip()
            if raw and raw != "n/a":
                return raw
            return "No disponible"
        except Exception:
            return "No disponible"

    def _sync_ntp(self):

        try:
            subprocess.Popen(
                ["foot", "-e", "sudo", "timedatectl", "set-ntp", "true"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
        except Exception:
            pass

    def _change_timezone(self):

        try:
            subprocess.Popen(
                ["foot", "-e", "sh", "-c", "echo 'Selecciona una zona horaria...'; timedatectl list-timezones | fzf | xargs -r sudo timedatectl set-timezone; exec bash"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
        except Exception:
            try:
                subprocess.Popen(
                    ["foot", "-e", "sh", "-c", "timedatectl list-timezones | less"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True,
                )
            except Exception:
                pass