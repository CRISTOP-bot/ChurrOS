import sys
import os
import threading

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PREF = os.path.abspath(os.path.join(ROOT, "preferences"))

sys.path.insert(0, ROOT)
sys.path.insert(0, PREF)

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GLib, Gio

from widgets.page import Page
from widgets.group import Group
from widgets.row import Row

from services.backup_service import BackupService


class BackupPage(Page):

    def __init__(self, navigator):

        super().__init__(
            navigator,
            "Copia de seguridad",
            "Exporta, importa o restablece la configuracion de ChurrOS",
            parent_page="system"
        )

        self._build()

    def _build(self):

        #
        # Exportar
        #

        export_group = Group("Exportar")

        export_row = Row(
            title="Exportar configuracion",
            subtitle="Empaqueta ajustes y dotfiles en un archivo .tar",
            icon="backup.svg",
            callback=lambda *_: self._on_export()
        )

        export_group.add(export_row)

        self.add(export_group)

        #
        # Importar
        #

        import_group = Group("Importar")

        import_row = Row(
            title="Importar configuracion",
            subtitle="Restaurar desde un backup de ChurrOS (.tar)",
            icon="backup.svg",
            callback=lambda *_: self._on_import()
        )

        import_group.add(import_row)

        self.add(import_group)

        #
        # Restablecer
        #

        reset_group = Group("Restablecer")

        reset_row = Row(
            title="Restablecer a valores de fabrica",
            subtitle="Borra tus cambios y restaura los defaults de ChurrOS",
            icon="backup.svg",
            callback=lambda *_: self._on_reset()
        )

        reset_group.add(reset_row)

        self.add(reset_group)

        #
        # Estado
        #

        status_group = Group("Estado")

        self._status_label = Gtk.Label(
            label="Listo."
        )
        self._status_label.set_xalign(0)
        self._status_label.set_wrap(True)
        self._status_label.add_css_class("row-subtitle")
        self._status_label.set_margin_start(14)
        self._status_label.set_margin_end(14)
        self._status_label.set_margin_top(10)
        self._status_label.set_margin_bottom(10)

        status_group.add(self._status_label)

        self.add(status_group)

    def _set_status(self, msg):

        self._status_label.set_label(msg)

    def _on_export(self):

        dialog = Gtk.FileDialog()
        dialog.set_title("Guardar backup")

        filter_tar = Gtk.FileFilter()
        filter_tar.set_name("Archivo tar")
        filter_tar.add_pattern("*.tar")
        filter_tar.add_pattern("*.tar.gz")
        filter_tar.add_pattern("*.tar.zst")

        filters = Gio.ListStore.new(Gtk.FileFilter)
        filters.append(filter_tar)
        dialog.set_filters(filters)
        dialog.set_default_filter(filter_tar)

        try:

            dialog.set_initial_name(
                "churros-backup.tar"
            )

            dialog.set_initial_folder(
                Gio.File.new_for_path(
                    os.path.expanduser("~")
                )
            )

        except Exception:
            pass

        def on_result(source, result, _user_data=None):

            try:

                file = dialog.save_finish(result)

            except GLib.Error:
                return

            if file is None:
                return

            path = file.get_path() if hasattr(file, "get_path") else None

            if not path:
                return

            self._set_status("Exportando...")

            def worker():

                try:

                    BackupService.export_to(path)

                    GLib.idle_add(
                        lambda: self._set_status(
                            "Backup guardado en " + path
                        )
                    )

                except Exception as exc:

                    GLib.idle_add(
                        lambda: self._set_status(
                            "Error al exportar: " + str(exc)
                        )
                    )


            threading.Thread(
                target=worker,
                daemon=True
            ).start()

        dialog.save(self.get_root(), None, on_result)

    def _on_import(self):

        dialog = Gtk.FileDialog()
        dialog.set_title("Seleccionar backup de ChurrOS")

        filter_tar = Gtk.FileFilter()
        filter_tar.set_name("Archivo tar")
        filter_tar.add_pattern("*.tar")
        filter_tar.add_pattern("*.tar.gz")
        filter_tar.add_pattern("*.tar.zst")

        filters = Gio.ListStore.new(Gtk.FileFilter)
        filters.append(filter_tar)
        dialog.set_filters(filters)
        dialog.set_default_filter(filter_tar)

        try:

            dialog.set_initial_folder(
                Gio.File.new_for_path(
                    os.path.expanduser("~")
                )
            )

        except Exception:
            pass

        def on_result(source, result, _user_data=None):

            try:

                file = dialog.open_finish(result)

            except GLib.Error:
                return

            if file is None:
                return

            path = file.get_path() if hasattr(file, "get_path") else None

            if not path or not os.path.isfile(path):
                return

            self._set_status("Importando... recargando tras aplicar")

            confirm = Gtk.AlertDialog()
            confirm.set_heading("Importar configuracion")
            confirm.set_message(
                "Esto reemplazara tu configuracion actual "
                "con la del archivo. ¿Continuar?"
            )
            confirm.set_modal(True)
            confirm.set_buttons(["Cancelar", "Importar"])

            def on_confirm(d, r):

                try:
                    response = d.choose_finish(r)
                except Exception:
                    return

                if response != 1:
                    return

                def worker():

                    try:

                        BackupService.import_from(path)

                        GLib.idle_add(
                            lambda: self._set_status(
                                "Configuracion importada."
                                " Reinicia las apps para ver todos"
                                " los cambios."
                            )
                        )

                    except Exception as exc:

                        GLib.idle_add(
                            lambda: self._set_status(
                                "Error al importar: " + str(exc)
                            )
                        )

                threading.Thread(
                    target=worker,
                    daemon=True
                ).start()

            confirm.choose(self.get_root(), None, on_confirm)

        dialog.open(self.get_root(), None, on_result)

    def _on_reset(self):

        dialog = Gtk.AlertDialog()
        dialog.set_heading("Restablecer a valores de fabrica")
        dialog.set_message(
            "Se borraran tus ajustes personales (tema, wallpaper, "
            "tipografia, dotfiles de niri/foot/fuzzel/mako/waybar) "
            "y se restauraran los defaults de ChurrOS. ¿Continuar?"
        )
        dialog.set_modal(True)
        dialog.set_buttons(["Cancelar", "Restablecer"])

        def on_response(d, result):

            try:
                response = d.choose_finish(result)
            except Exception:
                return

            if response != 1:
                return

            self._set_status("Restableciendo...")

            def worker():

                try:

                    BackupService.reset_to_defaults()

                    GLib.idle_add(
                        lambda: self._set_status(
                            "Configuraciones restablecidas a defaults. "
                            "Reinicia las apps para ver todos los cambios."
                        )
                    )

                except Exception as exc:

                    GLib.idle_add(
                        lambda: self._set_status(
                            "Error al restablecer: " + str(exc)
                        )
                    )


            threading.Thread(
                target=worker,
                daemon=True
            ).start()

        dialog.choose(self.get_root(), None, on_response)
