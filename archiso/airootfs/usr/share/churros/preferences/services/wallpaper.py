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
        os.path.expanduser("~/.local/share/churros/wallpapers"),
        os.path.expanduser("~/Pictures/Wallpapers"),
        os.path.expanduser("~/Pictures")
    ]

    USER_DIR = os.path.expanduser(
        "~/.local/share/churros/wallpapers"
    )

    EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp", ".gif")

    @classmethod
    def current(cls):
        return SettingsService.get("wallpaper.path", "")

    @classmethod
    def set(cls, path):
        SettingsService.set("wallpaper.path", path)

        # Intentamos primero con awww (transiciones suaves)
        if shutil.which("awww") is not None:

            try:

                daemon = subprocess.run(
                    ["pgrep", "awww-daemon"],
                    capture_output=True,
                    text=True
                )

                if daemon.returncode != 0:

                    subprocess.Popen(
                        ["awww-daemon"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )

                    time.sleep(0.5)

                subprocess.run(
                    ["awww", "img", path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=3
                )

                return

            except Exception:
                pass

        # Fallback: matar swaybg existente y relanzar con la nueva imagen
        try:
            subprocess.run(
                ["pkill", "-x", "swaybg"],
                capture_output=True,
                timeout=2
            )
        except Exception:
            pass

        try:
            subprocess.Popen(
                ["swaybg", "-i", path, "-m", "fill"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
        except Exception:
            pass

    @classmethod
    def available(cls):

        wallpapers = []
        seen = set()

        for directory in cls.WALLPAPER_DIRS:

            if not os.path.isdir(directory):
                continue

            try:

                for file in sorted(os.listdir(directory)):

                    if file.lower().endswith(cls.EXTENSIONS):

                        full = os.path.join(directory, file)

                        if full not in seen:
                            seen.add(full)
                            wallpapers.append(full)

            except (PermissionError, OSError):
                continue

        return wallpapers

    @classmethod
    def import_image(cls, source_path):
        """Copia una imagen externa a la carpeta de wallpapers del usuario.

        Devuelve la ruta destino, o None si falla.
        """

        if not source_path or not os.path.isfile(source_path):
            return None

        try:

            os.makedirs(cls.USER_DIR, exist_ok=True)

        except OSError:
            return None

        base = os.path.basename(source_path)

        # Si el nombre ya existe, añadir sufijo
        dest = os.path.join(cls.USER_DIR, base)
        n = 1
        name, ext = os.path.splitext(base)
        while os.path.exists(dest):
            dest = os.path.join(cls.USER_DIR, f"{name}_{n}{ext}")
            n += 1

        try:

            try:
                import shutil as _shutil
                _shutil.copyfile(source_path, dest)
            except Exception:
                return None

            return dest

        except Exception:
            return None
