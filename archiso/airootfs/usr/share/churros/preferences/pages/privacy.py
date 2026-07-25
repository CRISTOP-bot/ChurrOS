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

                active=PrivacyService.location()

            )

        )

        permissions.add(

            SwitchRow(

                title="Acceso a la cámara",

                subtitle="Permitir el uso de la cámara",

                icon="privacy.svg",

                active=PrivacyService.camera()

            )

        )

        permissions.add(

            SwitchRow(

                title="Acceso al micrófono",

                subtitle="Permitir el uso del micrófono",

                icon="privacy.svg",

                active=PrivacyService.microphone()

            )

        )

        self.add(
            permissions
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

                active=PrivacyService.telemetry()

            )

        )

        self.add(
            diagnostics
        )