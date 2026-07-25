import shutil
import subprocess


class BluetoothBackend:

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

        return shutil.which("bluetoothctl") is not None

    @classmethod
    def running(cls):

        if not cls.available():

            return False

        output = cls._run(

            [
                "systemctl",
                "is-active",
                "bluetooth"
            ]

        )

        return output == "active"

    @classmethod
    def adapter_available(cls):

        if not cls.running():

            return False

        output = cls._run(

            [
                "bluetoothctl",
                "list"
            ]

        )

        if output is None:

            return False

        return bool(output)

    @classmethod
    def enabled(cls):

        if not cls.adapter_available():

            return False

        output = cls._run(

            [
                "bluetoothctl",
                "show"
            ]

        )

        if output is None:

            return False

        for line in output.splitlines():

            line = line.strip()

            if line.startswith("Powered:"):

                return line.split(":")[1].strip().lower() == "yes"

        return False

    @classmethod
    def set_enabled(
        cls,
        enabled
    ):

        if not cls.adapter_available():

            return

        subprocess.run(

            [
                "bluetoothctl",
                "power",
                "on" if enabled else "off"
            ],

            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=cls.TIMEOUT

        )

    @classmethod
    def devices(cls):

        if not cls.adapter_available():

            return []

        output = cls._run(

            [
                "bluetoothctl",
                "devices"
            ]

        )

        if output is None:

            return []

        devices = []

        for line in output.splitlines():

            if not line.startswith("Device"):

                continue

            parts = line.split(maxsplit=2)

            if len(parts) < 3:

                continue

            devices.append(

                {

                    "mac": parts[1],

                    "name": parts[2]

                }

            )

        return devices