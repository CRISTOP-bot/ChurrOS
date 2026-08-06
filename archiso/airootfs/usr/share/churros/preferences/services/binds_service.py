import os
import re
import tempfile


class BindsService:

    PATH = os.path.join(
        os.path.expanduser("~"),
        ".config",
        "niri",
        "config.kdl"
    )

    SIMPLE_ACTIONS = (
        "close-window",
        "quit",
        "maximize-column",
        "fullscreen-window",
        "show-hotkey-overlay",
        "toggle-overview",
        "switch-preset-column-width",
        "toggle-window-floating",
        "switch-focus-between-floating-and-tiling",
        "screenshot",
        "screenshot-screen",
        "screenshot-window",
        "focus-column-left",
        "focus-column-right",
        "focus-window-up",
        "focus-window-down",
        "move-column-left",
        "move-column-right",
        "move-window-up",
        "move-window-down",
    )

    NUMERIC_ACTIONS = (
        "focus-workspace",
        "move-window-to-workspace",
    )

    @classmethod
    def _read(cls):

        try:
            with open(cls.PATH, "r") as f:
                return f.read()
        except Exception:
            return ""

    @classmethod
    def _write_atomic(cls, content):

        directory = os.path.dirname(cls.PATH)
        os.makedirs(directory, exist_ok=True)

        fd, tmp = tempfile.mkstemp(
            prefix="niri-binds-", suffix=".kdl", dir=directory
        )

        try:

            with os.fdopen(fd, "w") as f:
                f.write(content)

            os.replace(tmp, cls.PATH)

        except Exception:

            try:
                os.unlink(tmp)
            except OSError:
                pass

            raise

    @classmethod
    def _find_binds_block(cls, content):

        """Devuelve (start_idx, end_idx, lines) del bloque 'binds {'.

        Indices sobre splitlines(False). Si no existe, end es None.
        """

        lines = content.splitlines(False)

        stack = []

        for i, raw in enumerate(lines):

            stripped = raw.strip()

            if not stripped or stripped.startswith("//"):
                continue

            if stripped.endswith("{"):

                head = stripped.rstrip("{").strip()
                head_name = head.split("=", 1)[0].strip().strip('"')

                stack.append((i, head_name, len(stack)))

            elif stripped == "}" or stripped.startswith("}"):

                if stack:

                    start_idx, head_name, depth = stack.pop()

                    if depth == 0 and head_name == "binds":
                        return start_idx, i, lines

        return None, None, lines

    @classmethod
    def list_binds(cls):

        content = cls._read()

        start, end, lines = cls._find_binds_block(content)

        if start is None:
            return []

        binds = []

        for j in range(start + 1, end):

            stripped = lines[j].strip()

            if not stripped or stripped.startswith("//"):
                continue

            bind = cls._parse_bind_line(stripped)

            if bind is not None:

                bind["line_index"] = j
                binds.append(bind)

        return binds

    @classmethod
    def _parse_bind_line(cls, line):

        """Parsea una linea de bind del estilo:

            Mod+Return { spawn "foot"; }
            Mod+Q { close-window; }
            XF86AudioMute allow-when-locked=true { spawn-sh "wpctl..."; }
            Mod+1 { focus-workspace 1; }
        """

        m = re.match(
            r'^([^{]+?)(?:\s+(allow-when-\w+=\w+))?\s*\{(.+)\}$',
            line
        )

        if not m:
            return None

        keys = m.group(1).strip()
        modifier = m.group(2)
        body = m.group(3).strip().rstrip(";").strip()

        bind = {
            "keys": keys,
            "modifier": modifier or "",
            "raw_body": body,
            "action": "",
            "argument": "",
        }

        tokens = body.split(None, 1)

        bind["action"] = tokens[0].strip()

        if len(tokens) > 1:
            bind["argument"] = tokens[1].strip()

        return bind

    @classmethod
    def _serialize_bind(cls, bind):

        keys = bind.get("keys", "").strip()

        if not keys:
            return None

        action = (bind.get("action") or "").strip()

        if not action:
            return None

        prefix = keys

        mod = (bind.get("modifier") or "").strip()

        if mod:
            prefix += " " + mod

        arg = (bind.get("argument") or "").strip()

        if arg:
            body = action + " " + arg + ";"
        else:
            body = action + ";"

        return prefix + " { " + body + " }"

    @classmethod
    def add_bind(cls, keys, action, argument="", modifier=""):

        bind = {
            "keys": keys,
            "modifier": modifier,
            "action": action,
            "argument": argument,
            "raw_body": "",
        }

        line = cls._serialize_bind(bind)

        if line is None:
            raise ValueError("Bind invalido")

        content = cls._read()

        start, end, lines = cls._find_binds_block(content)

        if start is None:

            if content and not content.endswith("\n"):
                content += "\n"

            content += "\nbinds {\n    " + line + "\n}\n"

            cls._write_atomic(content)
            return

        indent = "    "

        insert_idx = end

        lines.insert(insert_idx, indent + line)

        cls._write_atomic("\n".join(lines))

    @classmethod
    def delete_bind(cls, keys):

        content = cls._read()

        start, end, lines = cls._find_binds_block(content)

        if start is None:
            return False

        target_keys = keys.strip()

        for j in range(start + 1, end):

            stripped = lines[j].strip()

            if not stripped or stripped.startswith("//"):
                continue

            bind = cls._parse_bind_line(stripped)

            if bind and bind["keys"] == target_keys:

                del lines[j]
                cls._write_atomic("\n".join(lines))
                return True

        return False
