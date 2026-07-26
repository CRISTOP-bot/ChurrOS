from widgets.page import Page
from widgets.group import Group
from widgets.row import Row

from services.power import PowerService


class BatteryPage(Page):

    def __init__(self, navigator):

        super().__init__(
            navigator,
            "Batería",
            "Estado y nivel de carga",
            parent_page="power"
        )

        present = PowerService.battery_present()

        info = Group("Estado")

        if not present:

            info.add(
                Row(
                    title="Batería",
                    subtitle="No se detecta ninguna batería",
                    icon="power.svg",
                    value="—"
                )
            )

            self.add(info)
            return

        info.add(
            Row(
                title="Nivel de carga",
                subtitle="Porcentaje actual",
                icon="power.svg",
                value=f"{PowerService.battery_percentage()} %"
            )
        )

        info.add(
            Row(
                title="Estado",
                subtitle="Cargando / descargando / llena",
                icon="power.svg",
                value=PowerService.battery_state()
            )
        )

        info.add(
            Row(
                title="Modo de energía",
                subtitle="Perfil activo del sistema",
                icon="power.svg",
                value=PowerService.power_profile()
            )
        )

        self.add(info)
