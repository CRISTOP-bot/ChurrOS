import os
import re
import shutil

HOME = os.path.expanduser("~")
NIRI_CONFIG_PATH = os.path.join(HOME, ".config", "niri", "config.kdl")
NIRI_CONFIG_BACKUP = os.path.join(HOME, ".config", "niri", "config.kdl.bak")


def _parse_action(raw_action):
    action = raw_action.strip().rstrip(";")

    m = re.match(r'^spawn\s+"([^"]+)"\s+"([^"]+)"', action)
    if m:
        return "spawn", m.group(1), m.group(2)

    m = re.match(r'^spawn\s+"([^"]+)"', action)
    if m:
        return "spawn", m.group(1), ""

    m = re.match(r'^spawn-sh\s+"([^"]*)"', action)
    if m:
        return "spawn-sh", m.group(1), ""

    parts = action.split()
    func = parts[0]
    args = " ".join(parts[1:])
    return "builtin", func, args


def _make_action_line(bind_type, command, args):
    if bind_type == "spawn":
        if args:
            return 'spawn "{}" "{}"'.format(command, args)
        return 'spawn "{}"'.format(command)
    if bind_type == "spawn-sh":
        return 'spawn-sh "{}"'.format(command)
    if args:
        return "{} {}".format(command, args)
    return command


class KeyboardService:

    @classmethod
    def get_keybinds(cls):
        if not os.path.exists(NIRI_CONFIG_PATH):
            return []

        binds = []
        try:
            with open(NIRI_CONFIG_PATH) as f:
                lines = f.readlines()
        except Exception:
            return []

        in_binds = False
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("binds"):
                in_binds = True
                continue
            if in_binds and stripped == "}":
                break

            if not in_binds:
                continue

            m = re.match(
                r"^\s*(Mod\S*|Print|Ctrl\+Print|Alt\+Print|XF86\S*)"
                r"(\s+allow-when-locked=\S+)?\s*\{\s*(.*?)\s*\}",
                stripped
            )
            if not m:
                continue

            key = m.group(1).strip()
            locked = m.group(2) is not None
            raw_action = m.group(3).strip().rstrip(";")

            bind_type, command, args = _parse_action(raw_action)

            binds.append({
                "key": key,
                "allow_when_locked": locked,
                "type": bind_type,
                "command": command,
                "args": args,
            })

        return binds

    @classmethod
    def set_keybind(cls, key, action_type, command, args):
        if not os.path.exists(NIRI_CONFIG_PATH):
            return False

        try:
            shutil.copyfile(NIRI_CONFIG_PATH, NIRI_CONFIG_BACKUP)
        except Exception:
            pass

        new_action = _make_action_line(action_type, command, args)
        new_line = "    {} {{ {}; }}".format(key, new_action)

        try:
            with open(NIRI_CONFIG_PATH) as f:
                lines = f.readlines()
        except Exception:
            return False

        in_binds = False
        out_lines = []
        replaced = False

        for line in lines:
            stripped = line.strip()
            if stripped.startswith("binds"):
                in_binds = True
                out_lines.append(line)
                continue
            if in_binds and stripped == "}":
                out_lines.append(line)
                in_binds = False
                continue

            if in_binds:
                m = re.match(r"^\s*" + re.escape(key) + r"(\s|$|\s*{|\s*\()", stripped)
                if m and not replaced:
                    indent = line[:len(line) - len(line.lstrip())]
                    out_lines.append(indent + new_action + "\n")
                    replaced = True
                    continue

            out_lines.append(line)

        if not replaced:
            return False

        try:
            with open(NIRI_CONFIG_PATH, "w") as f:
                f.writelines(out_lines)
            return True
        except Exception:
            return False

    @classmethod
    def add_keybind(cls, key, action_type, command, args):
        if not os.path.exists(NIRI_CONFIG_PATH):
            return False

        try:
            shutil.copyfile(NIRI_CONFIG_PATH, NIRI_CONFIG_BACKUP)
        except Exception:
            pass

        new_line = "    {} {{ {}; }}\n".format(
            key,
            _make_action_line(action_type, command, args)
        )

        try:
            with open(NIRI_CONFIG_PATH) as f:
                lines = f.readlines()
        except Exception:
            return False

        in_binds = False
        out_lines = []

        for line in lines:
            out_lines.append(line)

            stripped = line.strip()
            if stripped.startswith("binds"):
                in_binds = True
                continue

            if in_binds and stripped == "}":
                break

        insert_pos = len(out_lines) - 1
        out_lines.insert(insert_pos, new_line)

        try:
            with open(NIRI_CONFIG_PATH, "w") as f:
                f.writelines(out_lines)
            return True
        except Exception:
            return False

    @classmethod
    def restore_backup(cls):
        if os.path.exists(NIRI_CONFIG_BACKUP):
            try:
                shutil.copyfile(NIRI_CONFIG_BACKUP, NIRI_CONFIG_PATH)
                return True
            except Exception:
                pass
        return False