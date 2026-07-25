import os
import subprocess

from services.settings import SettingsService


class IconsService:

    ICON_DIRS = [

        "/usr/share/icons",

        os.path.expanduser(
            "~/.icons"
        ),

        os.path.expanduser(
            "~/.local/share/icons"
        )

    ]

    @classmethod
    def current(cls):

        try:

            result = subprocess.run(

                [

                    "gsettings",

                    "get",

                    "org.gnome.desktop.interface",

                    "icon-theme"

                ],

                capture_output=True,

                text=True

            )

            theme = result.stdout.strip().replace("'", "")

            if theme in cls.available():

                return theme

        except Exception:

            pass

        available = cls.available()

        if available:

            return available[0]

        return ""

    @classmethod
    def set(

        cls,

        theme

    ):

        SettingsService.set(

            "icons.theme",

            theme

        )

        try:

            subprocess.run(

                [

                    "gsettings",

                    "set",

                    "org.gnome.desktop.interface",

                    "icon-theme",

                    theme

                ],

                stdout=subprocess.DEVNULL,

                stderr=subprocess.DEVNULL

            )

        except Exception:

            pass

    @classmethod
    def available(cls):

        themes = []

        for directory in cls.ICON_DIRS:

            if not os.path.isdir(directory):

                continue

            for item in os.listdir(directory):

                path = os.path.join(

                    directory,

                    item

                )

                if not os.path.isdir(path):

                    continue

                if os.path.isfile(

                    os.path.join(

                        path,

                        "index.theme"

                    )

                ):

                    themes.append(item)

        return sorted(

            set(themes)

        )