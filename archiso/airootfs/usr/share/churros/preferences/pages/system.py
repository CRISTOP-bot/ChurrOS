import os
import subprocess

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GLib

from widgets.page import Page
from widgets.group import Group
from widgets.row import Row

from services.system import SystemService


class SystemPage(Page):

    def __init__(self, navigator):

        super().__init__(
            navigator,
            "Sistema",
            "Información del sistema"
        )

        #
        # Información
        #

        information = Group(
            "Información"
        )

        information.add(

            Row(

                title="Versión",

                icon="system.svg",

                value="ChurrOS Beta"

            )

        )

        information.add(

            Row(

                title="Edición",

                icon="system.svg",

                value="Developer Preview"

            )

        )

        information.add(

            Row(

                title="Hostname",

                icon="system.svg",

                value=SystemService.hostname()

            )

        )

        information.add(

            Row(

                title="Sesión",

                icon="system.svg",

                value=SystemService.session()

            )

        )

        self.add(
            information
        )

        #
        # Software
        #

        software = Group(
            "Software"
        )

        software.add(

            Row(

                title="Kernel",

                icon="applications.svg",

                value=SystemService.kernel()

            )

        )

        software.add(

            Row(

                title="Base",

                icon="applications.svg",

                value="Arch Linux"

            )

        )

        software.add(

            Row(

                title="Gestor de paquetes",

                icon="applications.svg",

                value="Pacman"

            )

        )

        self.add(
            software
        )

        #
        # Hardware
        #

        hardware = Group(
            "Hardware"
        )

        hardware.add(

            Row(

                title="Procesador",

                icon="about.svg",

                value=SystemService.cpu()

            )

        )

        hardware.add(

            Row(

                title="Memoria",

                icon="about.svg",

                value=SystemService.memory()

            )

        )

        hardware.add(

            Row(

                title="Gráficos",

                icon="about.svg",

                value=SystemService.gpu()

            )

        )

        self.add(
            hardware
        )

        #
        # Acciones
        #

        actions = Group("Acciones")

        actions.add(
            Row(
                title="Actualizar sistema",
                subtitle="Ejecuta pacman -Syu en una terminal",
                icon="system.svg",
                callback=lambda *_: self._update_system()
            )
        )

        self.add(actions)

    def _update_system(self):
        try:
            subprocess.Popen(
                ["foot", "-e", "sudo", "pacman", "-Syu"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
        except Exception:
            try:
                subprocess.Popen(
                    ["kitty", "-e", "sudo", "pacman", "-Syu"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True,
                )
            except Exception:
                pass