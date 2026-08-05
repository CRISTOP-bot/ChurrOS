import os
import tempfile


class FootConfig:

    PATH = os.path.join(
        os.path.expanduser("~"),
        ".config",
        "foot",
        "foot.ini"
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
            prefix="foot-",
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
            ) or stripped == key + "=":

                prefix = lines[j][:len(lines[j]) - len(lines[j].lstrip())]

                lines[j] = prefix + key + "=" + str(
                    value
                ) + "\n"

                return True

        insert = "    " + key + "=" + str(
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

    @classmethod
    def set_dark(
        cls,
        dark
    ):

        lines = cls._read()

        target_section = "colors-dark" if dark else "colors-light"

        existing_dark = cls._find_section(
            lines,
            "colors-dark"
        ) != -1

        existing_light = cls._find_section(
            lines,
            "colors-light"
        ) != -1

        section_idx = cls._find_section(
            lines,
            target_section
        )

        if section_idx == -1:

            if dark and not existing_dark:

                lines.append(
                    "[colors-dark]\n"
                )

            elif not dark and not existing_light:

                lines.append(
                    "[colors-light]\n"
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

        return cls._get_key("main", "font", "JetBrainsMono Nerd Font:size=10")

    @classmethod
    def get_pad(cls):

        return cls._get_key("main", "pad", "8x8")

    @classmethod
    def get_cursor_style(cls):

        return cls._get_key("cursor", "style", "beam")

    @classmethod
    def get_cursor_blink(cls):

        v = cls._get_key("cursor", "blink", "yes")
        return v.lower() in ("yes", "true", "1")

    @classmethod
    def get_bell(cls):

        v = cls._get_key("bell", "urgent", "yes")
        return v.lower() in ("yes", "true", "1")

    @classmethod
    def get_hide_when_typing(cls):

        v = cls._get_key("mouse", "hide-when-typing", "yes")
        return v.lower() in ("yes", "true", "1")

    # ------------------------------------------------------------- Setters

    @classmethod
    def set_pad(cls, pad):

        lines = cls._read()
        cls._set_key(lines, "main", "pad", pad)
        cls._write_atomic(lines)

    @classmethod
    def set_cursor(cls, style, blink):

        lines = cls._read()
        cls._set_key(lines, "cursor", "style", style)
        cls._set_key(lines, "cursor", "blink", "yes" if blink else "no")
        cls._write_atomic(lines)

    @classmethod
    def set_bell(cls, urgent):

        lines = cls._read()
        cls._set_key(lines, "bell", "urgent", "yes" if urgent else "no")
        cls._set_key(lines, "bell", "notify", "yes" if urgent else "no")
        cls._write_atomic(lines)

    @classmethod
    def set_hide_when_typing(cls, hide):

        lines = cls._read()
        cls._set_key(lines, "mouse", "hide-when-typing", "yes" if hide else "no")
        cls._write_atomic(lines)

    @classmethod
    def reload(cls):

        try:
            import subprocess
            subprocess.Popen(
                ["pkill", "-SIGUSR1", "foot"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except Exception:
            pass

