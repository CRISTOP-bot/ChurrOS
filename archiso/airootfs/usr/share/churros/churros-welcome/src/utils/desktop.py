import subprocess

import gi

gi.require_version("Gio", "2.0")
gi.require_version("Gtk", "4.0")

from gi.repository import Gio, Gtk


def launch_application(command: str):

    try:

        subprocess.Popen([command])

    except FileNotFoundError:
        pass


def open_terminal():

    launch_application("foot")


def open_browser():

    launch_application("firefox")


def launch_installer(parent_window=None):

    installer = Gio.DesktopAppInfo.new("calamares.desktop")

    if installer is not None:

        installer.launch(None, None)

        return True

    if parent_window is not None:

        dialog = Gtk.AlertDialog()

        dialog.set_message("Installer not available on this system.")
        dialog.set_modal(True)

        dialog.show(parent_window)

    else:

        dialog = Gtk.AlertDialog()

        dialog.set_message("Installer not available on this system.")
        dialog.set_modal(True)

        dialog.show()

    return False


def open_tour():

    try:

        subprocess.Popen(
            [
                "yelp",
                "help:churros"
            ]
        )

    except FileNotFoundError:

        pass
