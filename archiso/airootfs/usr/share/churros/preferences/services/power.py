import subprocess


def _run(command):

    """

    Helper seguro: ejecuta un comando del sistema con timeout corto
    y captura de salida. Nunca lanza excepciones.

    Devuelve la salida estándar sin espacios al final,
    o una cadena vacía si el comando falla o no existe.
    """

    try:

        result = subprocess.run(

            command,

            capture_output=True,

            text=True,

            timeout=2

        )

        return result.stdout.strip()

    except Exception:

        return ""


class PowerService:

    @staticmethod
    def battery_present():

        """

        Devuelve True si hay una batería detectada en el sistema.
        Usa upower para enumerar dispositivos con categoría batería.
        """

        output = _run(["upower", "-e"])

        if not output:

            return False

        for line in output.splitlines():

            if line.strip().endswith("battery"):

                return True

        return False

    @staticmethod
    def battery_percentage():

        """

        Devuelve el porcentaje de carga de la batería como entero (0-100).
        Si no hay batería o upower falla, devuelve 100.
        """

        try:

            output = _run(["upower", "-i", "/org/freedesktop/UPower/devices/battery_BAT0"])

            if not output:

                output = _run(["upower", "-i", "/org/freedesktop/UPower/devices/battery_BAT1"])

            for line in output.splitlines():

                if "percentage" in line:

                    value = line.split(":", 1)[1].strip().rstrip("%")

                    return int(float(value))

        except Exception:

            pass

        return 100

    @staticmethod
    def battery_state():

        """

        Devuelve el estado actual de la batería:
        'Cargando', 'Descargando', 'Llena', 'Desconocido'.
        """

        try:

            output = _run(["upower", "-i", "/org/freedesktop/UPower/devices/battery_BAT0"])

            if not output:

                output = _run(["upower", "-i", "/org/freedesktop/UPower/devices/battery_BAT1"])

            for line in output.splitlines():

                if "state" in line:

                    return line.split(":", 1)[1].strip()

        except Exception:

            pass

        return "Desconocido"

    @staticmethod
    def power_profile():

        """

        Devuelve el perfil de energía activo:
        'performance', 'balanced', 'power-saver', 'Desconocido'.
        Usa powerprofilesctl si está disponible.
        """

        output = _run(["powerprofilesctl", "get"])

        if output in ("performance", "balanced", "power-saver"):

            return output

        return "balanced"

    @staticmethod
    def power_profiles_available():

        """

        Devuelve la lista de perfiles soportados por el sistema.
        """

        try:

            output = _run(["powerprofilesctl", "list"])

            profiles = []

            for line in output.splitlines():

                line = line.strip()

                if line in ("performance", "balanced", "power-saver"):

                    profiles.append(line)

            if profiles:

                return profiles

        except Exception:

            pass

        return ["balanced"]

    @staticmethod
    def screen_timeout():

        """

        Devuelve el tiempo de espera para apagar la pantalla, en segundos.
        Lee la configuración de GNOME / gsettings.
        Si no está disponible, devuelve 300 (5 minutos).
        """

        try:

            output = _run([

                "gsettings",

                "get",

                "org.gnome.desktop.session",

                "idle-delay"

            ])

            if output.startswith("uint32"):

                return int(output.replace("uint32", "").strip())

            if output.isdigit():

                return int(output)

        except Exception:

            pass

        return 300

    @staticmethod
    def sleep_timeout():

        """

        Devuelve el tiempo de espera para suspender, en segundos.
        Si no está disponible, devuelve 900 (15 minutos).
        """

        try:

            output = _run([

                "gsettings",

                "get",

                "org.gnome.settings-daemon.plugins.power",

                "sleep-inactive-ac-timeout"

            ])

            if output.startswith("uint32"):

                return int(output.replace("uint32", "").strip())

            if output.isdigit():

                return int(output)

        except Exception:

            pass

        return 900

    @staticmethod
    def lid_close_action():

        """

        Devuelve la acción al cerrar la tapa:
        'suspend', 'hibernate', 'nothing', 'Desconocido'.
        """

        try:

            output = _run([

                "gsettings",

                "get",

                "org.gnome.settings-daemon.plugins.power",

                "lid-close-ac-action"

            ])

            value = output.strip().strip("'\"")

            if value in ("suspend", "hibernate", "nothing", "blank", "logout", "shutdown"):

                return value

        except Exception:

            pass

        return "suspend"

    @staticmethod
    def power_saver_enabled():

        """

        Devuelve True si el modo ahorro de energía está activo.
        """

        return PowerService.power_profile() == "power-saver"

    @staticmethod
    def set_power_profile(profile):

        """Cambia el perfil activo via powerprofilesctl."""

        try:

            subprocess.run(
                ["powerprofilesctl", "set", profile],
                capture_output=True,
                timeout=2
            )

        except Exception:

            pass

    @staticmethod
    def set_screen_timeout(seconds):

        """Establece el tiempo de espera para apagar la pantalla."""

        try:

            subprocess.run(
                ["gsettings", "set", "org.gnome.desktop.session", "idle-delay", str(int(seconds))],
                capture_output=True,
                timeout=2
            )

        except Exception:

            pass

    @staticmethod
    def set_sleep_timeout(seconds):

        """Establece el tiempo de espera para suspender."""

        try:

            subprocess.run(
                ["gsettings", "set", "org.gnome.settings-daemon.plugins.power", "sleep-inactive-ac-timeout", str(int(seconds))],
                capture_output=True,
                timeout=2
            )

        except Exception:

            pass

    @staticmethod
    def set_lid_close_action(action):

        """Configura la accion al cerrar la tapa."""

        try:

            subprocess.run(
                ["gsettings", "set", "org.gnome.settings-daemon.plugins.power", "lid-close-ac-action", action],
                capture_output=True,
                timeout=2
            )

        except Exception:

            pass
