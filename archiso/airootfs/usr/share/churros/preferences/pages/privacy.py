from widgets.page import Page
from widgets.group import Group
from widgets.switch_row import SwitchRow

from services.privacy import PrivacyService


class PrivacyPage(Page):

    def __init__(self, navigator):

        super().__init__(
            navigator,
            "Privacidad",
            "Configuración de privacidad y seguridad"
        )

        #
        # Permisos
        #

        permissions = Group(
            "Permisos"
        )
        permissions.add(

            SwitchRow(

                title="Servicios de ubicación",

                subtitle="Permitir que las aplicaciones accedan a la ubicación",

                icon="privacy.svg",

                active=PrivacyService.location(),

                callback=PrivacyService.set_location

            )

        )

        permissions.add(

            SwitchRow(

                title="Acceso a la cámara",

                subtitle="Permitir el uso de la cámara",

                icon="privacy.svg",

                active=PrivacyService.camera(),

                callback=PrivacyService.set_camera

            )

        )

        permissions.add(

            SwitchRow(

                title="Acceso al micrófono",

                subtitle="Permitir el uso del micrófono",

                icon="privacy.svg",

                active=PrivacyService.microphone(),

                callback=PrivacyService.set_microphone

            )

        )

        self.add(

            permissions

        )

        #
        # Firewall
        #

        firewall = Group(

            "Firewall"

        )

        firewall.add(

            SwitchRow(

                title="Firewall (ufw)",

                subtitle="Activar el firewall del sistema",

                icon="privacy.svg",

                active=PrivacyService.firewall(),

                callback=PrivacyService.set_firewall

            )

        )

        self.add(

            firewall

        )
        #
        # Diagnóstico
        #

        diagnostics = Group(
            "Diagnóstico"
        )

        diagnostics.add(

            SwitchRow(

                title="Enviar estadísticas",

                subtitle="Compartir información anónima para mejorar ChurrOS",

                icon="privacy.svg",

                active=PrivacyService.telemetry(),

                callback=PrivacyService.set_telemetry

            )

        )

        self.add(
            diagnostics
        )