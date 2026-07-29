import os
import sys
import threading

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PREF = os.path.abspath(os.path.join(ROOT, "..", "preferences"))

sys.path.insert(0, ROOT)
sys.path.insert(0, PREF)

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GLib, Gdk

from services.store import StoreService


ICON_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "icons")


class DetailView(Gtk.Box):

    def __init__(self, parent_window, package, on_back):

        super().__init__(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=0
        )
        self.add_css_class("store-detail")

        self.parent_window = parent_window
        self.package = package
        self.on_back = on_back

        self._build()

        self._load_info()

    def _build(self):

        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(
            Gtk.PolicyType.NEVER,
            Gtk.PolicyType.AUTOMATIC
        )
        scroller.set_vexpand(True)
        scroller.set_hexpand(True)
        self.append(scroller)

        body = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=0
        )
        scroller.set_child(body)

        body.append(self._build_top_bar())

        content = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=32
        )
        content.set_margin_top(24)
        content.set_margin_bottom(40)
        content.set_margin_start(36)
        content.set_margin_end(36)

        body.append(content)

        main = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=18
        )
        main.set_hexpand(True)
        main.set_halign(Gtk.Align.START)
        main.set_size_request(500, -1)

        main.append(self._build_main_section())

        content.append(main)

        sidebar = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=18
        )
        sidebar.set_size_request(280, -1)

        sidebar.append(self._build_sidebar())

        content.append(sidebar)

    def _build_top_bar(self):

        bar = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=10
        )
        bar.add_css_class("store-detail-top-bar")

        back_btn = Gtk.Button.new_from_icon_name("go-previous-symbolic")
        back_btn.set_label(" Volver")
        back_btn.add_css_class("store-detail-back-button")
        back_btn.connect("clicked", lambda *_: self.on_back())

        bar.append(back_btn)

        bar.append(Gtk.Box())  # spacer

        status = Gtk.Label(label="Cargando...")
        status.add_css_class("store-detail-status")

        self.status_label = status
        bar.append(status)

        install_btn = Gtk.Button.new_with_label("Obtener")
        install_btn.add_css_class("suggested-action")
        install_btn.connect("clicked", lambda *_: self._install())

        self.install_btn = install_btn
        bar.append(install_btn)

        remove_btn = Gtk.Button.new_with_label("Desinstalar")
        remove_btn.add_css_class("destructive-action")
        remove_btn.connect("clicked", lambda *_: self._remove())

        self.remove_btn = remove_btn
        bar.append(remove_btn)

        return bar

    def _build_main_section(self):

        box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=24
        )
        box.set_margin_bottom(12)

        icon_box = Gtk.Box()
        icon_box.set_size_request(180, 180)
        icon_box.set_valign(Gtk.Align.START)
        icon_box.set_halign(Gtk.Align.START)
        icon_box.add_css_class("store-detail-icon-box")

        self._image = Gtk.Image()
        self._image.set_size_request(160, 160)
        self._image.set_pixel_size(160)
        self._image_box = icon_box
        self._image_box.append(self._image)
        self._set_placeholder_icon()

        icon_url = self.package.get("icon", "")
        if icon_url:
            self._load_remote_icon(icon_url)

        box.append(self._image_box)

        info = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=6
        )
        info.set_hexpand(True)

        source = Gtk.Label(label=self.package.get("id", ""))
        source.set_xalign(0)
        source.add_css_class("store-detail-source")
        info.append(source)

        name = Gtk.Label(label=self.package.get("name", ""))
        name.set_xalign(0)
        name.set_yalign(0)
        name.add_css_class("store-detail-name")
        name.set_wrap(True)
        name.set_wrap_mode(2)
        info.append(name)

        version = Gtk.Label(label=("v " + self.package["version"]) if self.package.get("version") else "")
        version.set_xalign(0)
        version.add_css_class("store-detail-version")
        info.append(version)

        box.append(info)

        return box

    def _build_sidebar(self):

        box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=14
        )

        section_title = Gtk.Label(label="Informacion")
        section_title.set_xalign(0)
        section_title.add_css_class("store-detail-section-title")
        box.append(section_title)

        self._info_grid = Gtk.Grid()
        self._info_grid.set_column_spacing(12)
        self._info_grid.set_row_spacing(10)
        self._info_grid.add_css_class("store-detail-info-grid")

        box.append(self._info_grid)

        section_title = Gtk.Label(label="Capturas")
        section_title.set_xalign(0)
        section_title.add_css_class("store-detail-section-title")
        section_title.set_margin_top(8)
        box.append(section_title)

        self._screenshots_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=8
        )
        self._screenshots_box.set_halign(Gtk.Align.START)

        box.append(self._screenshots_box)

        section_title = Gtk.Label(label="Descripcion")
        section_title.set_xalign(0)
        section_title.add_css_class("store-detail-section-title")
        section_title.set_margin_top(8)
        box.append(section_title)

        self.desc_label = Gtk.Label(label="Cargando descripcion...")
        self.desc_label.set_xalign(0)
        self.desc_label.set_yalign(0)
        self.desc_label.set_wrap(True)
        self.desc_label.set_wrap_mode(2)
        self.desc_label.add_css_class("store-detail-description")
        box.append(self.desc_label)

        return box

    def _pretty_key(self, key):

        return {
            "version":       "Version",
            "developer":     "Desarrollador",
            "license":       "Licencia",
            "repository":    "Repositorio",
            "installed_size":"Instalado",
            "download_size": "Descarga",
            "homepage":      "Sitio web",
            "maintainer":    "Mantenedor",
            "votes":         "Votos",
            "popularity":    "Popularidad",
            "categories":    "Categorias",
        }.get(key, key.replace("_", " ").title())

    def _refresh_actions(self):

        package_id = self.package.get("id", "")
        is_installed = StoreService.is_installed(package_id)

        if is_installed:
            self.install_btn.set_label("Instalado")
            self.install_btn.set_sensitive(False)
            self.remove_btn.set_visible(True)
            self.status_label.set_label("INSTALADO")
        else:
            self.install_btn.set_label("Obtener")
            self.install_btn.set_sensitive(True)
            self.remove_btn.set_visible(False)
            self.status_label.set_label("Disponible")

    def _set_info_rows(self, info):

        child = self._info_grid.get_first_child()
        while child is not None:
            nxt = child.get_next_sibling()
            self._info_grid.remove(child)
            child = nxt

        keys = [
            "version", "developer", "maintainer", "votes", "popularity",
            "license", "repository", "installed_size", "download_size", "homepage",
        ]

        row_idx = 0

        for key in keys:

            val = info.get(key, "")

            if val == "" or val is None:
                continue

            if isinstance(val, list):
                val = ", ".join(str(v) for v in val)

            label_widget = Gtk.Label(label=self._pretty_key(key))
            label_widget.set_xalign(0)
            label_widget.add_css_class("store-detail-info-key")

            value_widget = Gtk.Label(label=str(val))
            value_widget.set_xalign(0)
            value_widget.set_hexpand(True)
            value_widget.set_halign(Gtk.Align.START)
            value_widget.add_css_class("store-detail-info-value")
            value_widget.set_wrap(True)
            value_widget.set_wrap_mode(2)
            value_widget.set_selectable(True)

            self._info_grid.attach(label_widget, 0, row_idx, 1, 1)
            self._info_grid.attach(value_widget, 1, row_idx, 1, 1)

            row_idx += 1

    def _set_placeholder_icon(self):

        icon_path = os.path.join(ICON_DIR, "store.svg")

        if os.path.exists(icon_path):
            self._image.set_from_file(icon_path)
        else:
            self._image.set_from_icon_name("package-x-generic-symbolic")

    def _load_remote_icon(self, url):

        def worker():

            try:

                import urllib.request

                with urllib.request.urlopen(url, timeout=8) as r:
                    data = r.read()

                GLib.idle_add(self._apply_remote_icon, data)

            except Exception:
                pass

        threading.Thread(target=worker, daemon=True).start()

    def _apply_remote_icon(self, data):

        try:
            texture = Gdk.Texture.new_from_bytes(GLib.Bytes.new(data))
            self._image.set_from_paintable(texture)
            self._image.set_pixel_size(-1)
            self._image.set_size_request(160, 160)
        except Exception:
            pass

        return False

    def _load_info(self):

        package_id = self.package.get("id", "")

        def worker():

            info = StoreService.info(package_id)

            if info:
                GLib.idle_add(self._apply_info, info)

        threading.Thread(target=worker, daemon=True).start()

    def _apply_info(self, info):

        if info.get("description"):
            self.desc_label.set_label(info["description"])

        if info.get("version"):
            self.package["version"] = info["version"]

        self._set_info_rows(info)

        for shot_url in info.get("screenshots", []) or []:

            try:

                img = Gtk.Picture()
                img.set_size_request(180, 110)
                img.add_css_class("store-detail-screenshot")

                img.set_paintable(
                    Gtk.Image.new_from_icon_name(
                        "image-loading-symbolic"
                    ).get_paintable()
                )

                self._screenshots_box.append(img)

                self._load_screenshot(img, shot_url)

            except Exception:
                continue

    def _load_screenshot(self, picture, url):

        def worker():

            try:

                import urllib.request

                with urllib.request.urlopen(url, timeout=10) as r:
                    data = r.read()

                GLib.idle_add(self._apply_screenshot, picture, data)

            except Exception:
                pass

        threading.Thread(target=worker, daemon=True).start()

    def _apply_screenshot(self, picture, data):

        try:
            texture = Gdk.Texture.new_from_bytes(GLib.Bytes.new(data))
            picture.set_paintable(texture)
        except Exception:
            pass

        return False

    def _install(self):

        self._set_busy(True)

        def done(ok, message):
            GLib.idle_add(self._after_action, ok, message)

        StoreService.install(self.package.get("id", ""), done)

    def _remove(self):

        self._set_busy(True)

        def done(ok, message):
            GLib.idle_add(self._after_action, ok, message)

        StoreService.remove(self.package.get("id", ""), done)

    def _after_action(self, ok, message):

        self._set_busy(False)
        self._refresh_actions()
        self.status_label.set_label(message if ok else f"Error: {message}")
        return False

    def _set_busy(self, busy):

        self.install_btn.set_sensitive(not busy)
        self.remove_btn.set_sensitive(not busy)
