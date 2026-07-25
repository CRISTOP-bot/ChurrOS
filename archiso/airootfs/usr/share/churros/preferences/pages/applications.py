from widgets.page import Page
from widgets.group import Group
from widgets.row import Row
from widgets.switch_row import SwitchRow

from services.applications import ApplicationsService


class ApplicationsPage(Page):

    def __init__(self, navigator):

        super().__init__(
            navigator,
            "Aplicaciones",
            "Administrar aplicaciones instaladas"
        )

        #
        # Información
        #

        info = Group(
            "Información"
        )

        info.add(

            Row(

                title="Aplicaciones instaladas",

                subtitle="Cantidad de aplicaciones",

                icon="applications.svg",

                value=ApplicationsService.count()

            )

        )

        info.add(

            Row(

                title="Tienda",

                subtitle="Gestor principal",

                icon="applications.svg",

                value=ApplicationsService.store()

            )

        )

        self.add(
            info
        )

        #
        # Opciones
        #

        options = Group(
            "Opciones"
        )

        options.add(

            SwitchRow(

                title="Buscar actualizaciones",

                subtitle="Comprobar nuevas versiones automáticamente",

                icon="applications.svg",

                active=ApplicationsService.auto_updates()

            )

        )

        options.add(

            SwitchRow(

                title="Actualizar automáticamente",

                subtitle="Instalar actualizaciones automáticamente",

                icon="applications.svg",

                active=ApplicationsService.auto_install()

            )

        )

        self.add(
            options
        )