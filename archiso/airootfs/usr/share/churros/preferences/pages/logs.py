import sys
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PREF = os.path.abspath(os.path.join(ROOT, "preferences"))

sys.path.insert(0, ROOT)
sys.path.insert(0, PREF)

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GLib

from widgets.page import Page
from widgets.group import Group
from widgets.row import Row

from services.logs_service import LogsService


class LogsPage(Page):

    def __init__(self, navigator):

        super().__init__(
            navigator,
            "Logs de Niri",
            "Registros del compositor y validacion de config",
            parent_page="system"
        )

        self._build()

    def _build(self):

        #
        # Validacion
        #

        validate_group = Group("Validacion del config")

        self._validate_status = Gtk.Label(
            label="Validando..."
        )
        self._validate_status.set_xalign(0)
        self._validate_status.set_margin_start(14)
        self._validate_status.set_margin_end(14)
        self._validate_status.set_margin_top(10)
        self._validate_status.set_margin_bottom(10)
        self._validate_status.set_wrap(True)

        validate_group.add(self._validate_status)

        validate_row = Row(
            title="Revalidar",
            subtitle="Ejecuta niri validate sobre tu config actual",
            icon="logs.svg",
            value=None
        )

        validate_row.connect(
            "clicked",
            lambda *_: GLib.idle_add(self._refresh_validate)
        )

        validate_group.add(validate_row)

        self.add(validate_group)

        self._refresh_validate()

        #
        # Logs
        #

        logs_group = Group("Registro de eventos")

        self._scrolled = Gtk.ScrolledWindow()
        self._scrolled.set_vexpand(True)
        self._scrolled.set_min_content_height(360)
        self._scrolled.set_max_content_height(420)
        self._scrolled.set_propagate_natural_height(True)

        self._log_view = Gtk.TextView()
        self._log_view.set_editable(False)
        self._log_view.set_monospace(True)
        self._log_view.set_wrap_mode(Gtk.WrapMode.CHAR)

        self._buffer = self._log_view.get_buffer()

        self._scrolled.set_child(self._log_view)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)

        reload_row = Row(
            title="Actualizar",
            subtitle="Vuelve a leer el journal en busca de logs de niri",
            icon="logs.svg",
            value=None
        )

        reload_row.connect(
            "clicked",
            lambda *_: GLib.idle_add(self._refresh_logs)
        )

        box.append(reload_row)
        box.append(self._scrolled)

        logs_group.add(box)

        self.add(logs_group)

        self._refresh_logs()

    def _refresh_validate(self):

        def worker():

            ok, msg = LogsService.niri_validate()

            if ok:
                text = "Config valida."
                cls_name = "row-subtitle"
            else:
                text = "Config invalida:\n" + msg
                cls_name = "row-title"

            GLib.idle_add(
                lambda: self._set_validate(text, cls_name)
            )

        self._set_validate("Validando...", "row-subtitle")

        import threading

        threading.Thread(
            target=worker,
            daemon=True
        ).start()

    def _set_validate(self, text, css_class):

        ctx = self._validate_status.get_style_context()
        for c in ("row-title", "row-subtitle"):
            ctx.remove_class(c)
        ctx.add_class(css_class)
        self._validate_status.set_label(text)

    def _refresh_logs(self):

        def worker():

            text = LogsService.niri_logs(limit=400)

            GLib.idle_add(
                lambda: self._set_log(text or "(sin logs)")
            )

        self._set_log("Cargando...")

        import threading

        threading.Thread(
            target=worker,
            daemon=True
        ).start()

    def _set_log(self, text):

        self._buffer.set_text(text)

        end = self._buffer.get_end_iter()
        self._log_view.scroll_to_iter(
            end,
            0.0,
            False,
            0.0,
            1.0
        )
