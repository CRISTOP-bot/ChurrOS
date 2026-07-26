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
