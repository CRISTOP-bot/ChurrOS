import subprocess
from datetime import datetime

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GLib

from widgets.page import Page
from widgets.group import Group
from widgets.row import Row
from widgets.switch_row import SwitchRow

from services.datetime import DatetimeService


class DateTimePage(Page):

    def __init__(self, navigator):

        super().__init__(
            navigator,
            "Fecha y hora",
            "Configura la hora, fecha y zona horaria del sistema",
        )

        self._pending = False

        self._build()

        GLib.timeout_add_seconds(1, self._tick_clock)

    def _build(self):

        info = Group("Estado actual")

        self.clock_row = Row(
            title="Hora del sistema",
            subtitle=datetime.now().strftime("%H:%M:%S"),
            icon="system.svg",
        )

        info.add(self.clock_row)

        self.date_row = Row(
            title="Fecha",
            subtitle=datetime.now().strftime("%A %d de %B de %Y"),
            icon="system.svg",
        )

        info.add(self.date_row)

        tz = DatetimeService.get_timezone()

        self.tz_row = Row(
            title="Zona horaria",
            subtitle=tz or "Desconocida",
            icon="system.svg",
        )

        info.add(self.tz_row)

        rtc = DatetimeService.get_rtc_time()
        self.rtc_row = Row(
            title="Reloj hardware (RTC)",
            subtitle=rtc or "No disponible",
            icon="system.svg",
        )

        info.add(self.rtc_row)

        self.add(info)

        #
        # Sincronización NTP
        #

        ntp_group = Group("Sincronización automática")

        self.ntp_switch = SwitchRow(
            title="NTP (Network Time Protocol)",
            subtitle="Mantiene la hora sincronizada con servidores de internet",
            active=DatetimeService.get_ntp(),
            callback=lambda v: self._on_ntp_toggle(v)
        )

        ntp_group.add(self.ntp_switch)

        self.add(ntp_group)

        #
        # Zona horaria
        #

        tz_group = Group("Cambiar zona horaria")

        search_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=6
        )
        search_box.set_margin_start(14)
        search_box.set_margin_end(14)
        search_box.set_margin_top(8)
        search_box.set_margin_bottom(8)

        search_label = Gtk.Label(label="Buscar zona horaria")
        search_label.set_xalign(0)
        search_label.add_css_class("row-title")

        search_box.append(search_label)

        self.tz_entry = Gtk.SearchEntry()
        self.tz_entry.set_placeholder_text(
            "Escribe una ciudad o region (ej. Madrid, Bogota, Tokyo)"
        )
        self.tz_entry.connect("search-changed", self._on_tz_filter)

        search_box.append(self.tz_entry)

        tz_group.add(search_box)

        self.tz_popover = Gtk.Popover()
        self.tz_popover.set_parent(self.tz_entry)
        self.tz_popover.set_position(Gtk.PositionType.BOTTOM)
        self.tz_popover.set_autohide(True)
        self.tz_popover.set_size_request(420, 320)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_max_content_height(360)
        scrolled.set_propagate_natural_height(True)

        self.tz_listbox = Gtk.ListBox()
        self.tz_listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.tz_listbox.connect(
            "row-activated",
            lambda lb, row: self._on_tz_select(row)
        )

        scrolled.set_child(self.tz_listbox)
        self.tz_popover.set_child(scrolled)

        self._all_zones = DatetimeService.list_timezones()
        self._filtered_zones = list(self._all_zones)

        self._populate_tz_list(self._filtered_zones)

        self.tz_status = Row(
            title="Zona actual",
            subtitle=DatetimeService.current_zone_short() or "Sin definir",
            icon="system.svg"
        )

        tz_group.add(self.tz_status)

        self.add(tz_group)

    def _populate_tz_list(self, zones):

        child = self.tz_listbox.get_first_child()
        while child is not None:
            nxt = child.get_next_sibling()
            self.tz_listbox.remove(child)
            child = nxt

        if not zones:
            empty = Gtk.ListBoxRow()
            label = Gtk.Label(label="Sin resultados")
            label.set_margin_top(10)
            label.set_margin_bottom(10)
            label.set_margin_start(12)
            empty.set_child(label)
            self.tz_listbox.append(empty)
            return

        for tz in zones[:200]:
            row = Gtk.ListBoxRow()

            box = Gtk.Box(
                orientation=Gtk.Orientation.VERTICAL,
                spacing=2
            )
            box.set_margin_top(6)
            box.set_margin_bottom(6)
            box.set_margin_start(12)
            box.set_margin_end(12)

            title = Gtk.Label(label=tz.split("/")[-1].replace("_", " "))
            title.set_xalign(0)
            title.add_css_class("row-title")

            box.append(title)

            if tz != tz.split("/")[-1].replace("_", " "):
                path = Gtk.Label(label=tz)
                path.set_xalign(0)
                path.add_css_class("row-subtitle")
                box.append(path)

            row.set_child(box)
            row._tz_value = tz
            self.tz_listbox.append(row)

    def _on_tz_filter(self, entry):

        query = entry.get_text().lower().strip()

        if not query:
            self._filtered_zones = list(self._all_zones)
        else:
            self._filtered_zones = [
                z for z in self._all_zones
                if query in z.lower()
            ]

        self._populate_tz_list(self._filtered_zones)

        if self._filtered_zones:

            self.tz_popover.popup()

        else:

            self.tz_popover.popdown()

    def _on_tz_select(self, row):

        tz = getattr(row, "_tz_value", None)

        if not tz:
            return

        self.tz_popover.popdown()
        self.tz_entry.set_text("")

        self._set_status(f"Aplicando zona horaria {tz}...")

        def worker():

            ok = DatetimeService.set_timezone(tz)

            GLib.idle_add(self._on_tz_applied, tz, ok)

        import threading

        threading.Thread(target=worker, daemon=True).start()

    def _on_tz_applied(self, tz, ok):

        if ok:
            self._set_status(f"Zona horaria cambiada a {tz}")
        else:
            self._set_status(
                "No se pudo cambiar la zona. Verifica que tienes pkexec instalado."
            )

        self._refresh_info()

    def _on_ntp_toggle(self, enabled):

        self._set_status(
            "Activando sincronizacion automatica..." if enabled
            else "Desactivando sincronizacion automatica..."
        )

        def worker():

            ok = DatetimeService.set_ntp(enabled)

            GLib.idle_add(self._on_ntp_applied, enabled, ok)

        import threading

        threading.Thread(target=worker, daemon=True).start()

    def _on_ntp_applied(self, enabled, ok):

        if ok:
            self._set_status(
                "NTP activado: hora sincronizada con internet"
                if enabled
                else "NTP desactivado"
            )
        else:
            self._set_status(
                "No se pudo cambiar NTP. Verifica pkexec o systemd-timesyncd."
            )

    def _set_status(self, text):

        if hasattr(self, "tz_status"):

            try:
                self.tz_status.set_subtitle(text)
            except Exception:
                pass

    def _refresh_info(self):

        tz = DatetimeService.get_timezone()

        try:
            self.tz_row.set_subtitle(tz or "Desconocida")
        except Exception:
            pass

        try:
            self.tz_status.set_subtitle(
                DatetimeService.current_zone_short() or tz
            )
        except Exception:
            pass

        try:
            self.ntp_switch.set_active(DatetimeService.get_ntp())
        except Exception:
            pass

        try:
            self.rtc_row.set_subtitle(
                DatetimeService.get_rtc_time() or "No disponible"
            )
        except Exception:
            pass

    def _tick_clock(self):

        now = datetime.now()

        try:
            self.clock_row.set_subtitle(now.strftime("%H:%M:%S"))
            self.date_row.set_subtitle(now.strftime("%A %d de %B de %Y"))
        except Exception:
            pass

        return True
