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
