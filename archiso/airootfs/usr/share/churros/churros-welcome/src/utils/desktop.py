import subprocess

import gi

gi.require_version("Gio", "2.0")
gi.require_version("Gtk", "4.0")

from gi.repository import Gio, Gtk


def launch_installer(parent_window=None):

    installer = Gio.DesktopAppInfo.new("calamares.desktop")

    if installer is not None:

        installer.launch(None, None)

        return True

    message = "Installer not available on this system."

    if parent_window is not None:

        dialog = Gtk.AlertDialog()
        dialog.set_message(message)
        dialog.set_modal(True)
        dialog.show(parent_window)

    else:

        dialog = Gtk.AlertDialog()
        dialog.set_message(message)
        dialog.set_modal(True)
        dialog.show()

    return False
