import subprocess
import shutil


def _has_bluetoothctl():

    return shutil.which("bluetoothctl") is not None


def _has_rfkill():

    return shutil.which("rfkill") is not None


class BluetoothService:

    @staticmethod
    def available():

        if not _has_bluetoothctl():

            try:

                import os
                return os.path.isdir("/sys/class/bluetooth")

            except Exception:
                return False

        try:

            out = subprocess.run(
                ["bluetoothctl", "show"],
                capture_output=True, text=True, timeout=2
            ).stdout

            return "No default controller" not in out

        except Exception:

            return False

    @staticmethod
    def is_enabled():

        if not _has_bluetoothctl():
            return False

        try:

            out = subprocess.run(
                ["bluetoothctl", "show"],
                capture_output=True, text=True, timeout=2
            ).stdout

            for line in out.splitlines():

                if "Powered:" in line:
                    return "yes" in line.split(":", 1)[1].strip().lower()

            return False

        except Exception:

            return False

    @staticmethod
    def is_blocked():

        if not _has_rfkill() or not _has_bluetoothctl():
            return False

        try:

            out = subprocess.run(
                ["rfkill", "list", "bluetooth"],
                capture_output=True, text=True, timeout=2
            ).stdout

            return "Soft blocked: yes" in out or "Hard blocked: yes" in out

        except Exception:

            return False

    @staticmethod
    def enable():

        if not _has_bluetoothctl():
            return False

        try:

            subprocess.run(
                ["bluetoothctl", "power", "on"],
                capture_output=True, timeout=3
            )
            return True

        except Exception:
            return False

    @staticmethod
    def disable():

        if not _has_bluetoothctl():
            return False

        try:

            subprocess.run(
                ["bluetoothctl", "power", "off"],
                capture_output=True, timeout=3
            )
            return True

        except Exception:
            return False

    @staticmethod
    def scan_start():

        if not _has_bluetoothctl():
            return

        try:

            subprocess.Popen(
                ["bluetoothctl", "--timeout", "10", "scan", "on"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

        except Exception:
            pass

    @staticmethod
    def scan_stop():

        if not _has_bluetoothctl():
            return

        try:

            subprocess.Popen(
                ["bluetoothctl", "scan", "off"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

        except Exception:
            pass

    @staticmethod
    def list_devices():

        if not _has_bluetoothctl():
            return []

        try:

            out = subprocess.run(
                ["bluetoothctl", "devices"],
                capture_output=True, text=True, timeout=3
            ).stdout

            devices = []

            for line in out.splitlines():

                line = line.strip()

                if line.startswith("Device "):

                    parts = line.split(maxsplit=2)

                    if len(parts) == 3:

                        addr = parts[1]
                        name = parts[2]
                        connected = BluetoothService._is_connected(
                            addr
                        )

                        devices.append({
                            "address": addr,
                            "name": name,
                            "connected": connected
                        })

            return devices

        except Exception:
            return []

    @staticmethod
    def _is_connected(address):

        try:

            out = subprocess.run(
                ["bluetoothctl", "info", address],
                capture_output=True, text=True, timeout=2
            ).stdout

            for line in out.splitlines():

                if "Connected:" in line:
                    return "yes" in line.split(":", 1)[1].strip().lower()

            return False

        except Exception:
            return False

    @staticmethod
    def connect(address):

        if not _has_bluetoothctl():
            return False

        try:

            subprocess.run(
                ["bluetoothctl", "connect", address],
                capture_output=True, timeout=10
            )
            return True

        except Exception:
            return False

    @staticmethod
    def disconnect(address):

        if not _has_bluetoothctl():
            return False

        try:

            subprocess.run(
                ["bluetoothctl", "disconnect", address],
                capture_output=True, timeout=5
            )
            return True

        except Exception:
            return False

    @staticmethod
    def pair(address):

        if not _has_bluetoothctl():
            return False

        try:

            subprocess.run(
                ["bluetoothctl", "pair", address],
                capture_output=True, timeout=15
            )
            return True

        except Exception:
            return False

    @staticmethod
    def remove(address):

        if not _has_bluetoothctl():
            return False

        try:

            subprocess.run(
                ["bluetoothctl", "remove", address],
                capture_output=True, timeout=3
            )
            return True

        except Exception:
            return False
