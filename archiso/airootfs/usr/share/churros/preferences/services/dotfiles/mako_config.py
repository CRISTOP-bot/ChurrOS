import os
import tempfile


class MakoConfig:

    PATH = os.path.join(
        os.path.expanduser("~"),
        ".config",
        "mako",
        "config"
    )

    DEFAULTS = {
        "font": "JetBrainsMono Nerd Font:size=11",
        "background-color": "#1e1e2e",
        "text-color": "#cdd6f4",
        "border-color": "#f97316",
        "border-size": 2,
        "border-radius": 8,
        "padding": "12,16",
        "margin": 8,
        "default-timeout": 5000,
        "width": 380,
        "anchor": "top-right",
        "markup": True,
        "actions": True,
        "icons": True,
        "history": True,
        "max-icon-size": 48,
    }

    @classmethod
    def _read(cls):

        try:

            with open(
                cls.PATH,
                "r"
            ) as file:

                return file.readlines()

        except Exception:

            return []

    @classmethod
    def _write_atomic(
        cls,
        lines
    ):

        directory = os.path.dirname(
            cls.PATH
        )

        os.makedirs(
            directory,
            exist_ok=True
        )

        fd, tmp = tempfile.mkstemp(
            prefix="mako-",
            suffix=".cfg",
            dir=directory
        )

        try:

            with os.fdopen(
                fd,
                "w"
            ) as file:

                file.writelines(
                    lines
                )

            os.replace(
                tmp,
                cls.PATH
            )

        except Exception:

            try:

                os.unlink(
                    tmp
                )

            except OSError:

                pass

            raise

    @classmethod
    def _find_section(
        cls,
        lines,
        section
    ):

        for i, line in enumerate(
            lines
        ):

            stripped = line.strip()

            if stripped == "[" + section + "]":

                return i

        return -1

    @classmethod
    def _set_key(
        cls,
        lines,
        section,
        key,
        value
    ):

        section_idx = cls._find_section(
            lines,
            section
        )

        if section_idx == -1:

            lines.append(
                "\n[" + section + "]\n"
            )

            section_idx = len(lines) - 1

        end = len(lines)

        for j in range(
            section_idx + 1,
            len(lines)
        ):

            stripped = lines[j].strip()

            if stripped.startswith(
                "["
            ) and stripped.endswith(
                "]"
            ):

                end = j

                break

        for j in range(
            section_idx + 1,
            end
        ):

            stripped = lines[j].strip()

            if stripped.startswith(
                key + "="
            ) or stripped.startswith(
                key + " "
            ):

                prefix = lines[j][:len(lines[j]) - len(lines[j].lstrip())]

                lines[j] = prefix + key + "=" + str(
                    value
                ) + "\n"

                return True

        insert = key + "=" + str(
            value
        ) + "\n"

        lines.insert(
            end,
            insert
        )

        return True

    @classmethod
    def _set_key_bool(
        cls,
        lines,
        section,
        key,
        on
    ):

        return cls._set_key(
            lines,
            section,
            key,
            "true" if on else "false"
        )

    # ------------------------------------------------------------ Getters

    @classmethod
    def _get_key(cls, section, key, default=""):

        lines = cls._read()

        idx = cls._find_section(lines, section)

        if idx < 0:
            return default

        for j in range(idx + 1, len(lines)):

            stripped = lines[j].strip()

            if stripped.startswith("[") and stripped.endswith("]"):
                break

            if stripped.startswith(key + "="):
                return stripped.split("=", 1)[1].strip()

        return default

    @classmethod
    def _get_key_bool(cls, section, key, default=True):

        val = cls._get_key(section, key, None)

        if val is None:
            return default

        return val == "true"

    @classmethod
    def _get_key_int(cls, section, key, default=0):

        val = cls._get_key(section, key, None)

        if val is None:
            return default

        try:
            return int(val)
        except ValueError:
            return default

    @classmethod
    def get_font(cls):

        return cls._get_key(
            "default",
            "font",
            cls.DEFAULTS["font"]
        )

    @classmethod
    def get_background_color(cls):

        return cls._get_key(
            "default",
            "background-color",
            cls.DEFAULTS["background-color"]
        )

    @classmethod
    def get_text_color(cls):

        return cls._get_key(
            "default",
            "text-color",
            cls.DEFAULTS["text-color"]
        )

    @classmethod
    def get_border_color(cls):

        return cls._get_key(
            "default",
            "border-color",
            cls.DEFAULTS["border-color"]
        )

    @classmethod
    def get_border_size(cls):

        return cls._get_key_int(
            "default",
            "border-size",
            cls.DEFAULTS["border-size"]
        )

    @classmethod
    def get_border_radius(cls):

        return cls._get_key_int(
            "default",
            "border-radius",
            cls.DEFAULTS["border-radius"]
        )

    @classmethod
    def get_padding(cls):

        return cls._get_key(
            "default",
            "padding",
            cls.DEFAULTS["padding"]
        )

    @classmethod
    def get_margin(cls):

        return cls._get_key_int(
            "default",
            "margin",
            cls.DEFAULTS["margin"]
        )

    @classmethod
    def get_default_timeout(cls):

        return cls._get_key_int(
            "default",
            "default-timeout",
            cls.DEFAULTS["default-timeout"]
        )

    @classmethod
    def get_width(cls):

        return cls._get_key_int(
            "default",
            "width",
            cls.DEFAULTS["width"]
        )

    @classmethod
    def get_anchor(cls):

        return cls._get_key(
            "default",
            "anchor",
            cls.DEFAULTS["anchor"]
        )

    @classmethod
    def get_markup(cls):

        return cls._get_key_bool(
            "default",
            "markup",
            cls.DEFAULTS["markup"]
        )

    @classmethod
    def get_actions(cls):

        return cls._get_key_bool(
            "default",
            "actions",
            cls.DEFAULTS["actions"]
        )

    @classmethod
    def get_icons(cls):

        return cls._get_key_bool(
            "default",
            "icons",
            cls.DEFAULTS["icons"]
        )

    @classmethod
    def get_history(cls):

        return cls._get_key_bool(
            "default",
            "history",
            cls.DEFAULTS["history"]
        )

    @classmethod
    def get_max_icon_size(cls):

        return cls._get_key_int(
            "default",
            "max-icon-size",
            cls.DEFAULTS["max-icon-size"]
        )

    # ------------------------------------------------------------- Setters

    @classmethod
    def set_font(cls, font):

        lines = cls._read()

        cls._set_key(lines, "default", "font", font)

        cls._write_atomic(lines)

    @classmethod
    def set_appearance(
        cls,
        background_color=None,
        text_color=None,
        border_color=None,
        border_size=None,
        border_radius=None
    ):

        lines = cls._read()

        if background_color is not None:
            cls._set_key(lines, "default", "background-color",
                         background_color)

        if text_color is not None:
            cls._set_key(lines, "default", "text-color", text_color)

        if border_color is not None:
            cls._set_key(lines, "default", "border-color", border_color)

        if border_size is not None:
            cls._set_key(lines, "default", "border-size",
                         str(int(border_size)))

        if border_radius is not None:
            cls._set_key(lines, "default", "border-radius",
                         str(int(border_radius)))

        cls._write_atomic(lines)

    @classmethod
    def set_layout(
        cls,
        padding=None,
        margin=None,
        default_timeout=None,
        width=None
    ):

        lines = cls._read()

        if padding is not None:
            cls._set_key(lines, "default", "padding", padding)

        if margin is not None:
            cls._set_key(lines, "default", "margin", str(int(margin)))

        if default_timeout is not None:
            cls._set_key(lines, "default", "default-timeout",
                         str(int(default_timeout)))

        if width is not None:
            cls._set_key(lines, "default", "width", str(int(width)))

        cls._write_atomic(lines)

    @classmethod
    def set_anchor(cls, anchor):

        lines = cls._read()

        cls._set_key(lines, "default", "anchor", anchor)

        cls._write_atomic(lines)

    @classmethod
    def set_behaviors(
        cls,
        markup=None,
        actions=None,
        icons=None,
        history=None,
        max_icon_size=None
    ):

        lines = cls._read()

        if markup is not None:
            cls._set_key_bool(lines, "default", "markup", markup)

        if actions is not None:
            cls._set_key_bool(lines, "default", "actions", actions)

        if icons is not None:
            cls._set_key_bool(lines, "default", "icons", icons)

        if history is not None:
            cls._set_key_bool(lines, "default", "history", history)

        if max_icon_size is not None:
            cls._set_key(lines, "default", "max-icon-size",
                         str(int(max_icon_size)))

        cls._write_atomic(lines)

    @classmethod
    def set_color(cls, key, hex_color):

        lines = cls._read()

        cls._set_key(lines, "default", key, hex_color)

        cls._write_atomic(lines)

    @classmethod
    def reload(cls):

        try:

            import subprocess

            subprocess.Popen(
                ["makoctl", "reload"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

        except Exception:

            pass
