import shutil
import subprocess


class NetworkManagerBackend:

    TIMEOUT = 2

    @classmethod
    def _run(cls, command):

        try:

            return subprocess.check_output(
                command,
                text=True,
                stderr=subprocess.DEVNULL,
                timeout=cls.TIMEOUT
            ).strip()

        except Exception:

            return None

    @classmethod
    def available(cls):

        return shutil.which("nmcli") is not None

    @classmethod
    def running(cls):

        if not cls.available():

            return False

        output = cls._run(

            [
                "systemctl",
                "is-active",
                "NetworkManager"
            ]

        )

        return output == "active"

    @classmethod
    def wifi_available(cls):

        if not cls.running():

            return False

        output = cls._run(

            [
                "nmcli",
                "-t",
                "-f",
                "TYPE",
                "device"
            ]

        )

        if output is None:

            return False

        return "wifi" in output.splitlines()

    @classmethod
    def wifi_enabled(cls):

        if not cls.wifi_available():

            return False

        output = cls._run(

            [
                "nmcli",
                "radio",
                "wifi"
            ]

        )

        if output is None:

            return False

        return output.lower() == "enabled"

    @classmethod
    def set_wifi(
        cls,
        enabled
    ):

        subprocess.run(

            [
                "nmcli",
                "radio",
                "wifi",
                "on" if enabled else "off"
            ],

            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=cls.TIMEOUT

        )

    @classmethod
    def current_network(cls):

        if not cls.wifi_available():

            return None

        output = cls._run(

            [
                "nmcli",
                "-t",
                "-f",
                "ACTIVE,SSID",
                "device",
                "wifi"
            ]

        )

        if output is None:

            return None

        for line in output.splitlines():

            parts = line.split(":", 1)

            if len(parts) != 2:

                continue

            active, ssid = parts

            if active == "yes":

                return ssid

        return None

    @classmethod
    def networks(cls):

        if not cls.wifi_available():

            return []

        output = cls._run(

            [
                "nmcli",
                "-t",
                "-f",
                "SSID,SIGNAL",
                "device",
                "wifi",
                "list"
            ]

        )

        if output is None:

            return []

        result = []

        for line in output.splitlines():

            if ":" not in line:

                continue

            ssid, signal = line.split(":", 1)

            if not ssid:

                continue

            try:

                signal = int(signal)

            except Exception:

                signal = 0

            result.append(

                {

                    "ssid": ssid,

                    "signal": signal

                }

            )

        return result