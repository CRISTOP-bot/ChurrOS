import os


class PrivacyService:

    @staticmethod
    def location():

        #
        # Más adelante leeremos la configuración
        # del servicio de ubicación.
        #

        return False

    @staticmethod
    def camera():

        #
        # Más adelante integraremos PipeWire
        # y xdg-desktop-portal.
        #

        return True

    @staticmethod
    def microphone():

        #
        # Más adelante integraremos PipeWire.
        #

        return True

    @staticmethod
    def telemetry():

        #
        # ChurrOS no enviará telemetría
        # por defecto.
        #

        return False

    @staticmethod
    def firewall():

        try:

            return os.system(
                "systemctl is-active --quiet ufw"
            ) == 0

        except Exception:

            return False

    @staticmethod
    def screen_lock():

        #
        # Más adelante leeremos
        # la configuración de Noctalia.
        #

        return True

    @staticmethod
    def history():

        #
        # Historial de archivos recientes.
        #

        return True

    @staticmethod
    def crash_reports():

        #
        # En futuras versiones podremos
        # activar el envío de reportes.
        #

        return False