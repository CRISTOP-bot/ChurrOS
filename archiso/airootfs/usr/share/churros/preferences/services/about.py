import os
import platform


class AboutService:

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
    def kernel():

        return platform.release()

    @staticmethod
    def base():

        return "Arch Linux"

    @staticmethod
    def session():

        return os.environ.get(
            "XDG_CURRENT_DESKTOP",
            "Desconocida"
        )

    @staticmethod
    def developer():

        return "Equipo ChurrOS"

    @staticmethod
    def license():

        return "GPL-3.0"