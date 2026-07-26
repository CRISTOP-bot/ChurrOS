import os

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, Gdk, GLib, Gio

from widgets.page import Page
from widgets.group import Group
from widgets.row import Row

from services.wallpaper import WallpaperService


class WallpaperPage(Page):

    def __init__(self, navigator):

        super().__init__(
            navigator,
            "Fondos",
            "Selecciona un fondo de pantalla",
            parent_page="appearance"
        )

        self.navigator = navigator

        #
        # Botón "Importar..."
        #

        actions_group = Group("Importar fondo")
        actions_group.add(
            Row(
                title="Importar desde archivos...",
                subtitle="Elige una imagen de tu disco duro",
                icon="wallpaper.svg",
                callback=lambda *_: self.import_from_files()
            )
        )
        self.add(actions_group)

        #
        # Fondo actual + grid
        #

        current = WallpaperService.current()
        wallpapers = WallpaperService.available()

        if not wallpapers:

            group = Group("Fondos disponibles")
            group.add(
                Row(
                    title="No se encontraron fondos",
                    subtitle="Importa una imagen o añádela a ~/.local/share/churros/wallpapers",
                    icon="wallpaper.svg"
                )
            )
            self.add(group)
            return

        #
        # Miniatura del fondo actual
        #

        current_group = Group("Fondo actual")

        if current and os.path.exists(current):

            try:

                texture = Gdk.Texture.new_from_filename(current)
                preview = Gtk.Image.new_from_paintable(texture)
                preview.set_pixel_size(160)
                preview.add_css_class("wallpaper-preview")

                current_group.add(
                    Row(
                        title=os.path.splitext(
                            os.path.basename(current)
                        )[0],
                        subtitle="Seleccionado",
                        icon="wallpaper.svg"
                    )
                )

                self.add(current_group)

            except Exception:

                self.add(current_group)

        #
        # Grid de fondos
        #

        grid_group = Group("Fondos disponibles")

        flow = Gtk.FlowBox()
        flow.set_selection_mode(Gtk.SelectionMode.NONE)
        flow.set_max_children_per_line(4)
        flow.set_min_children_per_line(2)
        flow.set_row_spacing(12)
        flow.set_column_spacing(12)
        flow.set_halign(Gtk.Align.FILL)

        for wallpaper in wallpapers:

            thumb = self._build_thumbnail(
                wallpaper,
                current
            )

            flow.insert(thumb, -1)

        grid_group.add(flow)

        self.add(grid_group)

    def import_from_files(self):
        """Abre un dialogo nativo GTK4 para elegir una imagen y la copiar
        a la carpeta de wallpapers del usuario."""

        dialog = Gtk.FileDialog()
        dialog.set_title("Importar imagen de fondo")

        filter_any = Gtk.FileFilter()
        filter_any.set_name("Imagenes")
        filter_any.add_mime_type("image/jpeg")
        filter_any.add_mime_type("image/png")
        filter_any.add_mime_type("image/webp")
        filter_any.add_mime_type("image/gif")

        filters = Gio.ListStore.new(Gtk.FileFilter)
        filters.append(filter_any)
        dialog.set_filters(filters)

        try:
            dialog.set_initial_folder(Gio.File.new_for_path(os.path.expanduser("~")))
        except Exception:
            pass

        win = self.get_root()

        def on_result(source, result):

            try:

                file = dialog.open_finish(result)

                if file is None:
                    return

                src = file.get_path()

                dest = WallpaperService.import_image(src)

                if dest is None:
                    print("[wallpaper] no se pudo importar", src)
                    return

                WallpaperService.set(dest)

                # Recargar la pagina
                self._rebuild_grid()

            except GLib.Error as e:
                print("[wallpaper] import dialog cancelado:", e)
                return

        try:
            dialog.open(win, None, on_result, None)

        except Exception:
            # fallback sync en GTK muy viejo: Gtk.FileChooserDialog
            pass

    def _rebuild_grid(self):
        """Recarga todo el contenido de la pagina para mostrar la nueva imagen."""

        content = self.content
        child = content.get_first_child()
        while child is not None:
            nxt = child.get_next_sibling()
            content.remove(child)
            child = nxt

        # Re-construir (re-ejecutar la parte grafica del __init__)
        self._build_after_import()

    def _build_after_import(self):
        """Reconstruye los grupos tras importar un fondo nuevo."""

        actions_group = Group("Importar fondo")
        actions_group.add(
            Row(
                title="Importar desde archivos...",
                subtitle="Elige una imagen de tu disco duro",
                icon="wallpaper.svg",
                callback=lambda *_: self.import_from_files()
            )
        )
        self.add(actions_group)

        current = WallpaperService.current()
        wallpapers = WallpaperService.available()

        if not wallpapers:

            group = Group("Fondos disponibles")
            group.add(
                Row(
                    title="No se encontraron fondos",
                    subtitle="Importa una imagen",
                    icon="wallpaper.svg"
                )
            )
            self.add(group)
            return

        current_group = Group("Fondo actual")

        if current and os.path.exists(current):

            try:

                texture = Gdk.Texture.new_from_filename(current)
                preview = Gtk.Image.new_from_paintable(texture)
                preview.set_pixel_size(160)
                preview.add_css_class("wallpaper-preview")

                current_group.add(
                    Row(
                        title=os.path.splitext(
                            os.path.basename(current)
                        )[0],
                        subtitle="Seleccionado",
                        icon="wallpaper.svg"
                    )
                )

                self.add(current_group)

            except Exception:
                self.add(current_group)

        grid_group = Group("Fondos disponibles")
        flow = Gtk.FlowBox()
        flow.set_selection_mode(Gtk.SelectionMode.NONE)
        flow.set_max_children_per_line(4)
        flow.set_min_children_per_line(2)
        flow.set_row_spacing(12)
        flow.set_column_spacing(12)
        flow.set_halign(Gtk.Align.FILL)

        for wallpaper in wallpapers:

            thumb = self._build_thumbnail(wallpaper, current)
            flow.insert(thumb, -1)

        grid_group.add(flow)

        self.add(grid_group)

    def _build_thumbnail(self, wallpaper, current):

        box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=6
        )

        name = os.path.splitext(
            os.path.basename(wallpaper)
        )[0]

        is_current = (wallpaper == current)

        try:

            texture = Gdk.Texture.new_from_filename(wallpaper)
            image = Gtk.Image.new_from_paintable(texture)
            image.set_pixel_size(120)
            image.add_css_class("wallpaper-thumb")

            if is_current:
                image.add_css_class("wallpaper-selected")

        except Exception:

            image = Gtk.Image.new_from_icon_name("image-missing")
            image.set_pixel_size(120)

        button = Gtk.Button()
        button.set_child(image)
        button.add_css_class("wallpaper-button")
        button.set_has_frame(False)
        button.set_tooltip_text(name)
        button.connect(
            "clicked",
            lambda _, w=wallpaper: self.select(w)
        )

        label = Gtk.Label(label=name)
        label.add_css_class("wallpaper-name")
        label.set_max_width_chars(18)
        label.set_ellipsize(0)  # PANGO_ELLIPSIZE_END
        label.set_tooltip_text(name)

        box.append(button)
        box.append(label)

        return box

    def select(self, wallpaper):

        WallpaperService.set(wallpaper)

        GLib.idle_add(
            lambda: self.navigator.show_page("appearance")
        )
