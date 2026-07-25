import os
import platform
import socket
import subprocess


class SystemService:

    @staticmethod
    def distro():

        return "ChurrOS"

    @staticmethod
    def version():

        return "Beta"

    @staticmethod
    def edition():

        return "Developer Preview"

    @staticmethod
    def session():

        return os.environ.get(
            "XDG_CURRENT_DESKTOP",
            "Desconocida"
        )

    @staticmethod
    def hostname():

        try:

            return socket.gethostname()

        except Exception:

            return "Desconocido"

    @staticmethod
    def username():

        try:

            return os.environ.get(
                "USER",
                "Desconocido"
            )

        except Exception:

            return "Desconocido"

    @staticmethod
    def kernel():

        try:

            return platform.release()

        except Exception:

            return "Desconocido"

    @staticmethod
    def package_manager():

        return "Pacman"

    @staticmethod
    def base():

        return "Arch Linux"

    @staticmethod
    def cpu():

        try:

            with open("/proc/cpuinfo") as file:

                for line in file:

                    if line.startswith("model name"):

                        return line.split(":", 1)[1].strip()

        except Exception:

            pass

        return "Desconocido"

    @staticmethod
    def memory():

        try:

            with open("/proc/meminfo") as file:

                for line in file:

                    if line.startswith("MemTotal"):

                        kb = int(
                            line.split()[1]
                        )

                        gb = kb / 1024 / 1024

                        return f"{gb:.1f} GB"

        except Exception:

            pass

        return "Desconocida"

    @staticmethod
    def gpu():

        try:

            result = subprocess.run(

                ["lspci"],

                capture_output=True,

                text=True,

                timeout=2

            )

            for line in result.stdout.splitlines():

                if "VGA" in line or "3D" in line:

                    return line.split(": ", 1)[1]

        except Exception:

            pass

        return "Desconocida"