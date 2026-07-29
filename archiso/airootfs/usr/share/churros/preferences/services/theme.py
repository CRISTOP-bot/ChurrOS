import subprocess

from services.settings import SettingsService


class ThemeService:

    @classmethod
    def is_dark(cls):

        cached = SettingsService.get("theme.dark", None)

        if cached is not None:
            return cached

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

            if result.returncode == 0:

                value = result.stdout.strip().lower()
                dark = value == "'prefer-dark'"

                SettingsService.set("theme.dark", dark)

                return dark

        except Exception:

            pass

        return False

    @classmethod
    def set(cls, dark):

        SettingsService.set("theme.dark", bool(dark))

        try:

            subprocess.run(

                [
                    "gsettings",
                    "set",
                    "org.gnome.desktop.interface",
                    "color-scheme",
                    "prefer-dark" if dark else "default"
                ],

                capture_output=True,
                timeout=2

            )

        except Exception:

            pass

    @classmethod
    def toggle(cls):

        cls.set(
            not cls.is_dark()
        )
