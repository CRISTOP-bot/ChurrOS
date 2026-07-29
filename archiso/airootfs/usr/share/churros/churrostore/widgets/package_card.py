import os
import threading
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, GLib, Gdk


ICON_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "icons")


def _format_size(votes):

    if votes > 1000:
        return f"{votes / 1000:.1f}K"

    return str(votes)


def _format_rating(value):

    if value >= 80:
        return "Excelente"

    if value >= 60:
        return "Bueno"

    if value >= 40:
        return "Regular"

    if value > 0:
        return "Bajo"

    return "Sin reseñas"


class PackageCard(Gtk.Button):

    def __init__(self, package, callback=None, small=False):

        super().__init__()

        self.add_css_class("store-card")

        if small:
            self.add_css_class("store-card-small")

        self.set_has_frame(False)

        if small:
            self.set_size_request(180, 230)
        else:
            self.set_size_request(220, 290)

        self.package = package
        self.callback = callback

        box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=8
        )
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        box.set_margin_start(12)
        box.set_margin_end(12)

        icon_box = Gtk.Box()
        icon_box.set_size_request(96 if not small else 80,
                                 96 if not small else 80)
        icon_box.set_valign(Gtk.Align.CENTER)
        icon_box.set_halign(Gtk.Align.CENTER)
        icon_box.add_css_class("store-card-icon-box")

        self._image = Gtk.Image()

        if small:
            self._image.set_size_request(72, 72)
            self._image.set_pixel_size(72)
        else:
            self._image.set_size_request(96, 96)
            self._image.set_pixel_size(96)

        icon_box.append(self._image)
        self._set_placeholder_icon()

        if package.get("installed"):
            install_badge = Gtk.Label(label="INSTALADO")
            install_badge.add_css_class("store-card-installed")
            icon_box.add_css_class("store-card-icon-installed")
            overlay = Gtk.Overlay()
            overlay.set_child(icon_box)
            overlay.add_overlay(install_badge)
            box.append(overlay)
        else:
            box.append(icon_box)

        name = Gtk.Label(label=package.get("name", ""))
        name.set_xalign(0)
        name.set_yalign(0)
        name.add_css_class("store-card-name")
        name.set_ellipsize(3)
        name.set_max_width_chars(22 if not small else 18)
        name.set_tooltip_text(package.get("name", ""))

        box.append(name)

        source = Gtk.Label(label=package.get("source", ""))
        source.set_xalign(0)
        source.add_css_class("store-card-source")

        box.append(source)

        votes = package.get("votes", 0)

        if votes or package.get("popularity"):

            meta = Gtk.Box(
                orientation=Gtk.Orientation.HORIZONTAL,
                spacing=8
            )
            meta.set_halign(Gtk.Align.START)
            meta.set_margin_top(2)

            stars_box = Gtk.Box(
                orientation=Gtk.Orientation.HORIZONTAL,
                spacing=2
            )

            full = min(5, int(votes / 200))
            fraction = (votes / 200) - full

            for i in range(5):

                if i < full:
                    star = Gtk.Image.new_from_file(
                        os.path.join(ICON_DIR, "star.svg")
                    )
                elif i == full and fraction > 0.4:
                    star = Gtk.Image.new_from_file(
                        os.path.join(ICON_DIR, "half-star.svg")
                    )
                else:
                    star = Gtk.Image.new_from_icon_name("non-starred-symbolic")
                    star.set_icon_size(Gtk.IconSize.INHERIT)

                star.set_pixel_size(10)
                stars_box.append(star)

            meta.append(stars_box)

            votes_label = Gtk.Label(label=_format_size(votes))
            votes_label.add_css_class("store-card-votes")
            meta.append(votes_label)

            box.append(meta)

        if not small:

            desc = Gtk.Label(label=package.get("description", ""))
            desc.set_xalign(0)
            desc.set_yalign(0)
            desc.set_wrap(True)
            desc.set_wrap_mode(2)
            desc.set_max_width_chars(26)
            desc.set_lines(3)
            desc.set_ellipsize(3)
            desc.add_css_class("store-card-desc")
            desc.set_vexpand(True)

            box.append(desc)

            get_btn = Gtk.Button.new_with_label("Obtener")
            get_btn.add_css_class("store-card-get")
            get_btn.set_halign(Gtk.Align.CENTER)
            get_btn.set_size_request(-1, 28)

            if package.get("installed"):
                get_btn.set_label("Instalado")
                get_btn.set_sensitive(False)

            get_btn.connect("clicked", lambda *_: self._on_get_clicked())

            box.append(get_btn)

        self.set_child(box)

        self.connect("clicked", self._on_click)

        icon_url = package.get("icon", "")
        if icon_url:
            self._load_remote_icon(icon_url)

    def _set_placeholder_icon(self):

        icon_path = os.path.join(ICON_DIR, "store.svg")

        if os.path.exists(icon_path):
            self._image.set_from_file(icon_path)
        else:
            self._image.set_from_icon_name("package-x-generic-symbolic")

        if not self.package.get("icon"):
            self._image.set_pixel_size(56 if not self.has_css_class("store-card-small") else 48)

    def _load_remote_icon(self, url):

        def worker():

            try:

                import urllib.request

                with urllib.request.urlopen(url, timeout=8) as r:
                    data = r.read()

                GLib.idle_add(self._apply_icon, data)

            except Exception:
                pass

        threading.Thread(target=worker, daemon=True).start()

    def _apply_icon(self, data):

        try:
            texture = Gdk.Texture.new_from_bytes(GLib.Bytes.new(data))
            self._image.set_from_paintable(texture)
            self._image.set_pixel_size(-1)
            self._image.set_size_request(96, 96)
        except Exception:
            pass

        return False

    def _on_click(self, *_):

        if self.callback:
            self.callback(self.package)

    def _on_get_clicked(self):

        if self.callback:
            self.callback(self.package)
