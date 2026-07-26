import os
import subprocess

from services.settings import SettingsService


class CursorService:

    CURSOR_DIRS = [

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
                    "cursor-theme"
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
    def set(cls, theme):

        SettingsService.set(

            "cursor.theme",

            theme

        )

        try:

            subprocess.run(

                [
                    "gsettings",
                    "set",
                    "org.gnome.desktop.interface",
                    "cursor-theme",
                    theme
                ],

                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL

            )

        except Exception:

            pass

    @classmethod
    def available(cls):

        cursors = []

        for directory in cls.CURSOR_DIRS:

            if not os.path.isdir(directory):

                continue

            for item in os.listdir(directory):

                path = os.path.join(
                    directory,
                    item
                )

                if not os.path.isdir(path):

                    continue

                if os.path.isdir(

                    os.path.join(
                        path,
                        "cursors"
                    )

                ):

                    cursors.append(item)

        return sorted(set(cursors))

    @classmethod
    def size(cls):

        try:

            result = subprocess.run(

                [
                    "gsettings",
                    "get",
                    "org.gnome.desktop.interface",
                    "cursor-size"
                ],

                capture_output=True,
                text=True,
                timeout=2

            )

            value = result.stdout.strip()

            if value.startswith("uint32"):

                value = value.replace("uint32", "").strip()

            return int(value)

        except Exception:

            return 24

    @classmethod
    def set_size(cls, size):

        try:

            subprocess.run(

                [
                    "gsettings",
                    "set",
                    "org.gnome.desktop.interface",
                    "cursor-size",
                    str(int(size))
                ],

                capture_output=True,
                timeout=2

            )

        except Exception:

            pass