import os

from services.settings import SettingsService


HOME = os.path.expanduser("~")


class CursorService:

    CURSOR_DIRS = [
        "/usr/share/icons",
        os.path.join(HOME, ".icons"),
        os.path.join(HOME, ".local/share/icons"),
    ]

    @classmethod
    def _write_gtk(cls, key, value):

        for ver in ("3.0", "4.0"):
            d = os.path.join(HOME, ".config", f"gtk-{ver}")
            os.makedirs(d, exist_ok=True)
            ini = os.path.join(d, "settings.ini")
            existing = ""
            if os.path.isfile(ini):
                with open(ini) as f:
                    existing = f.read()
            lines = []
            seen = False
            for line in existing.splitlines():
                if line.strip().startswith(f"{key}="):
                    lines.append(f"{key}={value}")
                    seen = True
                else:
                    lines.append(line)
            if not seen:
                lines.append(f"{key}={value}")
            if "[Settings]" not in "\n".join(lines):
                lines.insert(0, "[Settings]")
            with open(ini, "w") as f:
                f.write("\n".join(lines) + "\n")

    @classmethod
    def current(cls):

        cached = SettingsService.get("cursor.theme", "")
        if cached:
            return cached

        ini3 = os.path.join(HOME, ".config", "gtk-3.0", "settings.ini")
        if os.path.isfile(ini3):
            with open(ini3) as f:
                for line in f:
                    if line.strip().startswith("gtk-cursor-theme-name="):
                        return line.split("=", 1)[1].strip()
        return "default"

    @classmethod
    def set(cls, theme):
        SettingsService.set("cursor.theme", theme)
        cls._write_gtk("gtk-cursor-theme-name", theme)
        cls._write_gtk("gtk-cursor-theme-size", "24")

    @classmethod
    def available(cls):

        cursors = []
        for directory in cls.CURSOR_DIRS:
            if not os.path.isdir(directory):
                continue
            for item in os.listdir(directory):
                path = os.path.join(directory, item)
                if not os.path.isdir(path):
                    continue
                if os.path.isdir(os.path.join(path, "cursors")):
                    cursors.append(item)
        return sorted(set(cursors))

    @classmethod
    def size(cls):
        return SettingsService.get("cursor.size", 24)

    @classmethod
    def set_size(cls, size):
        size = int(size)
        SettingsService.set("cursor.size", size)
        cls._write_gtk("gtk-cursor-theme-size", str(size))