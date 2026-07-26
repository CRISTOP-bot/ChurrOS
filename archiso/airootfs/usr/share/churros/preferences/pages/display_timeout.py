from widgets.page import Page
from widgets.group import Group
from widgets.combo_row import ComboRow

from services.power import PowerService


class DisplayTimeoutPage(Page):

    def __init__(self, navigator):

        super().__init__(
            navigator,
            "Apagar pantalla",
            "Tiempo de inactividad antes de apagar la pantalla",
            parent_page="power"
        )

        group = Group("Tiempo de espera")

        options = [
            ("1 minuto", 60),
            ("2 minutos", 120),
            ("5 minutos", 300),
            ("10 minutos", 600),
            ("15 minutos", 900),
            ("30 minutos", 1800),
            ("Nunca", 0),
        ]

        labels = [label for label, _ in options]
        current = PowerService.screen_timeout()

        selected = "Nunca"
        for label, value in options:
            if current == value:
                selected = label
                break

        self.options = options

        self.combo = ComboRow(
            title="Apagar tras",
            values=labels,
            selected=selected,
            callback=self.on_changed
        )

        group.add(self.combo)

        self.add(group)

    def on_changed(self, label):

        for lbl, value in self.options:

            if lbl == label:

                if value == 0:

                    try:
                        from services.settings import SettingsService
                        SettingsService.set("display.timeout", 0)
                    except Exception:
                        pass

                PowerService.set_screen_timeout(value)

                return
