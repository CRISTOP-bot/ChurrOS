import subprocess

from services.settings import SettingsService


class FontService:

    DEFAULT = "Inter"

    @classmethod
    def available(cls):

        try:

            result = subprocess.run(

                [

                    "fc-list",

                    ":",

                    "family"

                ],

                capture_output=True,

                text=True,

                timeout=2

            )

            fonts = set()

            for line in result.stdout.splitlines():

                for family in line.split(","):

                    family = family.strip()

                    if family:

                        fonts.add(

                            family

                        )

            return sorted(

                fonts

            )

        except Exception:

            return [

                cls.DEFAULT,

                "Cantarell",

                "Roboto"

            ]

    @classmethod
    def current(cls):

        return SettingsService.get(

            "fonts.family",

            cls.DEFAULT

        )

    @classmethod
    def set(

        cls,

        family

    ):

        SettingsService.set(

            "fonts.family",

            family

        )

        try:

            subprocess.run(

                [

                    "gsettings",

                    "set",

                    "org.gnome.desktop.interface",

                    "font-name",

                    family

                ],

                timeout=2

            )

        except Exception:

            pass

    @classmethod
    def scale(cls):

        return SettingsService.get(

            "fonts.scale",

            1.0

        )

    @classmethod
    def set_scale(

        cls,

        scale

    ):

        SettingsService.set(

            "fonts.scale",

            scale

        )