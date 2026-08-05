import os
import tempfile


class FuzzelConfig:

    PATH = os.path.join(
        os.path.expanduser("~"),
        ".config",
        "fuzzel",
        "fuzzel.ini"
    )

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
            prefix="fuzzel-",
            suffix=".ini",
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
    def set_font(
        cls,
        font
    ):

        lines = cls._read()

        cls._set_key(
            lines,
            "main",
            "font",
            font
        )

        cls._write_atomic(
            lines
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
    def get_font(cls):

        return cls._get_key("main", "font", "JetBrainsMono Nerd Font:size=13")

    @classmethod
    def get_icon_theme(cls):

        return cls._get_key("main", "icon-theme", "")

    @classmethod
    def get_width(cls):

        v = cls._get_key("main", "width", "48")
        try:
            return int(v)
        except Exception:
            return 48

    @classmethod
    def get_lines(cls):

        v = cls._get_key("main", "lines", "12")
        try:
            return int(v)
        except Exception:
            return 12

    @classmethod
    def get_horizontal_pad(cls):

        v = cls._get_key("main", "horizontal-pad", "36")
        try:
            return int(v)
        except Exception:
            return 36

    @classmethod
    def get_vertical_pad(cls):

        v = cls._get_key("main", "vertical-pad", "14")
        try:
            return int(v)
        except Exception:
            return 14

    @classmethod
    def get_inner_pad(cls):

        v = cls._get_key("main", "inner-pad", "4")
        try:
            return int(v)
        except Exception:
            return 4

    @classmethod
    def get_line_height(cls):

        v = cls._get_key("main", "line-height", "24")
        try:
            return int(v)
        except Exception:
            return 24

    @classmethod
    def get_letter_spacing(cls):

        v = cls._get_key("main", "letter-spacing", "1")
        try:
            return int(v)
        except Exception:
            return 1

    # ------------------------------------------------------------- Setters

    @classmethod
    def set_icon_theme(cls, theme):

        lines = cls._read()
        if theme:
            cls._set_key(lines, "main", "icon-theme", theme)
        else:
            cls._set_key(lines, "main", "icon-theme", "")
        cls._write_atomic(lines)

    @classmethod
    def set_layout(cls, width, lines, h_pad, v_pad, inner_pad, line_height, letter_spacing):

        lines = cls._read()
        cls._set_key(lines, "main", "width", str(int(width)))
        cls._set_key(lines, "main", "lines", str(int(lines)))
        cls._set_key(lines, "main", "horizontal-pad", str(int(h_pad)))
        cls._set_key(lines, "main", "vertical-pad", str(int(v_pad)))
        cls._set_key(lines, "main", "inner-pad", str(int(inner_pad)))
        cls._set_key(lines, "main", "line-height", str(int(line_height)))
        cls._set_key(lines, "main", "letter-spacing", str(int(letter_spacing)))
        cls._write_atomic(lines)

    @classmethod
    def set_color(cls, key, hex_color):

        lines = cls._read()
        cls._set_key(lines, "colors", key, hex_color)
        cls._write_atomic(lines)

    @classmethod
    def reload(cls):

        try:
            import subprocess
            subprocess.Popen(
                ["pkill", "-fuzzel"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except Exception:
            pass

