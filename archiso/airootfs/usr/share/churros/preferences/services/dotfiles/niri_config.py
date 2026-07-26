import os
import re
import tempfile


class NiriConfig:

    PATH = os.path.join(
        os.path.expanduser("~"),
        ".config",
        "niri",
        "config.kdl"
    )

    @classmethod
    def _read(cls):

        try:

            with open(
                cls.PATH,
                "r"
            ) as file:

                return file.read()

        except Exception:

            return ""

    @classmethod
    def _write_atomic(
        cls,
        content
    ):

        directory = os.path.dirname(
            cls.PATH
        )

        os.makedirs(
            directory,
            exist_ok=True
        )

        fd, tmp = tempfile.mkstemp(
            prefix="niri-config-",
            suffix=".kdl",
            dir=directory
        )

        try:

            with os.fdopen(
                fd,
                "w"
            ) as file:

                file.write(
                    content
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
    def _replace_block(
        cls,
        content,
        header,
        new_block
    ):

        pattern = re.compile(
            r"^(\s*)" + re.escape(header) + r"\s*\{[^{}]*\n(^[ \t]*\}?\s*$\n?)",
            re.MULTILINE
        )

        if pattern.search(
            content
        ):

            return pattern.sub(
                new_block,
                content,
                count=1
            )

        return None

    @classmethod
    def _replace_value(
        cls,
        content,
        key,
        value
    ):

        pattern = re.compile(
            r"^([ \t]*)" + re.escape(key) + r"[ \t]+\"?[^\"\n]+\"?([ \t]*\n)",
            re.MULTILINE
        )

        def repl(m):
            return m.group(1) + key + " \"" + str(value) + "\"" + m.group(2)

        new_content, n = pattern.subn(
            repl,
            content,
            count=1
        )

        if n:

            return new_content

        return None

    @classmethod
    def _append(
        cls,
        content,
        line
    ):

        if content and not content.endswith(
            "\n"
        ):

            content += "\n"

        return content + line + "\n"

    @classmethod
    def set_cursor_size(
        cls,
        size
    ):

        content = cls._read()

        pattern = re.compile(
            r"^cursor\s*\{([^}]*)\}",
            re.MULTILINE | re.DOTALL
        )

        match = pattern.search(
            content
        )

        if match:

            block = match.group(
                1
            )

            new_block = re.sub(
                r"xcursor-size[ \t]+[0-9]+",
                "xcursor-size " + str(
                    int(size)
                ),
                block,
                count=1
            )

            if new_block == block:

                if re.search(
                    r"xcursor-size",
                    block
                ):

                    new_block = re.sub(
                        r"xcursor-size[ \t]+[0-9]+",
                        "xcursor-size " + str(
                            int(size)
                        ),
                        block
                    )

                else:

                    new_block = block + "    xcursor-size " + str(
                        int(size)
                    ) + "\n"

            new_full = "cursor {" + new_block + "}"

            new_content = pattern.sub(
                new_full,
                content,
                count=1
            )

        else:

            new_content = cls._append(
                content,
                "cursor {\n    xcursor-size " + str(
                    int(size)
                ) + "\n}"
            )

        cls._write_atomic(
            new_content
        )

    @classmethod
    def set_keyboard_layout(
        cls,
        layout
    ):

        content = cls._read()

        pattern = re.compile(
            r"keyboard\s*\{([^{}]*?)xkb\s*\{([^{}]*)\}",
            re.DOTALL
        )

        match = pattern.search(
            content
        )

        if match:

            pre = match.group(
                1
            )

            xkb_block = match.group(
                2
            )

            new_xkb = re.sub(
                r"layout[ \t]+\"[^\"]+\"",
                "layout \"" + str(
                    layout
                ) + "\"",
                xkb_block,
                count=1
            )

            if new_xkb == xkb_block:

                if re.search(
                    r"layout",
                    xkb_block
                ):

                    new_xkb = re.sub(
                        r"layout[ \t]+\"[^\"]+\"",
                        "layout \"" + str(
                            layout
                        ) + "\"",
                        xkb_block
                    )

                else:

                    new_xkb = xkb_block + "    layout \"" + str(
                        layout
                    ) + "\"\n"

            new_full = "keyboard {" + pre + "xkb {" + new_xkb + "}"

            new_content = pattern.sub(
                new_full,
                content,
                count=1
            )

        else:

            block = (
                "input {\n"
                "    keyboard {\n"
                "        xkb {\n"
                "            layout \"" + str(layout) + "\"\n"
                "        }\n"
                "    }\n"
                "}\n"
            )

            new_content = cls._append(
                content,
                block.rstrip(
                    "\n"
                )
            )

        cls._write_atomic(
            new_content
        )

    @classmethod
    def set_wallpaper_startup(
        cls,
        path
    ):

        content = cls._read()

        pattern = re.compile(
            r"^spawn-at-startup\s+\"swaybg\"[^\n]*\n",
            re.MULTILINE
        )

        new_line = (
            "spawn-at-startup \"swaybg\" \"-i\" \"" + path + "\" \"-m\" \"fill\"\n"
        )

        if pattern.search(
            content
        ):

            new_content = pattern.sub(
                new_line,
                content,
                count=1
            )

        else:

            new_content = cls._append(
                content,
                new_line.rstrip(
                    "\n"
                )
            )

        cls._write_atomic(
            new_content
        )

    @classmethod
    def add_spawn_at_startup(
        cls,
        command
    ):

        content = cls._read()

        pattern = re.compile(
            r"^spawn-at-startup\s+\"" + re.escape(
                command.split(
                    "\""
                )[0]
            ) + "\"[^\n]*\n",
            re.MULTILINE
        )

        new_line = "spawn-at-startup " + command + "\n"

        if pattern.search(
            content
        ):

            new_content = pattern.sub(
                new_line,
                content,
                count=1
            )

        else:

            new_content = cls._append(
                content,
                new_line.rstrip(
                    "\n"
                )
            )

        cls._write_atomic(
            new_content
        )

    @classmethod
    def add_keybind(
        cls,
        keybind,
        action
    ):

        content = cls._read()

        pattern = re.compile(
            r"^[ \t]+" + re.escape(keybind) + r"[ \t]+\{[^\n]*\n",
            re.MULTILINE
        )

        new_line = "    " + keybind + " { " + action + "; }\n"

        if pattern.search(
            content
        ):

            new_content = pattern.sub(
                new_line,
                content,
                count=1
            )

        else:

            binds_pattern = re.compile(
                r"^binds\s*\{",
                re.MULTILINE
            )

            if binds_pattern.search(
                content
            ):

                new_content = binds_pattern.sub(
                    "binds {\n" + new_line,
                    content,
                    count=1
                )

            else:

                new_content = cls._append(
                    content,
                    "binds {\n" + new_line + "}\n"
                )

        cls._write_atomic(
            new_content
        )
