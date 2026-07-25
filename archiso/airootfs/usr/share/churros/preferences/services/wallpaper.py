import os
import shutil
import subprocess
import time

from services.settings import SettingsService


class WallpaperService:

    PROJECT_DIR = os.path.abspath(

        os.path.join(

            os.path.dirname(__file__),

            "..",

            ".."

        )

    )

    PROJECT_WALLPAPERS = os.path.join(

        PROJECT_DIR,

        "wallpapers"

    )

    WALLPAPER_DIRS = [

        PROJECT_WALLPAPERS,

        "/usr/share/churros/wallpapers",

        "/usr/share/backgrounds",

        os.path.expanduser(
            "~/Pictures/Wallpapers"
        )

    ]

    EXTENSIONS = (

        ".jpg",

        ".jpeg",

        ".png",

        ".webp"

    )

    @classmethod
    def current(cls):

        return SettingsService.get(

            "wallpaper.path",

            ""

        )

    @classmethod
    def set(cls, path):

        SettingsService.set(

            "wallpaper.path",

            path

        )

        if shutil.which("awww") is None:

            return

        #
        # Si el daemon no está ejecutándose,
        # intentamos iniciarlo.
        #

        daemon = subprocess.run(

            [

                "pgrep",

                "awww-daemon"

            ],

            capture_output=True,

            text=True

        )

        if daemon.returncode != 0:

            subprocess.Popen(

                [

                    "awww-daemon"

                ],

                stdout=subprocess.DEVNULL,

                stderr=subprocess.DEVNULL

            )

            time.sleep(0.5)

        subprocess.run(

            [

                "awww",

                "img",

                path

            ],

            stdout=subprocess.DEVNULL,

            stderr=subprocess.DEVNULL

        )

    @classmethod
    def available(cls):

        wallpapers = []

        for directory in cls.WALLPAPER_DIRS:

            if not os.path.isdir(directory):

                continue

            for file in sorted(os.listdir(directory)):

                if file.lower().endswith(cls.EXTENSIONS):

                    wallpapers.append(

                        os.path.join(

                            directory,

                            file

                        )

                    )

        return wallpapers