import subprocess

from services.settings import SettingsService


class FontService:

    DEFAULT = "Inter"

    @classmethod
    def available(cls):

        try:

            result = subprocess.run(
                ["fc-list", ":", "family"],
                capture_output=True,
                text=True,
                timeout=2
            )

            fonts = set()

            for line in result.stdout.splitlines():

                for family in line.split(","):

                    family = family.strip()

                    if family:
                        fonts.add(family)

            return sorted(fonts)

        except Exception:

            return [cls.DEFAULT, "Cantarell", "Roboto", "Sans"]

    @classmethod
    def current(cls):
        return SettingsService.get("fonts.family", cls.DEFAULT)

    @classmethod
    def set(cls, family):

        SettingsService.set("fonts.family", family)

        try:

            subprocess.run(
                [
                    "gsettings",
                    "set",
                    "org.gnome.desktop.interface",
                    "font-name",
                    family + " 11"
                ],
                capture_output=True,
                timeout=2
            )

        except Exception:

            pass

        try:

            subprocess.run(
                [
                    "gsettings",
                    "set",
                    "org.gnome.desktop.interface",
                    "document-font-name",
                    family + " 11"
                ],
                capture_output=True,
                timeout=2
            )

        except Exception:

            pass

        try:

            subprocess.run(
                [
                    "gsettings",
                    "set",
                    "org.gnome.desktop.interface",
                    "monospace-font-name",
                    family + " Mono 10"
                ],
                capture_output=True,
                timeout=2
            )

        except Exception:

            pass

        # Forzar a las apps GTK a releer settings
        try:

            gi_settings_xd = None

            import gi
            gi.require_version("Gtk", "4.0")
            from gi.repository import Gtk, Pango

            settings = Gtk.Settings.get_default()
            settings.set_property("gtk-font-name", family + " 11")
            settings.set_property("gtk-fontconfig-timestamp", 0)

        except Exception:

            pass

    @classmethod
    def scale(cls):
        return SettingsService.get("fonts.scale", 1.0)

    @classmethod
    def set_scale(cls, scale):

        SettingsService.set("fonts.scale", scale)

        try:

            subprocess.run(
                [
                    "gsettings",
                    "set",
                    "org.gnome.desktop.interface",
                    "text-scaling-factor",
                    str(float(scale))
                ],
                capture_output=True,
                timeout=2
            )

        except Exception:

            pass

        try:

            import gi
            gi.require_version("Gtk", "4.0")
            from gi.repository import Gtk

            settings = Gtk.Settings.get_default()
            settings.set_property("gtk-xft-dpi", int(1024 * float(scale)))

        except Exception:

            pass
