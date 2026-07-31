import os

from services.settings import SettingsService


HOME = os.path.expanduser("~")


class IconsService:

    ICON_DIRS = [
        "/usr/share/icons",
        os.path.join(HOME, ".icons"),
        os.path.join(HOME, ".local/share/icons"),
    ]

    @classmethod
    def current(cls):

        cached = SettingsService.get("icons.theme", "")
        if cached:
            return cached

        ini3 = os.path.join(HOME, ".config", "gtk-3.0", "settings.ini")
        if os.path.isfile(ini3):
            with open(ini3) as f:
                for line in f:
                    if line.strip().startswith("gtk-icon-theme-name="):
                        return line.split("=", 1)[1].strip()
        return "Adwaita"

    @classmethod
    def set(cls, theme):
        SettingsService.set("icons.theme", theme)

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
                if line.strip().startswith("gtk-icon-theme-name="):
                    lines.append(f"gtk-icon-theme-name={theme}")
                    seen = True
                else:
                    lines.append(line)
            if not seen:
                lines.append(f"gtk-icon-theme-name={theme}")
            if "[Settings]" not in "\n".join(lines):
                lines.insert(0, "[Settings]")
            with open(ini, "w") as f:
                f.write("\n".join(lines) + "\n")

    @classmethod
    def available(cls):

        themes = []
        for directory in cls.ICON_DIRS:
            if not os.path.isdir(directory):
                continue
            for item in os.listdir(directory):
                path = os.path.join(directory, item)
                if not os.path.isdir(path):
                    continue
                if os.path.isfile(os.path.join(path, "index.theme")):
                    themes.append(item)
        return sorted(set(themes))