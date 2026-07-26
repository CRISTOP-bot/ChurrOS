import subprocess


def _has_wpctl():

    try:

        subprocess.run(

            ["wpctl", "status"],
            capture_output=True,
            timeout=2

        )

        return True

    except Exception:

        return False


class AudioService:

    @staticmethod
    def available():

        return _has_wpctl()

    @staticmethod
    def _get_default_volume(target="@DEFAULT_AUDIO_SINK@"):

        try:

            output = subprocess.check_output(

                ["wpctl", "get-volume", target],

                text=True,
                timeout=2

            ).strip()

            volume = float(output.split()[1])
            muted = "MUTED" in output

            return int(volume * 100), muted

        except Exception:

            return 0, False

    @staticmethod
    def get_volume():

        return AudioService._get_default_volume("@DEFAULT_AUDIO_SINK@")[0]

    @staticmethod
    def get_input_volume():

        vol, _ = AudioService._get_default_volume("@DEFAULT_AUDIO_SOURCE@")
        return vol

    @staticmethod
    def is_muted():

        _, muted = AudioService._get_default_volume("@DEFAULT_AUDIO_SINK@")
        return muted

    @staticmethod
    def is_input_muted():

        _, muted = AudioService._get_default_volume("@DEFAULT_AUDIO_SOURCE@")
        return muted

    @staticmethod
    def set_volume(value):

        try:

            subprocess.Popen(
                ["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", f"{int(value)}%"]
            )

        except Exception:
            pass

    @staticmethod
    def set_input_volume(value):

        try:

            subprocess.Popen(
                ["wpctl", "set-volume", "@DEFAULT_AUDIO_SOURCE@", f"{int(value)}%"]
            )

        except Exception:
            pass

    @staticmethod
    def set_mute(muted):

        cmd = ["wpctl", "set-mute", "@DEFAULT_AUDIO_SINK@", "1" if muted else "0"]
        try:
            subprocess.Popen(cmd)
        except Exception:
            pass

    @staticmethod
    def set_input_mute(muted):

        cmd = ["wpctl", "set-mute", "@DEFAULT_AUDIO_SOURCE@", "1" if muted else "0"]
        try:
            subprocess.Popen(cmd)
        except Exception:
            pass

    @staticmethod
    def list_sinks():

        return AudioService._list_devices("sink")

    @staticmethod
    def list_sources():

        return AudioService._list_devices("source")

    @staticmethod
    def set_default_sink(node_id):

        try:

            subprocess.Popen(
                ["wpctl", "set-default", str(node_id)]
            )

        except Exception:
            pass

    @staticmethod
    def _list_devices(kind):

        devices = []
        default_marker = "*"

        try:

            out = subprocess.check_output(
                ["wpctl", "status"],
                text=True,
                timeout=2
            )

            target_line = "Sinks:" if kind == "sink" else "Sources:"
            other_blocked = False
            in_section = False

            for line in out.splitlines():

                stripped = line.strip()

                if stripped == target_line:

                    in_section = True
                    continue

                if in_section:

                    if stripped.endswith(":") and target_line not in stripped:

                        break

                    if not stripped:

                        continue

                    if stripped.startswith("*"):

                        name = stripped[len(default_marker):].strip()
                        name = ". ".join(name.split(". ")[1:]) if ". " in name else name

                        parts = name.split(". ", 1)

                        if len(parts) == 2:
                            node_id, dev_name = parts
                        else:
                            node_id = "0"
                            dev_name = stripped

                        try:

                            devices.append({
                                "id": int(node_id),
                                "name": dev_name,
                                "default": True
                            })

                        except ValueError:
                            pass

                    else:

                        parts = stripped.split(". ", 1)

                        if len(parts) == 2:

                            try:

                                devices.append({
                                    "id": int(parts[0]),
                                    "name": parts[1],
                                    "default": False
                                })

                            except ValueError:
                                pass

        except Exception:
            pass

        return devices
