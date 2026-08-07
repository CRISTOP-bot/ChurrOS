from widgets.page import Page
from widgets.group import Group
from widgets.combo_row import ComboRow
from widgets.row import Row

from services.power import PowerService


PROFILES = {
    "performance": {
        "label": "Rendimiento",
        "desc": "Maximo rendimiento, mas consumo. Ideal para juegos, "
                "edicion de video o cargas intensivas."
    },
    "balanced": {
        "label": "Balanceado",
        "desc": "Optima relacion entre rendimiento y consumo. Recomendado "
                "para uso diario."
    },
    "power-saver": {
        "label": "Ahorro de energia",
        "desc": "Minimo consumo, reloj reducido. Prolonga la bateria "
                "en portatiles."
    }
}


class PowerProfilePage(Page):

    def __init__(self, navigator):

        super().__init__(
            navigator,
            "Modo de energia",
            "Equilibra rendimiento y consumo",
            parent_page="power"
        )

        self._build()

    def _build(self):

        #
        # Estado actual
        #

        available = PowerService.power_profiles_available()

        if not available:

            info_group = Group("No soportado")

            info_group.add(
                Row(
                    title="Perfiles de energia no disponibles",
                    subtitle="powerprofilesctl no encontro perfiles en el hardware actual",
                    icon="power.svg"
                )
            )

            self.add(info_group)

            return

        current = PowerService.power_profile()

        if current in PROFILES:
            desc = PROFILES[current]["desc"]
        else:
            desc = "Perfil: " + current

        info_group = Group("Perfil actual")

        self.current_row = Row(
            title=PROFILES.get(current, {"label": current})["label"],
            subtitle=desc,
            icon="power.svg"
        )

        info_group.add(self.current_row)

        self.add(info_group)

        #
        # Cambiar perfil
        #

        profile_group = Group("Cambiar perfil")

        labels_map = {p: PROFILES.get(p, {"label": p})["label"]
                      for p in available}

        selected = labels_map.get(current, current)

        self.combo = ComboRow(
            title="Perfil activo",
            subtitle="El cambio se aplica de inmediato",
            values=[labels_map[p] for p in available],
            selected=selected,
            callback=lambda label: self.on_profile_changed(label, available, labels_map)
        )

        profile_group.add(self.combo)

        self.add(profile_group)

        #
        # Advertencias
        #

        self.warn_group = Group("Detalles del perfil")

        self.warn_label = None
        self._update_warn(current)

        self.add(self.warn_group)

    def _update_warn(self, profile):

        self.warn_group.clear()

        if profile == "performance":
            msg = ("Modo rendimiento activo. Ventilador puede subir de "
                   "revoluciones y la bateria se agota mas rapido.")
        elif profile == "power-saver":
            msg = ("Modo ahorro activo. Aplicaciones pesadas pueden "
                   "responder mas lentas; ideal para alargar la bateria.")
        else:
            msg = None

        if msg:
            self.warn_group.add(
                Row(
                    title="Como afecta al sistema",
                    subtitle=msg,
                    value=None
                )
            )

    def on_profile_changed(self, label, available, labels_map):

        inverse = {v: k for k, v in labels_map.items()}

        profile = inverse.get(label)

        if not profile:
            return

        try:
            PowerService.set_power_profile(profile)
        except Exception:
            pass

        self._update_warn(profile)
