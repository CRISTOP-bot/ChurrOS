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
    def _parse_lines(cls, content):

        """Devuelve una lista de (line, depth, indent_str).

        depth cuenta el numero de bloques abiertos en esa linea.
        Las lineas con '{' incrementan depth para las siguientes.
        """

        lines = content.splitlines()
        depth = 0
        result = []
        for raw in lines:
            stripped = raw.strip()
            open_in_line = stripped.count("{")
            close_in_line = stripped.count("}")
            indent = raw[:len(raw) - len(raw.lstrip())]

            effective_depth = depth + max(open_in_line - close_in_line, 0)

            if stripped.endswith("{"):
                depth += 1
            elif "}" in stripped:
                depth -= stripped.count("}")

            result.append((raw, effective_depth, indent))

        return result

    @classmethod
    def _find_block(cls, content, path):

        """Encuentra (start_line_idx, end_line_idx) del bloque en path.

        path es una lista de nombres, p.ej. ['layout', 'border'].
        Devuelve indices sobre splitlines(); el bloque incluye la
        linea de apertura 'path[-1] {' y la linea de cierre '}'.
        """

        lines = content.splitlines()
        stack = []

        for i, raw in enumerate(lines):

            stripped = raw.strip()

            if not stripped or stripped.startswith("//"):
                continue

            if stripped.endswith("{"):

                name = stripped.rstrip("{").strip()
                name = re.sub(r'"\s*"$', '"', name).strip()
                name = name.split("=", 1)[0].strip()
                name = name.strip('"')

                stack.append((i, name))

            elif stripped == "}" or stripped.startswith("}"):

                if stack:

                    start_idx, name = stack[-1]

                    full_path = [n for _, n in stack]
                    if full_path == path:
                        return start_idx, i

                    stack.pop()

        return None, None

    @classmethod
    def _update_value_in_block(cls, content, path, key, value):

        """Actualiza o inserta 'key=value' dentro del bloque en path.

        Mantiene indentacion y formato de lineas existentes. Si el
        bloque no existe, devuelve None (el caller debe crearlo).
        """

        lines = content.splitlines()

        start, end = cls._find_block(content, path)

        if start is None:
            return None

        header_line = lines[start]
        m = re.match(r"^(\s*)", header_line)
        base_indent = m.group(1) if m else ""
        inner_indent = base_indent + "    "

        for j in range(start + 1, end):

            stripped = lines[j].strip()

            if stripped.startswith(key + " ") or stripped.startswith(key + "="):

                lines[j] = inner_indent + key + " " + str(value)
                return "\n".join(lines)

        insert_line = inner_indent + key + " " + str(value)
        lines.insert(end, insert_line)

        return "\n".join(lines)

    @classmethod
    def _create_block(cls, content, path, body_lines=None):

        """Crea el bloque en path al final del config.

        Crea cada padre si no existe. body_lines: lista de strings
        para el contenido interno (con indentacion apropiada).
        """

        if body_lines is None:
            body_lines = []

        current = path[:-1]
        block_name = path[-1]

        for i in range(1, len(path) + 1):

            sub_path = path[:i]
            _, found_end = cls._find_block(content, list(sub_path))

            if found_end is None:

                indent = "    " * (len(sub_path) - 1)

                lines = body_lines if i == len(path) else []

                block_str = indent + sub_path[-1] + " {\n"

                for ln in lines:
                    block_str += indent + "    " + ln + "\n"

                block_str += indent + "}\n"

                if content and not content.endswith("\n"):
                    content += "\n"

                content += block_str

                return content

        return content

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

    # --------------------------------------------------------------- Layout

    @classmethod
    def set_gaps(
        cls,
        gaps
    ):

        content = cls._read()
        result = cls._update_value_in_block(
            content,
            ["layout"],
            "gaps",
            str(int(gaps))
        )

        if result is None:

            result = cls._create_block(
                content,
                ["layout"],
                ["gaps " + str(int(gaps))]
            )

        cls._write_atomic(result)

    # --------------------------------------------------------------- Border

    @classmethod
    def set_border(
        cls,
        on,
        width=None,
        active_color=None,
        inactive_color=None
    ):

        content = cls._read()

        start, end = cls._find_block(content, ["layout", "border"])

        if not on:

            if start is not None:

                lines = content.splitlines(True)
                del lines[start:end + 1]
                cls._write_atomic("".join(lines))

            return

        if start is None:

            body = []
            if width is not None:
                body.append("width " + str(int(width)))
            if active_color is not None:
                body.append("active-color \"" + str(active_color) + "\"")
            if inactive_color is not None:
                body.append("inactive-color \"" + str(inactive_color) + "\"")

            _, parent_end = cls._find_block(content, ["layout"])

            if parent_end is None:

                result = cls._create_block(
                    content,
                    ["layout", "border"],
                    body
                )

            else:

                lines = content.splitlines(True)
                indent = "    "
                block_str = indent + "border {\n"
                for ln in body:
                    block_str += indent + "    " + ln + "\n"
                block_str += indent + "}\n"
                lines.insert(parent_end, block_str)
                result = "".join(lines)

            cls._write_atomic(result)

            return

        lines = content.splitlines(False)

        child_indent = "            "

        if width is not None:

            updated = cls._update_value_in_block(
                "\n".join(lines),
                ["layout", "border"],
                "width",
                str(int(width))
            )

            if updated is not None:
                lines = updated.splitlines(False)

        if active_color is not None:

            updated = cls._update_value_in_block(
                "\n".join(lines),
                ["layout", "border"],
                "active-color",
                "\"" + str(active_color) + "\""
            )

            if updated is not None:
                lines = updated.splitlines(False)

        if inactive_color is not None:

            updated = cls._update_value_in_block(
                "\n".join(lines),
                ["layout", "border"],
                "inactive-color",
                "\"" + str(inactive_color) + "\""
            )

            if updated is not None:
                lines = updated.splitlines(False)

        cls._write_atomic("\n".join(lines))

    # ----------------------------------------------------------- Focus ring

    @classmethod
    def set_focus_ring(
        cls,
        on
    ):

        content = cls._read()

        start, end = cls._find_block(content, ["layout", "focus-ring"])

        if not on:

            if start is not None:

                lines = content.splitlines(True)
                del lines[start:end + 1]
                cls._write_atomic("".join(lines))

            else:

                parent_end = None
                _, parent_end = cls._find_block(content, ["layout"])

                if parent_end is None:

                    result = cls._create_block(
                        content,
                        ["layout", "focus-ring"],
                        ["off"]
                    )

                else:

                    lines = content.splitlines(True)
                    block_str = "    focus-ring {\n        off\n    }\n"
                    lines.insert(parent_end, block_str)
                    result = "".join(lines)

                cls._write_atomic(result)

            return

        if start is not None:

            lines = content.splitlines(False)

            inner = [l for l in lines[start + 1:end]
                     if l.strip() and l.strip() != "off"]

            has_on = any(l.strip() == "on" for l in inner)

            if not has_on:

                insert_idx = None
                for k in range(start + 1, end):
                    if lines[k].strip():
                        insert_idx = k
                        break

                if insert_idx is None:

                    insert_idx = end

                    lines.insert(insert_idx, "        on")

                else:

                    lines.insert(insert_idx, "        on")

                result = "\n".join(lines)

            else:

                result = "\n".join(lines)

            cls._write_atomic(result)

            return

        parent_end = None
        _, parent_end = cls._find_block(content, ["layout"])

        if parent_end is None:

            result = cls._create_block(
                content,
                ["layout", "focus-ring"],
                ["on"]
            )

        else:

            lines = content.splitlines(True)
            block_str = "    focus-ring {\n        on\n    }\n"
            lines.insert(parent_end, block_str)
            result = "".join(lines)

        cls._write_atomic(result)

    # ---------------------------------------------------------------- Blur

    @classmethod
    def set_blur(
        cls,
        passes=None,
        offset=None,
        noise=None,
        saturation=None
    ):

        content = cls._read()

        start, end = cls._find_block(content, ["blur"])

        changes = []
        if passes is not None:
            changes.append(("passes", str(int(passes))))
        if offset is not None:
            changes.append(("offset", str(float(offset))))
        if noise is not None:
            changes.append(("noise", str(float(noise))))
        if saturation is not None:
            changes.append(("saturation", str(float(saturation))))

        if start is None:

            body = [k + " " + v for k, v in changes]

            result = cls._create_block(
                content,
                ["blur"],
                body
            )

            cls._write_atomic(result)

            return

        lines = "\n".join(content.splitlines(False))

        for key, value in changes:

            updated = cls._update_value_in_block(
                lines,
                ["blur"],
                key,
                value
            )

            if updated is not None:
                lines = updated

        cls._write_atomic(lines)

    # ------------------------------------------------------- prefer-no-csd

    @classmethod
    def set_prefer_no_csd(
        cls,
        on
    ):

        content = cls._read()

        lines = content.splitlines(False)

        for i, raw in enumerate(lines):

            stripped = raw.strip()

            if stripped == "prefer-no-csd":

                if not on:
                    del lines[i]
                    cls._write_atomic("\n".join(lines))

                return

            if stripped.startswith("prefer-no-csd"):

                if not on:
                    del lines[i]
                    cls._write_atomic("\n".join(lines))
                else:
                    lines[i] = raw[:len(raw) - len(raw.lstrip())] + "prefer-no-csd"
                    cls._write_atomic("\n".join(lines))

                return

        if on:

            if content and not content.endswith("\n"):
                content += "\n"

            content += "prefer-no-csd\n"

            cls._write_atomic(content)

    # --------------------------------------------------------------- Getters

    @staticmethod
    def _extract_value(content, block_path, key):

        lines = content.splitlines(False)

        depth = 0
        stack = []

        target_depth = len(block_path)

        for i, raw in enumerate(lines):

            stripped = raw.strip()

            if not stripped or stripped.startswith("//"):
                continue

            if stripped.endswith("{"):

                name = stripped.rstrip("{").strip()
                name = name.split("=", 1)[0].strip().strip('"')
                stack.append(name)
                depth += 1

            elif stripped == "}" or stripped.startswith("}"):

                if stack:
                    stack.pop()
                    depth -= 1

            if depth == target_depth and stack == block_path:

                if (stripped.startswith(key + " ")
                        or stripped.startswith(key + "=")):

                    value = stripped[len(key):].strip().lstrip("=").strip()
                    return value.rstrip(";").strip()

        return None

    @classmethod
    def get_gaps(cls):

        content = cls._read()

        val = cls._extract_value(content, ["layout"], "gaps")

        if val is None:
            return 16

        try:
            return int(val)
        except ValueError:
            return 16

    @classmethod
    def get_border(cls):

        content = cls._read()

        start, end = cls._find_block(content, ["layout", "border"])

        if start is None:
            return {"on": False, "width": 0,
                    "active_color": "", "inactive_color": ""}

        lines = content.splitlines(False)

        result = {"on": True, "width": 0,
                  "active_color": "", "inactive_color": ""}

        for j in range(start + 1, end):

            stripped = lines[j].strip()

            if stripped.startswith("width"):
                try:
                    result["width"] = int(stripped.split()[1])
                except (IndexError, ValueError):
                    pass

            elif stripped.startswith("active-color"):
                m = re.search(r'"(.*?)"', stripped)
                if m:
                    result["active_color"] = m.group(1)

            elif stripped.startswith("inactive-color"):
                m = re.search(r'"(.*?)"', stripped)
                if m:
                    result["inactive_color"] = m.group(1)

        return result

    @classmethod
    def get_focus_ring(cls):

        content = cls._read()

        start, end = cls._find_block(content, ["layout", "focus-ring"])

        if start is None:
            return False

        lines = content.splitlines(False)

        for j in range(start + 1, end):

            stripped = lines[j].strip()

            if stripped == "off":
                return False
            if stripped == "on":
                return True

        return True

    @classmethod
    def get_blur(cls):

        content = cls._read()

        start, end = cls._find_block(content, ["blur"])

        if start is None:
            return {"passes": 0, "offset": 0.0,
                    "noise": 0.0, "saturation": 1.0}

        lines = content.splitlines(False)

        result = {"passes": 0, "offset": 0.0,
                  "noise": 0.0, "saturation": 1.0}

        for j in range(start + 1, end):

            stripped = lines[j].strip()

            parts = stripped.split()

            if len(parts) == 2:

                key, value = parts

                if key == "passes":
                    try:
                        result["passes"] = int(value)
                    except ValueError:
                        pass

                elif key in ("offset", "noise", "saturation"):
                    try:
                        result[key] = float(value)
                    except ValueError:
                        pass

        return result

    @classmethod
    def get_prefer_no_csd(cls):

        content = cls._read()

        lines = content.splitlines(False)

        for raw in lines:

            stripped = raw.strip()

            if stripped == "prefer-no-csd":
                return True

            if stripped.startswith("prefer-no-csd"):
                val = stripped.split(None, 1)

                if len(val) == 2 and val[1] in ("on", "true"):
                    return True

                if len(val) == 2 and val[1] in ("off", "false"):
                    return False

                return True

        return False

    @classmethod
    def get_cursor_size(cls):

        content = cls._read()

        val = cls._extract_value(content, ["cursor"], "xcursor-size")

        if val is None:
            return 24

        try:
            return int(val)
        except ValueError:
            return 24

    @classmethod
    def get_keyboard_layout(cls):

        content = cls._read()

        start, end = cls._find_block(content, ["input", "keyboard", "xkb"])

        if start is not None:

            lines = content.splitlines(False)

            for j in range(start + 1, end):

                stripped = lines[j].strip()

                if stripped.startswith("layout"):
                    return stripped.split(None, 1)[1].strip().strip('"')

        m = re.search(r'layout\s+"([^"]+)"', content)

        if m:
            return m.group(1)

        return "us"
