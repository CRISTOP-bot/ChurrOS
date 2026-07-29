import json
import os
import shutil
import subprocess

from services.accent import AccentService


CONFIG_PATH = os.path.expanduser("~/.config/waybar/config.jsonc")
STYLE_PATH = os.path.expanduser("~/.config/waybar/style.css")
COLORS_PATH = os.path.expanduser("~/.config/waybar/colors-waybar.css")


DEFAULTS = {
    "layer": "top",
    "position": "top",
    "spacing": 0,
    "height": 30,
    "font-size": 14,
    "font-family": "JetBrainsMono Nerd Font",
    "background": "#2a1612",
    "foreground": "#c9c4c3",
    "accent": "#DE8636",
    "background-alpha": 0.9,
}


def _read_jsonc(path):

    if not os.path.exists(path):
        return {}

    try:
        with open(path, "r") as f:
            raw = f.read()

        cleaned = []

        in_string = False
        in_comment = False
        escape = False

        for ch in raw:

            if in_comment:

                if ch == "\n":
                    in_comment = False
                    cleaned.append("\n")

                continue

            if in_string:

                cleaned.append(ch)

                if escape:
                    escape = False
                    continue

                if ch == "\\":
                    escape = True
                    continue

                if ch == '"':
                    in_string = False

                continue

            if ch == "/" and cleaned and cleaned[-1] == "/":

                cleaned.pop()
                in_comment = True
                continue

            if ch == '"':
                in_string = True

            cleaned.append(ch)

        return json.loads("".join(cleaned))

    except Exception:
        return {}


def _write_jsonc(path, data):

    os.makedirs(os.path.dirname(path), exist_ok=True)

    text = json.dumps(data, indent=2)

    text = text.replace("'", "\\'")

    lines = text.splitlines()

    out = []

    for line in lines:

        if ": {" in line or ": [" in line:
            out.append(line)
        else:
            out.append("  // " + line.strip().lstrip("{").rstrip("}"))

    with open(path, "w") as f:
        f.write("\n".join(out))


class WaybarService:

    @classmethod
    def config_path(cls):
        return CONFIG_PATH

    @classmethod
    def style_path(cls):
        return STYLE_PATH

    @classmethod
    def colors_path(cls):
        return COLORS_PATH

    @classmethod
    def defaults(cls):
        return dict(DEFAULTS)

    @classmethod
    def get(cls):

        cfg = _read_jsonc(CONFIG_PATH)

        colors = cls._read_colors()

        return {
            "layer":        cfg.get("layer", DEFAULTS["layer"]),
            "position":     cfg.get("position", DEFAULTS["position"]),
            "spacing":      cfg.get("spacing", DEFAULTS["spacing"]),
            "height":       cfg.get("height", DEFAULTS["height"]),
            "font-size":    colors.get("font-size", DEFAULTS["font-size"]),
            "font-family":  colors.get("font-family", DEFAULTS["font-family"]),
            "background":   colors.get("background", DEFAULTS["background"]),
            "foreground":   colors.get("foreground", DEFAULTS["foreground"]),
            "accent":       colors.get("accent", DEFAULTS["accent"]),
            "background-alpha": colors.get("background-alpha", DEFAULTS["background-alpha"]),
            "modules-left":   cfg.get("modules-left", []),
            "modules-center": cfg.get("modules-center", []),
            "modules-right":  cfg.get("modules-right", []),
        }

    @classmethod
    def set(cls, values, reload_kind="auto"):

        cfg = _read_jsonc(CONFIG_PATH)

        cfg["layer"] = values.get("layer", DEFAULTS["layer"])
        cfg["position"] = values.get("position", DEFAULTS["position"])
        cfg["spacing"] = int(values.get("spacing", DEFAULTS["spacing"]))
        cfg["height"] = int(values.get("height", DEFAULTS["height"]))

        for key in ("modules-left", "modules-center", "modules-right"):

            modules = values.get(key)
            if modules is not None:
                cfg[key] = modules

        _write_jsonc(CONFIG_PATH, cfg)

        cls._write_colors(values)

        if reload_kind == "style":
            cls.reload(full_restart=False)
        elif reload_kind == "full":
            cls.reload(full_restart=True)
        else:
            cls.reload(full_restart=False)

    @classmethod
    def _read_colors(cls):

        result = {}

        if not os.path.exists(COLORS_PATH):
            return result

        try:
            with open(COLORS_PATH, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("@import") or line.startswith("/*"):
                        continue
                    if line.startswith("@define-color"):
                        parts = line.split(maxsplit=2)
                        if len(parts) >= 3:
                            name = parts[1].lstrip("@")
                            value = parts[2].rstrip(";")
                            result[name] = value
        except Exception:
            pass

        return result

    @classmethod
    def _write_colors(cls, values):

        os.makedirs(os.path.dirname(COLORS_PATH), exist_ok=True)

        bg = values.get("background", DEFAULTS["background"])
        fg = values.get("foreground", DEFAULTS["foreground"])
        accent = values.get("accent", DEFAULTS["accent"])
        font_size = values.get("font-size", DEFAULTS["font-size"])
        font_family = values.get("font-family", DEFAULTS["font-family"])

        content = (
            f"@define-color background {bg};\n"
            f"@define-color foreground {fg};\n"
            f"@define-color color4 {accent};\n"
            f"@define-color color1 {accent};\n"
            f"@define-color font-size {font_size};\n"
            f"@define-color font-family '{font_family}';\n"
            f"@define-color background-alpha {values.get('background-alpha', 0.9)};\n"
        )

        with open(COLORS_PATH, "w") as f:
            f.write(content)

    @classmethod
    def reload(cls, full_restart=False):

        if shutil.which("pkill") is None:
            return

        if full_restart:

            try:
                subprocess.run(
                    ["pkill", "-x", "waybar"],
                    check=False,
                    timeout=2
                )
            except Exception:
                pass

        else:

            try:
                subprocess.run(
                    ["pkill", "-SIGUSR1", "waybar"],
                    check=False,
                    timeout=2
                )

                return

            except Exception:
                pass

        try:
            subprocess.Popen(
                ["waybar"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
        except Exception:
            pass

    @classmethod
    def reset(cls):

        if os.path.exists(CONFIG_PATH):
            os.remove(CONFIG_PATH)

        if os.path.exists(STYLE_PATH):
            os.remove(STYLE_PATH)

        if os.path.exists(COLORS_PATH):
            os.remove(COLORS_PATH)
