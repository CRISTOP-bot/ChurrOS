import os
import threading
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, GLib, Gdk


ICON_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "icons")


class FeaturedCard(Gtk.Button):

    def __init__(self, package, callback=None):

        super().__init__()

        self.set_has_frame(False)
        self.add_css_class("store-featured-card")
        self.set_size_request(-1, 280)

        self.package = package
        self.callback = callback

        outer = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=0
        )

        cover = Gtk.Box()
        cover.set_size_request(260, 260)
        cover.set_valign(Gtk.Align.CENTER)
        cover.set_halign(Gtk.Align.CENTER)
        cover.set_margin_start(20)
        cover.set_margin_end(10)
        cover.set_margin_top(10)
        cover.set_margin_bottom(10)
        cover.add_css_class("store-featured-cover")

        self.cover_image = Gtk.Image()
        self.cover_image.set_size_request(220, 220)
        self.cover_image.set_pixel_size(220)

        self._set_placeholder_cover(cover, self.cover_image)
        cover.append(self.cover_image)
        outer.append(cover)

        info = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=10
        )
        info.set_valign(Gtk.Align.CENTER)
        info.set_halign(Gtk.Align.START)
        info.set_margin_start(16)
        info.set_margin_end(24)
        info.set_margin_top(16)
        info.set_margin_bottom(16)
        info.set_hexpand(True)

        badge = Gtk.Label(label="Destacado de hoy")
        badge.set_xalign(0)
        badge.add_css_class("store-featured-badge")

        info.append(badge)

        name = Gtk.Label(label=package.get("name", ""))
        name.set_xalign(0)
        name.set_yalign(0)
        name.add_css_class("store-featured-name")
        name.set_wrap(True)
        name.set_wrap_mode(2)
        name.set_lines(2)
        info.append(name)

        desc = Gtk.Label(label=package.get("description", ""))
        desc.set_xalign(0)
        desc.set_yalign(0)
        desc.set_wrap(True)
        desc.set_wrap_mode(2)
        desc.set_lines(3)
        desc.set_ellipsize(3)
        desc.add_css_class("store-featured-desc")
        info.append(desc)

        meta = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=12
        )
        meta.set_margin_top(8)

        source = Gtk.Label(label=package.get("source", ""))
        source.add_css_class("store-featured-source")

        meta.append(source)

        if package.get("version"):
            v = Gtk.Label(label=f"v {package['version']}")
            v.add_css_class("store-featured-version")
            meta.append(v)

        info.append(meta)

        outer.append(info)

        self.set_child(outer)

        self.connect("clicked", self._on_click)

        icon_url = package.get("icon", "")
        if icon_url:
            self._load_cover(icon_url)

    def _set_placeholder_cover(self, box, image):

        icon_path = os.path.join(ICON_DIR, "store.svg")

        if os.path.exists(icon_path):
            image.set_from_file(icon_path)
        else:
            image.set_from_icon_name("package-x-generic-symbolic")

    def _load_cover(self, url):

        def worker():

            try:

                import urllib.request

                with urllib.request.urlopen(url, timeout=8) as r:
                    data = r.read()

                GLib.idle_add(self._apply_cover, data)

            except Exception:
                pass

        threading.Thread(target=worker, daemon=True).start()

    def _apply_cover(self, data):

        try:
            texture = Gdk.Texture.new_from_bytes(GLib.Bytes.new(data))
            self.cover_image.set_from_paintable(texture)
            self.cover_image.set_pixel_size(-1)
            self.cover_image.set_size_request(220, 220)
        except Exception:
            pass

        return False

    def _on_click(self, *_):

        if self.callback:
            self.callback(self.package)
