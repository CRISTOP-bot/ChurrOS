import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GLib

from widgets.page import Page
from widgets.group import Group
from widgets.row import Row

from services.keyboard import KeyboardService

ACTION_TYPES = {
    "spawn": "Ejecutar programa",
    "spawn-sh": "Ejecutar shell",
    "builtin": "Accion de Niri",
}


class KeyboardPage(Page):

    def __init__(self, navigator):

        super().__init__(
            navigator,
            "Atajos de teclado",
            "Modifica los atajos de teclado de Niri",
        )

        self._build()

    def _build(self):

        try:
            self.binds = KeyboardService.get_keybinds()
        except Exception:
            self.binds = []

        hint = Group("Info")

        hint.add(
            Row(
                title="Haz clic en un atajo para editarlo",
                subtitle="Los cambios se guardan en config.kdl al instante",
                icon="system.svg",
            )
        )

        self.add(hint)

        add_group = Group("Agregar")
        add_btn = Row(
            title="Agregar nuevo atajo",
            subtitle="Define una nueva combinacion de teclas",
            icon="system.svg",
            callback=lambda *_: self._add_new_bind(),
        )
        add_group.add(add_btn)
        self.add(add_group)

        categories = {
            "Aplicaciones": [],
            "Ventanas": [],
            "Workspaces": [],
            "Movimiento": [],
            "Capturas": [],
            "Overlays": [],
            "Multimedia": [],
            "Niri": [],
        }

        for bind in self.binds:
            cmd = bind["command"]
            bind_type = bind["type"]

            cat = self._categorize(cmd, bind_type)
            categories[cat].append(bind)

        for cat_name, cat_binds in categories.items():
            if not cat_binds:
                continue

            group = Group(cat_name)
            for bind in cat_binds:
                self._add_bind_row(group, bind)
            self.add(group)

    @staticmethod
    def _categorize(cmd, bind_type):
        c = cmd.lower()

        if bind_type == "spawn" or bind_type == "spawn-sh":
            if any(w in c for w in ("churros", "thunar", "fuzzel", "foot", "store")):
                return "Aplicaciones"
            return "Aplicaciones"

        wm = [
            "close-window", "quit", "maximize-column", "fullscreen-window",
            "switch-preset-column-width", "toggle-window-floating",
            "switch-focus-between-floating-and-tiling"
        ]
        if cmd in wm:
            return "Ventanas"

        move_keys = [
            "focus-column-left", "focus-column-right", "focus-window-up", "focus-window-down",
            "move-column-left", "move-column-right", "move-window-up", "move-window-down"
        ]
        if cmd in move_keys:
            return "Movimiento"

        if "focus-workspace" in cmd or "move-window-to-workspace" in cmd:
            return "Workspaces"

        if "screenshot" in cmd:
            return "Capturas"

        if "hotkey-overlay" in cmd or "toggle-overview" in cmd:
            return "Overlays"

        if "battery" in cmd or "XFBattery" in cmd or "playerctl" in cmd:
            return "Multimedia"

        if any(w in cmd for w in ["wpctl", "pamixer", "audio", "mute", "volume"]):
            return "Audio"

        if "brightness" in cmd.lower():
            return "Multimedia"

        return "Niri"

    def _add_bind_row(self, group, bind):
        key = bind["key"]
        cmd = bind["command"]
        args = bind["args"]
        bind_type = bind["type"]
        type_label = ACTION_TYPES.get(bind_type, bind_type)

        if bind_type == "spawn" and cmd:
            summary = cmd
            if args:
                summary = "{} {}".format(cmd, args)
        elif bind_type == "spawn-sh" and cmd:
            summary = "shell: " + cmd
        elif bind_type == "builtin" and cmd:
            summary = cmd
            if args:
                summary = "{} {}".format(cmd, args)
        else:
            summary = cmd or "(vacio)"

        info_row = Row(
            title=summary,
            subtitle=type_label,
            icon="system.svg",
            callback=lambda *__, b=bind: self._edit_bind(b)
        )
        group.add(info_row)

    def _edit_bind(self, bind):

        key = bind["key"]
        bind_type = bind["type"]
        command = bind["command"]
        args = bind["args"]

        dialog = Gtk.Window()
        dialog.set_title("Editar atajo")
        dialog.set_default_size(440, 280)
        dialog.set_resizable(False)
        dialog.set_decorated(True)
        dialog.set_modal(True)
        root = self.get_root()
        if root is not None:
            dialog.set_transient_for(root)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.set_margin_top(16)
        vbox.set_margin_bottom(16)
        vbox.set_margin_start(16)
        vbox.set_margin_end(16)

        header = Gtk.Label()
        header.set_markup("<b>Cambiar atajo</b>")
        header.set_xalign(0)
        vbox.append(header)

        current_label = Gtk.Label()
        current_label.set_markup(
                "Atajo actual: <b>{}</b>\nAccion: {}".format(key, command)
            )
        current_label.set_xalign(0)
        current_label.set_wrap(True)
        vbox.append(current_label)

        vbox.append(Gtk.Separator())

        new_key_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        new_key_label = Gtk.Label(label="Nuevo atajo:")
        new_key_label.set_xalign(0)
        new_key_box.append(new_key_label)
        new_key_entry = Gtk.Entry()
        new_key_entry.set_placeholder_text("Ej: Mod+Shift+X")
        new_key_box.append(new_key_entry)
        vbox.append(new_key_box)

        new_cmd_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        new_cmd_label = Gtk.Label(label="Nuevo comando:")
        new_cmd_label.set_xalign(0)
        new_cmd_box.append(new_cmd_label)
        new_cmd_entry = Gtk.Entry()
        new_cmd_entry.set_text(command)
        new_cmd_box.append(new_cmd_entry)
        vbox.append(new_cmd_box)

        args_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        args_label = Gtk.Label(label="Argumentos:")
        args_label.set_xalign(0)
        args_box.append(args_label)
        args_entry = Gtk.Entry()
        args_entry.set_text(args or "")
        args_box.append(args_entry)
        vbox.append(args_box)

        buttons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        buttons.set_halign(Gtk.Align.END)

        cancel_btn = Gtk.Button(label="Cancelar")
        cancel_btn.connect("clicked", lambda *_: dialog.close())
        buttons.append(cancel_btn)

        save_btn = Gtk.Button(label="Guardar")
        save_btn.add_css_class("suggested-action")

        def on_save(*_):
            new_key = new_key_entry.get_text().strip()
            new_cmd = new_cmd_entry.get_text().strip()

            if not new_key:
                dialog.close()
                e = Gtk.AlertDialog()
                e.set_message("Define la nueva combinacion de teclas")
                e.show()
                return

            new_args = args_entry.get_text().strip()
            bind_type_new = bind["type"]

            if new_cmd.startswith("spawn "):
                bind_type_new = "spawn"
                parts = new_cmd.split(None, 1)
                actual_cmd = parts[1] if len(parts) > 1 else ""
                if not new_args and " " in actual_cmd:
                    tokens = actual_cmd.split(None, 1)
                    actual_cmd = tokens[0]
                    new_args = tokens[1] if len(tokens) > 1 else ""
                new_cmd = actual_cmd
            else:
                actual_cmd = new_cmd

            ok = KeyboardService.set_keybind(key, bind_type_new, actual_cmd, new_args)
            dialog.close()

            if not ok:
                e = Gtk.AlertDialog()
                e.set_message("No se pudo guardar el atajo")
                e.show()
            else:
                GLib.idle_add(lambda: self._rebuild())

        save_btn.connect("clicked", on_save)
        buttons.append(save_btn)

        vbox.append(buttons)

        dialog.set_child(vbox)
        dialog.present()

    def _add_new_bind(self):

        dialog = Gtk.Window()
        dialog.set_title("Nuevo atajo")
        dialog.set_default_size(440, 260)
        dialog.set_resizable(False)
        dialog.set_decorated(True)
        dialog.set_modal(True)
        root = self.get_root()
        if root is not None:
            dialog.set_transient_for(root)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.set_margin_top(16)
        vbox.set_margin_bottom(16)
        vbox.set_margin_start(16)
        vbox.set_margin_end(16)

        header = Gtk.Label()
        header.set_markup("<b>Nuevo atajo de teclado</b>")
        header.set_xalign(0)
        vbox.append(header)

        vbox.append(Gtk.Separator())

        key_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        key_label = Gtk.Label(label="Combinacion:")
        key_label.set_xalign(0)
        key_box.append(key_label)
        key_entry = Gtk.Entry()
        key_entry.set_placeholder_text("Ej: Mod+Shift+X")
        key_box.append(key_entry)
        vbox.append(key_box)

        cmd_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        cmd_label = Gtk.Label(label="Comando o accion:")
        cmd_label.set_xalign(0)
        cmd_box.append(cmd_label)
        cmd_entry = Gtk.Entry()
        cmd_entry.set_placeholder_text("Ej: churros-settings o close-window")
        cmd_box.append(cmd_entry)
        vbox.append(cmd_box)

        args_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        args_label = Gtk.Label(label="Argumentos:")
        args_label.set_xalign(0)
        args_box.append(args_label)
        args_entry = Gtk.Entry()
        args_entry.set_placeholder_text("Opcional")
        args_box.append(args_entry)
        vbox.append(args_box)

        buttons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        buttons.set_halign(Gtk.Align.END)

        cancel_btn = Gtk.Button(label="Cancelar")
        cancel_btn.connect("clicked", lambda *_: dialog.close())
        buttons.append(cancel_btn)

        add_btn = Gtk.Button(label="Agregar")
        add_btn.add_css_class("suggested-action")

        def on_add(*_):
            new_key = key_entry.get_text().strip()
            new_cmd = cmd_entry.get_text().strip()

            if not new_key or not new_cmd:
                dialog.close()
                e = Gtk.AlertDialog()
                e.set_message("Define la combinacion y el comando")
                e.show()
                return

            new_args = args_entry.get_text().strip()

            action_type = "spawn"
            if new_cmd in [
                "close-window", "quit", "maximize-column", "fullscreen-window",
                "switch-preset-column-width", "toggle-window-floating",
                "focus-column-left", "focus-column-right", "focus-window-up", "focus-window-down",
                "move-column-left", "move-column-right", "move-window-up", "move-window-down",
                "show-hotkey-overlay", "toggle-overview", "screenshot",
                "screenshot-screen", "screenshot-window"
            ]:
                action_type = "builtin"

            ok = KeyboardService.add_keybind(new_key, action_type, new_cmd, new_args)
            dialog.close()

            if not ok:
                e = Gtk.AlertDialog()
                e.set_message("No se pudo agregar el atajo")
                e.show()
            else:
                GLib.idle_add(lambda: self._rebuild())

        add_btn.connect("clicked", on_add)
        buttons.append(add_btn)

        vbox.append(buttons)

        dialog.set_child(vbox)
        dialog.present()

    def _reload_binds(self):
        try:
            self.binds = KeyboardService.get_keybinds()
        except Exception:
            pass

    def _rebuild(self):
        content = self.content
        child = content.get_first_child()
        while child is not None:
            nxt = child.get_next_sibling()
            content.remove(child)
            child = nxt

        self._build()