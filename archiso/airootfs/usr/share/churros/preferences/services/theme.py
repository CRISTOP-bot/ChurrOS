import subprocess

from services.settings import SettingsService


class ThemeService:

    @classmethod
    def is_dark(cls):

        value = SettingsService.get(
            "theme.dark",
            None
        )

        if value is not None:

            return value

        try:

            result = subprocess.run(

                [
                    "gsettings",
                    "get",
                    "org.gnome.desktop.interface",
                    "color-scheme"
                ],

                capture_output=True,
                text=True,
                timeout=2

            )

            dark = "dark" in result.stdout.lower()

        except Exception:

            dark = False

        SettingsService.set(
            "theme.dark",
            dark
        )

        return dark

    @classmethod
    def set(cls, dark):

        SettingsService.set(
            "theme.dark",
            dark
        )

        try:

            subprocess.run(

                [
                    "gsettings",
                    "set",
                    "org.gnome.desktop.interface",
                    "color-scheme",
                    "prefer-dark" if dark else "default"
                ],

                timeout=2

            )

        except Exception:

            pass

    @classmethod
    def toggle(cls):

        cls.set(

            not cls.is_dark()

        )