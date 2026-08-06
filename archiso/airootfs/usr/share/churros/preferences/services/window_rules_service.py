import os
import re
import tempfile


class WindowRulesService:

    PATH = os.path.join(
        os.path.expanduser("~"),
        ".config",
        "niri",
        "config.kdl"
    )

    INDENT = "    "

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
            prefix="niri-wr-",
            suffix=".kdl",
            dir=directory
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
    def _find_all_blocks(cls, content, name):

        """Encuentra cada bloque top-level llamado 'name'.

        Devuelve lista de (start_idx, end_idx) sobre splitlines(False).
        """

        lines = content.splitlines(False)

        stack = []
        blocks = []

        for i, raw in enumerate(lines):

            stripped = raw.strip()

            if not stripped or stripped.startswith("//"):
                continue

            if stripped.endswith("{"):

                head = stripped.rstrip("{").strip()
                head_name = head.split("=", 1)[0].strip().strip('"')

                stack.append((i, head_name, len(stack)))

                if len(stack) == 1 and head_name == name:
                    pass

            elif stripped == "}" or stripped.startswith("}"):

                if stack:

                    start_idx, head_name, depth = stack.pop()

                    if depth == 0 and head_name == name:

                        blocks.append((start_idx, i))

        return blocks, lines

    @classmethod
    def list_rules(cls):

        content = cls._read()

        blocks, lines = cls._find_all_blocks(content, "window-rule")

        rules = []

        for idx, (start, end) in enumerate(blocks):

            rule = {
                "index": idx,
                "app_id": "",
                "title": "",
                "opacity": None,
                "open_floating": None,
                "corner_radius": None,
                "clip_to_geometry": None,
                "blur": None,
            }

            for j in range(start + 1, end):

                stripped = lines[j].strip()

                if stripped.startswith("match "):

                    m = re.match(
                        r'match\s+app-id\s*=\s*"([^"]*)"',
                        stripped
                    )

                    if m:
                        rule["app_id"] = m.group(1)
                        continue

                    m = re.match(
                        r'match\s+title\s*=\s*"([^"]*)"',
                        stripped
                    )

                    if m:
                        rule["title"] = m.group(1)
                        continue

                if stripped.startswith("opacity"):
                    try:
                        value = stripped.split(None, 1)[1].strip()
                        rule["opacity"] = float(value)
                    except (IndexError, ValueError):
                        pass

                elif stripped.startswith("open-floating"):
                    try:
                        value = stripped.split(None, 1)[1].strip()
                        rule["open_floating"] = value == "true"
                    except IndexError:
                        pass

                elif stripped.startswith("geometry-corner-radius"):
                    try:
                        value = stripped.split(None, 1)[1].strip()
                        rule["corner_radius"] = float(value)
                    except (IndexError, ValueError):
                        pass

                elif stripped.startswith("clip-to-geometry"):
                    try:
                        value = stripped.split(None, 1)[1].strip()
                        rule["clip_to_geometry"] = value == "true"
                    except IndexError:
                        pass

                elif stripped == "background-effect {" or \
                        stripped.startswith("background-effect"):

                    inner_end = None

                    for k in range(j + 1, end):
                        if lines[k].strip() == "}" or \
                                lines[k].strip().startswith("}"):
                            inner_end = k
                            break

                    if inner_end is not None:
                        for k in range(j + 1, inner_end):
                            s = lines[k].strip()
                            if s.startswith("blur"):
                                parts = s.split()
                                if len(parts) == 2:
                                    rule["blur"] = parts[1] == "true"

            rules.append(rule)

        return rules

    @classmethod
    def _serialize_rule(cls, rule):

        lines = ["window-rule {"]

        if rule.get("app_id"):
            lines.append(
                cls.INDENT + 'match app-id="' + rule["app_id"] + '"'
            )

        if rule.get("title"):
            lines.append(
                cls.INDENT + 'match title="' + rule["title"] + '"'
            )

        if rule.get("opacity") is not None:
            lines.append(
                cls.INDENT + "opacity " + str(rule["opacity"])
            )

        if rule.get("open_floating") is not None:
            lines.append(
                cls.INDENT + "open-floating " +
                ("true" if rule["open_floating"] else "false")
            )

        if rule.get("corner_radius") is not None:
            lines.append(
                cls.INDENT + "geometry-corner-radius " +
                str(rule["corner_radius"])
            )

        if rule.get("clip_to_geometry") is not None:
            lines.append(
                cls.INDENT + "clip-to-geometry " +
                ("true" if rule["clip_to_geometry"] else "false")
            )

        if rule.get("blur") is not None:
            lines.append(cls.INDENT + "background-effect {")
            lines.append(
                cls.INDENT + cls.INDENT + "blur " +
                ("true" if rule["blur"] else "false")
            )
            lines.append(cls.INDENT + "}")

        lines.append("}")

        return "\n".join(lines) + "\n"

    @classmethod
    def add_rule(cls, app_id="", title="", opacity=None,
                 open_floating=None, corner_radius=None,
                 clip_to_geometry=None, blur=None):

        rule = {
            "app_id": app_id,
            "title": title,
            "opacity": opacity,
            "open_floating": open_floating,
            "corner_radius": corner_radius,
            "clip_to_geometry": clip_to_geometry,
            "blur": blur,
        }

        rule_str = cls._serialize_rule(rule)

        content = cls._read()

        if content and not content.endswith("\n"):
            content += "\n"

        content += "\n// Window rule (custom)\n" + rule_str

        cls._write_atomic(content)

        lines = content.splitlines(False)

        blocks, _ = cls._find_all_blocks(content, "window-rule")

        return len(blocks) - 1

    @classmethod
    def update_rule(cls, index, **kwargs):

        rules_serialized = cls.list_rules()

        if index < 0 or index >= len(rules_serialized):
            raise IndexError("window-rule index out of range: " + str(index))

        rules_serialized[index].update(kwargs)

        cls._rewrite_all(rules_serialized)

    @classmethod
    def delete_rule(cls, index):

        rules = cls.list_rules()

        if index < 0 or index >= len(rules):
            raise IndexError("window-rule index out of range: " + str(index))

        del rules[index]

        cls._rewrite_all(rules)

    @classmethod
    def _rewrite_all(cls, rules):

        content = cls._read()

        blocks, lines = cls._find_all_blocks(content, "window-rule")

        if not blocks:
            return

        first_start = blocks[0][0]
        last_end = blocks[-1][1]

        prefix = "\n".join(lines[:first_start])

        if prefix:

            prefix = re.sub(
                r"//+\s*Window rules\s*\n+\s*\Z",
                "",
                prefix.rstrip() + "\n"
            )

        if not prefix:
            prefix = ""

        suffix = "\n".join(lines[last_end + 1:])

        body = ""

        for r in rules:

            body += cls._serialize_rule(r)

        new_content = prefix + "\n// Window rules\n" + body + suffix

        cls._write_atomic(new_content)
