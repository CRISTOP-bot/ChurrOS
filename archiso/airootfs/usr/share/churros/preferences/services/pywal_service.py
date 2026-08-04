import json
import os
import subprocess

from services.settings import SettingsService
from services.accent import AccentService


class PywalService:

    """Punto de integracion con pywal para colores dinamicos.

    Si pywal no esta instalado o el wallpaper actual no existe,
    los metodos devuelven False / None sin levantar excepciones.
    """

    CACHE_FILE = os.path.expanduser(
        "~/.cache/wal/colors.json"
    )

    @classmethod
    def available(cls):

        try:

            return subprocess.call(
                ["which", "wal"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            ) == 0

        except Exception:

            return False

    @classmethod
    def _current_wallpaper(cls):

        from services.wallpaper import WallpaperService

        path = WallpaperService.current()

        if path and os.path.isfile(path):

            return path

        default = "/usr/share/churros/wallpapers/default.jpeg"

        if os.path.isfile(default):

            return default

        return None

    @classmethod
    def generate(cls):

        """Corre `wal -i <wallpaper>` y exporta colors.json.

        Devuelve la paleta (dict) o None si pywal no esta disponible.
        """

        wallpaper = cls._current_wallpaper()

        if not wallpaper:

            return None

        if not cls.available():

            return None

        try:

            subprocess.call(
                [
                    "wal",
                    "-q",
                    "-i", wallpaper,
                    "-n",
                    "-e"
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

        except Exception:

            return None

        return cls.read_cache()

    @classmethod
    def read_cache(cls):

        try:

            with open(cls.CACHE_FILE, "r", encoding="utf-8") as f:

                return json.load(f)

        except Exception:

            return None

    @classmethod
    def enabled(cls):

        return SettingsService.get(
            "theme.dynamic_colors",
            False
        )

    @classmethod
    def enable(cls):

        SettingsService.set("theme.dynamic_colors", True)

        palette = cls.generate()

        if palette is None:

            return False

        cls.apply_accent(palette)

        return True

    @classmethod
    def disable(cls):

        SettingsService.set("theme.dynamic_colors", False)

        AccentService.set(AccentService.current())

        return True

    @classmethod
    def toggle(cls, value):

        if value:

            return cls.enable()

        return cls.disable()

    @classmethod
    def apply_accent(cls, palette):

        """Toma el color principal de la paleta y lo aplica como accent."""

        if not isinstance(palette, dict):

            return False

        colors = palette.get("colors") or {}

        specials = palette.get("special") or {}

        hex_color = (
            specials.get("background")
            or specials.get("foreground")
            or colors.get("color0")
        )

        if not hex_color:

            return False

        hex_color = hex_color.lstrip("#")

        if len(hex_color) != 6:

            return False

        AccentService.set_hex("#" + hex_color)

        return True

    @classmethod
    def regenerate_if_enabled(cls):

        """Hook llamado por WallpaperService.set tras cambiar el wallpaper.

        Si el modo dynamic_colors esta activo, regenera la paleta y la
        aplica como accent. No se ejecuta si esta desactivado.
        """

        if not cls.enabled():

            return False

        palette = cls.generate()

        if palette is None:

            return False

        return cls.apply_accent(palette)
