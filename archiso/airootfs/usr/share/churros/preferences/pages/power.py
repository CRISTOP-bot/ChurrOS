from widgets.page import Page
from widgets.group import Group
from widgets.navigation_row import NavigationRow
from widgets.switch_row import SwitchRow


class PowerPage(Page):

    def __init__(self, navigator):

        super().__init__(
            navigator,
            "Energía",
            "Batería y rendimiento"
        )

        #
        # Perfil
        #

        profile = Group("Perfil de energía")

        profile.add(

            NavigationRow(

                navigator,

                "Modo de energía",

                "power.svg",

                "power-profile",

                "Balanceado, ahorro o rendimiento"

            )

        )

        self.add(profile)

        #
        # Batería
        #

        battery = Group("Batería")

        battery.add(

            NavigationRow(

                navigator,

                "Estado de la batería",

                "power.svg",

                "battery",

                "Información sobre la batería"

            )

        )

        battery.add(

            SwitchRow(

                title="Ahorro de energía",

                subtitle="Reducir el consumo cuando sea posible",

                icon="power.svg",

                active=False

            )

        )

        self.add(battery)

        #
        # Pantalla
        #

        display = Group("Pantalla")

        display.add(

            NavigationRow(

                navigator,

                "Apagar pantalla",

                "power.svg",

                "display-timeout",

                "Tiempo de espera de la pantalla"

            )

        )

        self.add(display)

        #
        # Suspensión
        #

        suspend = Group("Suspensión")

        suspend.add(

            NavigationRow(

                navigator,

                "Suspensión automática",

                "power.svg",

                "sleep",

                "Configurar la suspensión"

            )

        )

        suspend.add(

            SwitchRow(

                title="Suspender al cerrar la tapa",

                subtitle="Solo en portátiles",

                icon="power.svg",

                active=True

            )

        )

        self.add(suspend)