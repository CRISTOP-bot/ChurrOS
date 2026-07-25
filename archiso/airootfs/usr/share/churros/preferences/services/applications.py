import subprocess


class ApplicationsService:

    @staticmethod
    def count():

        try:

            result = subprocess.run(

                ["pacman", "-Q"],

                capture_output=True,

                text=True,

                timeout=2

            )

            return str(
                len(
                    result.stdout.splitlines()
                )
            )

        except Exception:

            return "0"

    @staticmethod
    def store():

        return "Pacman"

    @staticmethod
    def auto_updates():

        #
        # Más adelante leeremos
        # la configuración de ChurrOS Update.
        #

        return True

    @staticmethod
    def auto_install():

        #
        # Todavía no implementado.
        #

        return False

    @staticmethod
    def package_manager():

        return "pacman"

    @staticmethod
    def repositories():

        return "Arch Linux"

    @staticmethod
    def flatpak_enabled():

        try:

            result = subprocess.run(

                ["which", "flatpak"],

                capture_output=True,

                text=True,

                timeout=2

            )

            return result.returncode == 0

        except Exception:

            return False

    @staticmethod
    def snap_enabled():

        try:

            result = subprocess.run(

                ["which", "snap"],

                capture_output=True,

                text=True,

                timeout=2

            )

            return result.returncode == 0

        except Exception:

            return False