from widgets.page import Page
from widgets.group import Group
from widgets.row import Row

from services.about import AboutService


class AboutPage(Page):

    def __init__(self, navigator):

        super().__init__(
            navigator,
            "Acerca de",
            "Información de ChurrOS"
        )

        #
        # ChurrOS
        #

        system = Group(
            "ChurrOS"
        )

        system.add(

            Row(

                title="Distribución",

                subtitle="Sistema operativo",

                icon="system.svg",

                value=AboutService.distro()

            )

        )

        system.add(

            Row(

                title="Versión",

                subtitle="Versión instalada",

                icon="system.svg",

                value=AboutService.version()

            )

        )

        system.add(

            Row(

                title="Edición",

                subtitle="Canal de desarrollo",

                icon="system.svg",

                value=AboutService.edition()

            )

        )

        self.add(
            system
        )

        #
        # Software
        #

        software = Group(
            "Software"
        )

        software.add(

            Row(

                title="Kernel",

                subtitle="Versión del kernel",

                icon="applications.svg",

                value=AboutService.kernel()

            )

        )

        software.add(

            Row(

                title="Base",

                subtitle="Distribución base",

                icon="applications.svg",

                value=AboutService.base()

            )

        )

        software.add(

            Row(

                title="Sesión",

                subtitle="Entorno actual",

                icon="applications.svg",

                value=AboutService.session()

            )

        )

        self.add(
            software
        )

        #
        # Proyecto
        #

        project = Group(
            "Proyecto"
        )

        project.add(

            Row(

                title="Desarrollador",

                subtitle="Proyecto iniciado por",

                icon="about.svg",

                value=AboutService.developer()

            )

        )

        project.add(

            Row(

                title="Licencia",

                subtitle="Licencia del proyecto",

                icon="about.svg",

                value=AboutService.license()

            )

        )

        self.add(
            project
        )