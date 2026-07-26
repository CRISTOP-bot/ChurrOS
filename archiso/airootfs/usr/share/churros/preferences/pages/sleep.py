from widgets.page import Page
from widgets.group import Group
from widgets.combo_row import ComboRow
from widgets.switch_row import SwitchRow

from services.power import PowerService


class SleepPage(Page):

    def __init__(self, navigator):

        super().__init__(
            navigator,
            "Suspensión",
            "Suspensión automática y actions de tapa",
            parent_page="power"
        )

        group = Group("Suspensión automática")

        options = [
            ("5 minutos", 300),
            ("10 minutos", 600),
            ("15 minutos", 900),
            ("30 minutos", 1800),
            ("1 hora", 3600),
            ("Nunca", 0),
        ]

        labels = [label for label, _ in options]
        current = PowerService.sleep_timeout()

        selected = "Nunca"
        for label, value in options:
            if current == value:
                selected = label
                break

        self.options = options

        self.combo = ComboRow(
            title="Suspender tras",
            values=labels,
            selected=selected,
            callback=self.on_timeout_changed
        )

        group.add(self.combo)

        self.add(group)

        lid = Group("Cierre de tapa")

        actions = ["suspend", "hibernate", "nothing", "blank", "logout", "shutdown"]
        current_action = PowerService.lid_close_action()

        self.lid_combo = ComboRow(
            title="Al cerrar la tapa",
            values=actions,
            selected=current_action if current_action in actions else "suspend",
            callback=self.on_lid_changed
        )

        lid.add(self.lid_combo)

        self.add(lid)

    def on_timeout_changed(self, label):

        for lbl, value in self.options:

            if lbl == label:

                PowerService.set_sleep_timeout(value)

                return

    def on_lid_changed(self, action):

        PowerService.set_lid_close_action(action)
