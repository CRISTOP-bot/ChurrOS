from widgets.page import Page
from widgets.group import Group
from widgets.combo_row import ComboRow

from services.power import PowerService


class PowerProfilePage(Page):

    def __init__(self, navigator):

        super().__init__(
            navigator,
            "Modo de energía",
            "Equilibra rendimiento y consumo",
            parent_page="power"
        )

        group = Group("Perfil")

        available = PowerService.power_profiles_available()
        current = PowerService.power_profile()

        labels = {
            "performance": "Rendimiento",
            "balanced": "Balanceado",
            "power-saver": "Ahorro de energía"
        }

        values = [labels.get(p, p) for p in available]
        selected = labels.get(current, current)

        self.combo = ComboRow(
            title="Perfil activo",
            values=values,
            selected=selected,
            callback=lambda label: self.on_profile_changed(label, available, labels)
        )

        group.add(self.combo)

        self.add(group)

    def on_profile_changed(self, label, available, labels):

        inverse = {v: k for k, v in labels.items()}

        profile = inverse.get(label)

        if profile:

            PowerService.set_power_profile(profile)
