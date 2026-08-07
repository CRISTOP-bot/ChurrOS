import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GLib

from widgets.page import Page
from widgets.group import Group
from widgets.row import Row
from widgets.switch_row import SwitchRow
from widgets.slider_row import SliderRow

from services.night_light import NightLightService


class NightLightPage(Page):

    def __init__(self, navigator):

        super().__init__(
            navigator,
            "Luz nocturna",
            "Temperatura de color y filtro de luz azul",
            parent_page="appearance"
        )

        self._pending = False

        self._build()

    def _build(self):

        if not NightLightService.is_available():

            warn = Group("No disponible")

            warn.add(
                Row(
                    title="wlsunset no esta instalado",
                    subtitle="Para activar la luz nocturna necesitas el paquete wlsunset",
                    icon="night_light.svg"
                )
            )

            self.add(warn)

            return

        state_group = Group("Estado")

        self.enabled_switch = SwitchRow(
            title="Activar luz nocturna",
            subtitle="Ajusta la temperatura del color segun la hora del dia",
            active=NightLightService.is_enabled(),
            callback=lambda v: self._on_enable_toggle(v)
        )

        state_group.add(self.enabled_switch)

        self.status_row = Row(
            title="Estado de wlsunset",
            subtitle=self._status_text(),
            icon="night_light.svg"
        )

        state_group.add(self.status_row)

        self.add(state_group)

        temp_group = Group("Temperatura de color")

        self.day_slider = SliderRow(
            title="Temperatura de dia",
            subtitle="Color en Kelvin durante el dia (6500K = neutro)",
            value=float(NightLightService.get_temp_day()),
            minimum=3500.0,
            maximum=10000.0,
            step=100.0,
            callback=lambda *_: self._schedule_apply()
        )

        temp_group.add(self.day_slider)

        self.night_slider = SliderRow(
            title="Temperatura de noche",
            subtitle="Color en Kelvin durante la noche (mas bajo = mas calido)",
            value=float(NightLightService.get_temp_night()),
            minimum=2500.0,
            maximum=6500.0,
            step=100.0,
            callback=lambda *_: self._schedule_apply()
        )

        temp_group.add(self.night_slider)

        self.add(temp_group)

        gamma_group = Group("Gamma")

        self.gamma_slider = SliderRow(
            title="Intensidad",
            subtitle="1.0 = maximo, 0.5 = moderado",
            value=float(NightLightService.get_gamma()),
            minimum=0.1,
            maximum=1.0,
            step=0.05,
            callback=lambda *_: self._schedule_apply()
        )

        gamma_group.add(self.gamma_slider)

        self.add(gamma_group)

        loc_group = Group("Ubicacion manual")

        info = Row(
            title="Latitud / Longitud",
            subtitle="Si las desactivas, wlsunset usara la geolocalizacion automatica"
        )

        loc_group.add(info)

        self.lat_entry = Gtk.Entry()
        self.lat_entry.set_placeholder_text("Latitud (-90 a 90)")
        self.lat_entry.set_margin_start(14)
        self.lat_entry.set_margin_end(14)
        self.lat_entry.set_margin_top(8)
        self.lat_entry.set_margin_bottom(8)

        lat, lng = NightLightService.get_location()

        if lat is not None:
            self.lat_entry.set_text(str(lat))

        loc_group.add(self.lat_entry)

        self.lng_entry = Gtk.Entry()
        self.lng_entry.set_placeholder_text("Longitud (-180 a 180)")
        self.lng_entry.set_margin_start(14)
        self.lng_entry.set_margin_end(14)
        self.lng_entry.set_margin_bottom(8)

        if lng is not None:
            self.lng_entry.set_text(str(lng))

        loc_group.add(self.lng_entry)

        apply_row = Row(
            title="Aplicar ubicacion",
            subtitle="Usa la latitud/longitud manual (o vacia para geolocalizar)",
            icon="night_light.svg"
        )

        apply_row.connect("clicked", lambda *_: self._on_location_apply())

        loc_group.add(apply_row)

        self.add(loc_group)

        self._refresh_status()

        GLib.timeout_add_seconds(
            5,
            lambda: (self._refresh_status(), True)[-1]
        )

    def _on_enable_toggle(self, value):

        NightLightService.set_enabled(value)

        self._refresh_status()

    def _status_text(self):

        if NightLightService.is_running():
            return "wlsunset ejecutandose"

        if NightLightService.is_enabled():
            return "wlsunset activado pero no se esta ejecutando"

        return "wlsunset desactivado"

    def _refresh_status(self):

        try:
            self.status_row.set_subtitle(self._status_text())
        except Exception:
            pass

    def _on_location_apply(self):

        try:
            lat = float(self.lat_entry.get_text()) if self.lat_entry.get_text() else None
        except ValueError:
            lat = None

        try:
            lng = float(self.lng_entry.get_text()) if self.lng_entry.get_text() else None
        except ValueError:
            lng = None

        NightLightService.set_location(lat, lng)

        self._refresh_status()

    def _schedule_apply(self):

        if self._pending:
            return

        self._pending = True

        def apply():

            self._pending = False

            try:

                NightLightService.set_temps(
                    self.day_slider.get_value(),
                    self.night_slider.get_value()
                )

                NightLightService.set_gamma(
                    self.gamma_slider.get_value()
                )

                self._refresh_status()

            except Exception as exc:

                print("[night-light] apply fallo:", exc)

        GLib.timeout_add(400, apply)
