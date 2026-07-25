import os
import pwd
import getpass


class UsersService:

    @staticmethod
    def username():

        try:

            return getpass.getuser()

        except Exception:

            return "Desconocido"

    @staticmethod
    def full_name():

        try:

            return pwd.getpwuid(
                os.getuid()
            ).pw_gecos.split(",")[0]

        except Exception:

            return UsersService.username()

    @staticmethod
    def home():

        try:

            return os.path.expanduser("~")

        except Exception:

            return ""

    @staticmethod
    def shell():

        try:

            return pwd.getpwuid(
                os.getuid()
            ).pw_shell

        except Exception:

            return "Desconocido"

    @staticmethod
    def uid():

        try:

            return str(
                os.getuid()
            )

        except Exception:

            return "0"

    @staticmethod
    def gid():

        try:

            return str(
                os.getgid()
            )

        except Exception:

            return "0"

    @staticmethod
    def hostname():

        try:

            return os.uname().nodename

        except Exception:

            return "Desconocido"

    @staticmethod
    def auto_login():

        #
        # Más adelante leeremos la configuración
        # de GDM/SDDM/LightDM.
        #

        return False