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
from widgets.combo_row import ComboRow

from services.binds_service import BindsService
from services.dotfiles.niri_config import NiriConfig


class ShortcutsPage(Page):

    def __init__(self, navigator):

        super().__init__(
            navigator,
            "Atajos de teclado",
            "Keybindings de Niri",
            parent_page="appearance"
        )

        self._pending = False

        self._build()

    def _build(self):

        #
        # Anadir atajo
        #

        add_group = Group("Nuevo atajo")

        keys_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=4
        )
        keys_box.set_margin_start(14)
        keys_box.set_margin_end(14)
        keys_box.set_margin_top(10)

        keys_label = Gtk.Label(label="Tecla:")
        keys_label.set_xalign(0)
        keys_box.append(keys_label)

        self._keys_entry = Gtk.Entry()
        self._keys_entry.set_placeholder_text(
            "p.ej. Mod+Y, Ctrl+Shift+E, XF86AudioPlay"
        )

        keys_box.append(self._keys_entry)

        add_group.add(keys_box)

        actions = list(BindsService.SIMPLE_ACTIONS) + \
            list(BindsService.NUMERIC_ACTIONS) + [
                "spawn", "spawn-sh",
            ]

        self._action_combo = ComboRow(
            title="Accion",
            subtitle="Comando interno de niri",
            values=actions,
            selected="spawn",
            callback=lambda *_: self._on_action_changed()
        )

        add_group.add(self._action_combo)

        self._argument_entry = Gtk.Entry()
        self._argument_entry.set_placeholder_text(
            'Argumento (programa o workspace number)'
        )
        self._argument_entry.set_margin_start(14)
        self._argument_entry.set_margin_end(14)
        self._argument_entry.set_margin_top(10)

        add_group.add(self._argument_entry)

        self._modifier_entry = Gtk.Entry()
        self._modifier_entry.set_placeholder_text(
            "allow-when-locked=true  (opcional)"
        )
        self._modifier_entry.set_margin_start(14)
        self._modifier_entry.set_margin_end(14)
        self._modifier_entry.set_margin_top(10)
        self._modifier_entry.set_margin_bottom(6)

        add_group.add(self._modifier_entry)

        add_row = Row(
            title="Anadir atajo",
            subtitle="Registra la combinacion en niri",
            icon="shortcuts.svg",
            value=None
        )

        add_row.connect(
            "clicked",
            lambda *_: self._on_add_bind()
        )

        add_group.add(add_row)

        self.add(add_group)

        #
        # Lista de atajos
        #

        self._list_group = Group("Atajos definidos")

        self._binds_list = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=4
        )

        self._list_group.add(self._binds_list)

        self.add(self._list_group)

        self._refresh_list()

        #
        # Acciones
        #

        actions_group = Group("Acciones")

        reload_row = Row(
            title="Recargar Niri",
            subtitle="Aplica los cambios",
            icon="shortcuts.svg",
            value=None
        )

        reload_row.connect(
            "clicked",
            lambda *_: NiriConfig.reload()
        )

        actions_group.add(reload_row)

        self.add(actions_group)

    def _refresh_list(self):

        child = self._binds_list.get_first_child()

        while child is not None:

            nxt = child.get_next_sibling()
            self._binds_list.remove(child)
            child = nxt

        try:

            binds = BindsService.list_binds()

        except Exception as exc:

            label = Gtk.Label(label="Error: " + str(exc))
            label.set_xalign(0)
            label.set_wrap(True)
            label.set_margin_start(14)
            self._binds_list.append(label)
            return

        if not binds:

            label = Gtk.Label(label="No hay atajos definidos.")
            label.set_xalign(0)
            label.set_margin_start(14)
            label.set_margin_top(10)
            label.add_css_class("row-subtitle")
            self._binds_list.append(label)
            return

        for b in binds:

            self._binds_list.append(
                self._build_bind_row(b)
            )

    def _build_bind_row(self, bind):

        row = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=12
        )
        row.add_css_class("row")
        row.set_margin_top(8)
        row.set_margin_bottom(8)
        row.set_margin_start(14)
        row.set_margin_end(14)

        left = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=2
        )
        left.set_hexpand(True)

        title_label = Gtk.Label(label=bind["keys"])
        title_label.set_xalign(0)
        title_label.add_css_class("row-title")

        left.append(title_label)

        if bind.get("modifier"):
            title_label.set_label(
                bind["keys"] + "  (" + bind["modifier"] + ")"
            )

        action_summary = bind["action"]

        if bind.get("argument"):
            action_summary += " " + bind["argument"]

        sub_label = Gtk.Label(label="    " + action_summary)
        sub_label.set_xalign(0)
        sub_label.add_css_class("row-subtitle")
        sub_label.set_wrap(True)

        left.append(sub_label)

        row.append(left)

        del_btn = Gtk.Button(label="Borrar")
        del_btn.add_css_class("destructive-action")
        del_btn.connect(
            "clicked",
            lambda *_: self._on_delete_bind(bind["keys"])
        )

        row.append(del_btn)

        return row

    def _on_action_changed(self):

        action = self._action_combo.value()

        if action in BindsService.NUMERIC_ACTIONS:
            self._argument_entry.set_placeholder_text(
                "Numero de workspace (1-9)"
            )
        elif action == "spawn":
            self._argument_entry.set_placeholder_text(
                'Programa, p.ej. "foot"'
            )
        elif action == "spawn-sh":
            self._argument_entry.set_placeholder_text(
                'Comando de shell, p.ej. "wpctl set-volume ..."'
            )
        else:
            self._argument_entry.set_placeholder_text(
                "(esta accion no toma argumento)"
            )

    def _on_add_bind(self):

        keys = self._keys_entry.get_text().strip()

        if not keys:
            return

        action = self._action_combo.value()
        argument = self._argument_entry.get_text().strip()
        modifier = self._modifier_entry.get_text().strip()

        try:

            BindsService.add_bind(
                keys=keys,
                action=action,
                argument=argument,
                modifier=modifier,
            )

            self._keys_entry.set_text("")
            self._argument_entry.set_text("")
            self._modifier_entry.set_text("")

            NiriConfig.reload()

            self._refresh_list()

        except Exception as exc:

            dlg = Gtk.AlertDialog()
            dlg.set_heading("Error")
            dlg.set_message(str(exc))
            dlg.show(self.get_root())

    def _on_delete_bind(self, keys):

        dlg = Gtk.AlertDialog()
        dlg.set_heading("Borrar atajo")
        dlg.set_message("¿Borrar el atajo '" + keys + "'?")
        dlg.set_modal(True)
        dlg.set_buttons(["Cancelar", "Borrar"])

        def on_resp(d, r):

            try:
                resp = d.choose_finish(r)
            except Exception:
                return

            if resp != 1:
                return

            try:

                BindsService.delete_bind(keys)

                NiriConfig.reload()

                self._refresh_list()

            except Exception as exc:

                dlg2 = Gtk.AlertDialog()
                dlg2.set_heading("Error")
                dlg2.set_message(str(exc))
                dlg2.show(self.get_root())

        dlg.choose(self.get_root(), None, on_resp)
