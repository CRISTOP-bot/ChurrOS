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
from widgets.switch_row import SwitchRow

from services.window_rules_service import WindowRulesService
from services.dotfiles.niri_config import NiriConfig


class WindowRulesPage(Page):

    def __init__(self, navigator):

        super().__init__(
            navigator,
            "Reglas de ventana",
            "Window-rules de Niri: opacidad, flotantes, esquinas, blur",
            parent_page="appearance"
        )

        self._pending = []

        self._build()

    def _build(self):

        #
        # Lista de reglas
        #

        self._rules_group = Group("Reglas definidas")

        self._rules_list = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=8
        )

        self._rules_group.add(self._rules_list)

        self.add(self._rules_group)

        self._refresh_rules()

        #
        # Anadir nueva regla
        #

        add_group = Group("Anadir regla")

        self._app_id_entry = Gtk.Entry()
        self._app_id_entry.set_placeholder_text("app-id, p.ej. firefox")
        self._app_id_entry.set_margin_start(14)
        self._app_id_entry.set_margin_end(14)
        self._app_id_entry.set_margin_top(10)
        self._app_id_entry.set_margin_bottom(10)

        add_group.add(self._app_id_entry)

        self._title_entry = Gtk.Entry()
        self._title_entry.set_placeholder_text('regex del titulo (opcional)')
        self._title_entry.set_margin_start(14)
        self._title_entry.set_margin_end(14)
        self._title_entry.set_margin_bottom(10)

        add_group.add(self._title_entry)

        opacity_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=8
        )
        opacity_box.set_margin_start(14)
        opacity_box.set_margin_end(14)
        opacity_box.set_margin_bottom(10)

        opacity_label = Gtk.Label(label="Opacidad:")
        opacity_label.set_xalign(0)
        opacity_label.set_hexpand(True)

        self._opacity_spin = Gtk.SpinButton.new_with_range(
            0.0, 1.0, 0.05
        )
        self._opacity_spin.set_value(1.0)

        opacity_box.append(opacity_label)
        opacity_box.append(self._opacity_spin)

        add_group.add(opacity_box)

        corner_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=8
        )
        corner_box.set_margin_start(14)
        corner_box.set_margin_end(14)
        corner_box.set_margin_bottom(10)

        corner_label = Gtk.Label(label="Radio de esquinas:")
        corner_label.set_xalign(0)
        corner_label.set_hexpand(True)

        self._corner_spin = Gtk.SpinButton.new_with_range(
            0.0, 64.0, 1.0
        )
        self._corner_spin.set_value(0.0)

        corner_box.append(corner_label)
        corner_box.append(self._corner_spin)

        add_group.add(corner_box)

        self._floating_switch = SwitchRow(
            title="Abrir como flotante",
            subtitle="Las ventanas que matcheen se abren como popups",
            active=False,
            callback=lambda *_: None
        )

        add_group.add(self._floating_switch)

        self._clip_switch = SwitchRow(
            title="Recortar al geometry-corner-radius",
            subtitle="clip-to-geometry",
            active=False,
            callback=lambda *_: None
        )

        add_group.add(self._clip_switch)

        self._blur_switch = SwitchRow(
            title="Fondo con blur (background-effect)",
            subtitle="Desenfoque del fondo detras de la ventana",
            active=False,
            callback=lambda *_: None
        )

        add_group.add(self._blur_switch)

        add_row = Row(
            title="Anadir regla",
            subtitle="Crea una nueva window-rule con estos valores",
            icon="window_rules.svg",
            value=None
        )

        add_row.connect(
            "clicked",
            lambda *_: self._on_add_rule()
        )

        add_group.add(add_row)

        self._edit_index = None

        self._update_row = Row(
            title="Guardar cambios sobre la regla seleccionada",
            subtitle="Actualizar la regla que estas editando",
            icon="window_rules.svg",
            value=None
        )

        self._update_row.connect(
            "clicked",
            lambda *_: self._on_update_rule()
        )

        self._update_row.set_visible(False)

        add_group.add(self._update_row)

        self.add(add_group)

        #
        # Acciones
        #

        actions_group = Group("Acciones")

        reload_row = Row(
            title="Recargar Niri",
            subtitle="Aplica los cambios forzando una transicion",
            icon="logs.svg",
            value=None
        )

        reload_row.connect(
            "clicked",
            lambda *_: NiriConfig.reload()
        )

        actions_group.add(reload_row)

        self.add(actions_group)

    def _refresh_rules(self):

        child = self._rules_list.get_first_child()

        while child is not None:

            nxt = child.get_next_sibling()
            self._rules_list.remove(child)
            child = nxt

        try:

            rules = WindowRulesService.list_rules()

        except Exception as exc:

            label = Gtk.Label(label="Error: " + str(exc))
            label.set_xalign(0)
            label.set_wrap(True)
            self._rules_list.append(label)

            return

        if not rules:

            label = Gtk.Label(label="No hay reglas definidas.")
            label.set_xalign(0)
            label.add_css_class("row-subtitle")
            label.set_margin_start(14)
            label.set_margin_top(10)
            label.set_margin_bottom(10)

            self._rules_list.append(label)

            return

        for r in rules:

            self._rules_list.append(
                self._build_rule_card(r)
            )

    def _build_rule_card(
        self,
        rule
    ):

        card = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=6
        )
        card.add_css_class("row")
        card.set_margin_top(10)
        card.set_margin_bottom(10)
        card.set_margin_start(14)
        card.set_margin_end(14)

        title = rule["app_id"] or rule["title"] or "(sin filtro)"
        title_label = Gtk.Label(label="Regla: " + title)
        title_label.set_xalign(0)
        title_label.set_hexpand(True)
        title_label.add_css_class("row-title")

        card.append(title_label)

        summary_parts = []

        if rule.get("title") and rule.get("app_id"):
            summary_parts.append('title="' + rule["title"] + '"')

        if rule.get("opacity") is not None:
            summary_parts.append("opacity " + str(rule["opacity"]))

        if rule.get("open_floating") is not None:
            summary_parts.append(
                "open-floating " +
                ("true" if rule["open_floating"] else "false")
            )

        if rule.get("corner_radius") is not None:
            summary_parts.append(
                "radius " + str(rule["corner_radius"])
            )

        if rule.get("clip_to_geometry") is not None:
            summary_parts.append(
                "clip " +
                ("true" if rule["clip_to_geometry"] else "false")
            )

        if rule.get("blur") is not None:
            summary_parts.append(
                "blur " + ("true" if rule["blur"] else "false")
            )

        summary = Gtk.Label(
            label="    " + (", ".join(summary_parts) or "(sin cambios)")
        )
        summary.set_xalign(0)
        summary.set_hexpand(True)
        summary.add_css_class("row-subtitle")
        summary.set_wrap(True)

        card.append(summary)

        actions = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=8
        )
        actions.set_halign(Gtk.Align.END)

        edit_btn = Gtk.Button(label="Editar")
        edit_btn.add_css_class("suggested-action")
        edit_btn.connect(
            "clicked",
            lambda *_: self._on_edit_rule(rule["index"])
        )

        del_btn = Gtk.Button(label="Borrar")
        del_btn.add_css_class("destructive-action")
        del_btn.connect(
            "clicked",
            lambda *_: self._on_delete_rule(rule["index"])
        )

        actions.append(edit_btn)
        actions.append(del_btn)

        card.append(actions)

        return card

    def _on_add_rule(self):

        app_id = self._app_id_entry.get_text().strip()
        title = self._title_entry.get_text().strip()

        opacity = self._opacity_spin.get_value()
        if opacity >= 1.0:
            opacity = None

        corner_radius = self._corner_spin.get_value()
        if corner_radius == 0.0:
            corner_radius = None

        try:

            WindowRulesService.add_rule(
                app_id=app_id,
                title=title,
                opacity=opacity,
                open_floating=self._floating_switch.get_active() or None,
                corner_radius=corner_radius,
                clip_to_geometry=self._clip_switch.get_active() or None,
                blur=self._blur_switch.get_active() or None,
            )

            self._reset_form()

            NiriConfig.reload()

            self._refresh_rules()

        except Exception as exc:

            dlg = Gtk.AlertDialog()
            dlg.set_heading("Error")
            dlg.set_message(str(exc))
            dlg.show(self.get_root())

    def _on_update_rule(self):

        if self._edit_index is None:
            return

        app_id = self._app_id_entry.get_text().strip()
        title = self._title_entry.get_text().strip()

        update = {
            "app_id": app_id,
            "title": title,
        }

        opacity = self._opacity_spin.get_value()
        update["opacity"] = None if opacity >= 1.0 else opacity

        corner_radius = self._corner_spin.get_value()
        update["corner_radius"] = None if corner_radius == 0.0 \
            else corner_radius

        update["open_floating"] = \
            self._floating_switch.get_active() or None

        update["clip_to_geometry"] = \
            self._clip_switch.get_active() or None

        update["blur"] = self._blur_switch.get_active() or None

        try:

            WindowRulesService.update_rule(self._edit_index, **update)

            self._edit_index = None

            self._update_row.set_visible(False)

            self._reset_form()

            NiriConfig.reload()

            self._refresh_rules()

        except Exception as exc:

            dlg = Gtk.AlertDialog()
            dlg.set_heading("Error")
            dlg.set_message(str(exc))
            dlg.show(self.get_root())

    def _reset_form(self):

        self._app_id_entry.set_text("")
        self._title_entry.set_text("")
        self._opacity_spin.set_value(1.0)
        self._corner_spin.set_value(0.0)
        self._floating_switch.set_active(False)
        self._clip_switch.set_active(False)
        self._blur_switch.set_active(False)

    def _on_delete_rule(self, index):

        dlg = Gtk.AlertDialog()
        dlg.set_heading("Borrar regla")
        dlg.set_message("¿Seguro que quieres borrar esta regla?")
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

                WindowRulesService.delete_rule(index)

                NiriConfig.reload()

                self._refresh_rules()

            except Exception as exc:

                dlg2 = Gtk.AlertDialog()
                dlg2.set_heading("Error")
                dlg2.set_message(str(exc))
                dlg2.show(self.get_root())

        dlg.choose(self.get_root(), None, on_resp)

    def _on_edit_rule(self, index):

        try:
            rules = WindowRulesService.list_rules()
        except Exception as exc:
            return

        for r in rules:
            if r["index"] == index:
                match = r
                break
        else:
            return

        self._app_id_entry.set_text(match.get("app_id") or "")
        self._title_entry.set_text(match.get("title") or "")

        if match.get("opacity") is not None:
            self._opacity_spin.set_value(float(match["opacity"]))

        if match.get("corner_radius") is not None:
            self._corner_spin.set_value(float(match["corner_radius"]))

        self._floating_switch.set_active(
            bool(match.get("open_floating", False))
        )
        self._clip_switch.set_active(
            bool(match.get("clip_to_geometry", False))
        )
        self._blur_switch.set_active(
            bool(match.get("blur", False))
        )

        self._edit_index = index
        self._update_row.set_visible(True)