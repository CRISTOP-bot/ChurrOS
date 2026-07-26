import subprocess


def _unescape(s):

    return s.replace("\\:", ":")


class WifiService:

    @staticmethod
    def _run(command):

        try:

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=5
            )

            return (
                result.returncode,
                result.stdout.strip(),
                result.stderr.strip()
            )

        except Exception:

            return (1, "", "execution error")

    @staticmethod
    def available():

        code, out, _ = WifiService._run(
            [
                "nmcli",
                "-t",
                "-f",
                "DEVICE,TYPE",
                "device"
            ]
        )

        if code != 0:
            return False

        for line in out.splitlines():

            try:

                _, dev_type = line.split(":", 1)

                if dev_type == "wifi":
                    return True

            except ValueError:
                continue

        return False

    @staticmethod
    def enabled():

        code, out, _ = WifiService._run(
            [
                "nmcli",
                "radio",
                "wifi"
            ]
        )

        if code != 0:
            return False

        return out.lower() == "enabled"

    @staticmethod
    def scan():

        try:

            subprocess.Popen(
                ["nmcli", "device", "wifi", "rescan"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

        except Exception:
            pass

    @staticmethod
    def get():

        data = {

            "available": WifiService.available(),

            "enabled": WifiService.enabled(),

            "connected": None,

            "networks": []

        }

        if not data["available"]:

            return data

        if not data["enabled"]:

            return data

        code, out, _ = WifiService._run(
            [
                "nmcli",
                "--escape",
                "yes",
                "-t",
                "-f",
                "ACTIVE,SSID,SIGNAL,SECURITY",
                "device",
                "wifi",
                "list",
                "--rescan",
                "no"
            ]
        )

        if code != 0:

            return data

        saved = WifiService.saved_networks()

        for line in out.splitlines():

            if not line:

                continue

            fields = []
            current = ""
            escape = False

            for ch in line:

                if escape:

                    current += ch
                    escape = False

                elif ch == "\\":

                    escape = True

                elif ch == ":":

                    fields.append(current)
                    current = ""

                else:

                    current += ch

            fields.append(current)

            while len(fields) < 4:

                fields.append("")

            active, ssid, signal, security = fields[:4]

            ssid = _unescape(ssid)

            network = {

                "ssid": ssid if ssid else "Hidden Network",

                "signal": int(signal) if signal.lstrip("-").isdigit() else 0,

                "security": _unescape(security),

                "connected": active == "yes",

                "saved": ssid in saved

            }

            if network["connected"]:

                data["connected"] = network["ssid"]

            data["networks"].append(
                network
            )

        seen = set()

        deduped = []

        for n in data["networks"]:

            key = n["ssid"]

            if key in seen:

                continue

            seen.add(key)

            deduped.append(n)

        deduped.sort(

            key=lambda n: (

                not n["connected"],

                not n["saved"],

                -n["signal"]

            )

        )

        data["networks"] = deduped

        return data

    @staticmethod
    def saved_networks():

        code, out, _ = WifiService._run(
            [
                "nmcli",
                "-t",
                "-f",
                "NAME,TYPE",
                "connection",
                "show"
            ]
        )

        saved = set()

        if code != 0:

            return saved

        for line in out.splitlines():

            try:

                name, conn_type = line.split(":", 1)

                if conn_type == "802-11-wireless":

                    saved.add(name)

            except ValueError:

                pass

        return saved

    @staticmethod
    def connect(ssid, password=None):

        command = [

            "nmcli",

            "device",

            "wifi",

            "connect",

            ssid

        ]

        if password:

            command.extend(

                [

                    "password",

                    password

                ]

            )

        code, _, err = WifiService._run(
            command
        )

        if code == 0:

            return True, ""

        err = err.lower()

        if "secrets were required" in err:

            return False, "Password required."

        if "invalid" in err:

            return False, "Incorrect password."

        if "activation" in err:

            return False, "Unable to connect."

        return False, "Unknown error."

    @staticmethod
    def connect_hidden(ssid, password=None):

        try:

            code, _, err = WifiService._run(
                [
                    "nmcli",
                    "connection",
                    "add",
                    "type",
                    "wifi",
                    "ifname",
                    "wlan0",
                    "con-name",
                    ssid,
                    "ssid",
                    ssid,
                    "hidden",
                    "yes"
                ]
            )

            if code != 0:

                return False, "Failed to create hidden profile."

        except Exception:
            return False, "Unknown error."

        cmd = [
            "nmcli",
            "connection",
            "up",
            ssid
        ]

        if password:

            cmd.extend(
                [
                    "password",
                    password
                ]
            )

        code, _, err = WifiService._run(cmd)

        if code == 0:

            return True, ""

        err = err.lower()

        if "secrets were required" in err:

            return False, "Password required."

        if "invalid" in err:

            return False, "Incorrect password."

        if "activation" in err:

            return False, "Unable to connect."

        return False, "Unknown error."

    @staticmethod
    def disconnect():

        code, out, _ = WifiService._run(

            [

                "nmcli",

                "-t",

                "-f",

                "DEVICE,TYPE",

                "device"

            ]

        )

        if code != 0:

            return

        for line in out.splitlines():

            try:

                device, dev_type = line.split(":", 1)

                if dev_type == "wifi":

                    WifiService._run(

                        [

                            "nmcli",

                            "device",

                            "disconnect",

                            device

                        ]

                    )

                    break

            except ValueError:
                pass

    @staticmethod
    def forget(ssid):

        WifiService._run(

            [

                "nmcli",

                "connection",

                "delete",

                ssid

            ]

        )

    @staticmethod
    def enable():

        WifiService._run(

            [

                "nmcli",

                "radio",

                "wifi",

                "on"

            ]

        )

    @staticmethod
    def disable():

        WifiService._run(

            [

                "nmcli",

                "radio",

                "wifi",

                "off"

            ]

        )

    @staticmethod
    def toggle():

        if WifiService.enabled():

            WifiService.disable()

        else:

            WifiService.enable()
