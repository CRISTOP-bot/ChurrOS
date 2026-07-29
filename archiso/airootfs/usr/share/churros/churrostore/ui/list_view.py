import os
import sys
import threading

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PREF = os.path.abspath(os.path.join(ROOT, "..", "preferences"))

sys.path.insert(0, ROOT)
sys.path.insert(0, PREF)

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GLib

from services.store import StoreService

from widgets.package_card import PackageCard
from widgets.featured_card import FeaturedCard


CATEGORY_PROFILES = {
    "apps": {
        "title":     "Apps",
        "subtitle":  "Mensajeria, navegadores, editores y mas",
        "keywords":  [
            "browser", "firefox", "chrome", "chromium", "brave",
            "telegram", "discord", "whatsapp", "signal", "chat", "messenger",
            "mail", "thunderbird", "evolution",
            "code", "visual", "vscodium", "sublime", "atom", "emacs", "neovim",
            "terminal", "foot", "konsole", "alacritty", "tilix",
            "notes", "obsidian", "logseq", "standard",
            "image", "viewer", "photo", "shot", "screenshot",
            "reader", "pdf", "epub", "ebook",
            "audio", "video", "player", "music", "media",
            "sound", "podcast",
        ],
    },

    "games": {
        "title":     "Juegos",
        "subtitle":  "Steam, emuladores y juegos nativos",
        "keywords":  [
            "game", "play", "rpg", "strategy", "shooter", "adventure",
            "steam", "lutris", "heroic", "bottles",
            "emulator", "emulation",
            "minecraft", "minetest", "terraria",
            "godot", "unity", "unreal",
            "wine", "proton", "playstation", "xbox", "nintendo",
            "snes", "nes", "gba", "psp", "nds",
            "0ad", "wesnoth", "frozen-bubble", "supertuxkart",
        ],
    },

    "productivity": {
        "title":     "Productividad",
        "subtitle":  "Oficina, tareas, calendario y notas",
        "keywords":  [
            "office", "libreoffice", "libre", "calligra",
            "notes", "note", "task", "todo", "kanban",
            "calendar", "cal", "khal",
            "password", "passwd", "vault", "keepass", "bitwarden",
            "finance", "money", "gnucash",
            "pdf", "ocr", "scan",
            "time", "tracker", "toggl", "hamster",
            "rss", "reader", "feed",
        ],
    },

    "creativity": {
        "title":     "Creatividad",
        "subtitle":  "Edicion de imagen, video, audio y 3D",
        "keywords":  [
            "gimp", "inkscape", "krita", "mypaint", "drawing", "paint",
            "blender", "freecad", "sculpt", "model", "3d",
            "darktable", "rawtherapee", "photivo",
            "kdenlive", "shotcut", "pitivi", "openshot", "olive", "flowblade",
            "audacity", "ardour", "lmms", "musescore", "qtractor",
            "obs", "studio", "broadcast",
            "font", "design", "figma",
        ],
    },

    "tools": {
        "title":     "Herramientas",
        "subtitle":  "Sistema, terminal y utilidades",
        "keywords":  [
            "system", "utility", "tool", "manager", "monitor",
            "terminal", "shell", "bash", "fish", "zsh",
            "file", "files", "filemanager", "thunar", "nemo", "nautilus",
            "htop", "btop", "top", "process",
            "archive", "extract", "zip", "tar", "7z", "compress",
            "vpn", "tor", "proxy", "network",
            "git", "docker", "kubectl", "ansible", "container",
            "backup", "sync", "borg", "restic", "rsync",
            "partition", "gparted", "disk", "boot", "grub",
            "config", "settings", "preferences", "control",
            "log", "analyzer", "debug",
        ],
    },
}


def _category_match(pkg, keywords):

    if not keywords:
        return True

    text = " ".join([
        pkg.get("name", ""),
        pkg.get("description", "") or "",
        pkg.get("summary", "") or "",
        pkg.get("id", ""),
        pkg.get("developer", "") or "",
        pkg.get("maintainer", "") or "",
    ]).lower()

    matches = 0

    for keyword in keywords:
        if keyword in text:
            matches += 1

    return matches >= 1


class ListView(Gtk.Box):

    def __init__(self, parent_window, query="", source="all", category="discover"):

        super().__init__(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=0
        )
        self.add_css_class("store-list")

        self.parent_window = parent_window
        self.query = query
        self.source = source
        self.category = category
        self.packages = []

        self._build_scaffold()

        self.refresh()

    def _build_scaffold(self):

        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(
            Gtk.PolicyType.NEVER,
            Gtk.PolicyType.AUTOMATIC
        )
        scroller.set_vexpand(True)
        scroller.set_hexpand(True)
        self.append(scroller)

        self.content = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=24
        )
        self.content.set_margin_top(20)
        self.content.set_margin_bottom(40)
        self.content.set_margin_start(28)
        self.content.set_margin_end(28)

        scroller.set_child(self.content)

        self.spinner = Gtk.Spinner()
        self.spinner.set_halign(Gtk.Align.CENTER)
        self.spinner.set_valign(Gtk.Align.CENTER)
        self.spinner.set_margin_top(40)
        self.append(self.spinner)

    def _clear(self):

        child = self.content.get_first_child()
        while child is not None:
            nxt = child.get_next_sibling()
            self.content.remove(child)
            child = nxt

    def set_category(self, category, query=None):

        if query is not None:
            self.query = query

        self.category = category

        self.refresh()

    def refresh(self):

        self.spinner.start()

        cat = self.category
        query = self.query
        source = self.source

        def worker():

            packages = []

            try:

                if cat == "installed":
                    installed = StoreService.installed()

                    for pkg_id, info in installed.items():

                        packages.append({
                            "id": pkg_id,
                            "name": info.get("name", pkg_id.split(":", 1)[-1]),
                            "version": info.get("version", ""),
                            "description": info.get("description", ""),
                            "icon": info.get("icon", ""),
                            "source": pkg_id.split(":", 1)[0],
                            "installed": True,
                        })

                else:

                    results = StoreService.search(query, source)

                    if cat in CATEGORY_PROFILES:
                        keywords = CATEGORY_PROFILES[cat]["keywords"]

                        for pkg in results:
                            if _category_match(pkg, keywords):
                                packages.append(pkg)

                    elif cat == "discover":
                        packages = results

                    elif cat == "updates":
                        packages = results

                    else:
                        packages = results

            except Exception as exc:
                packages = []
                print("[list_view] worker error:", exc)

            GLib.idle_add(self._populate, cat, query, packages)

        threading.Thread(target=worker, daemon=True).start()

    def _populate(self, cat, query, packages):

        self.spinner.stop()

        self._clear()

        if not packages:

            empty = Gtk.Label(label="Sin resultados")
            empty.add_css_class("store-empty")
            self.content.append(empty)
            return

        if cat == "discover" and not query:

            self._render_hero(packages)

            installed_pkgs = []
            featured_pkgs = []

            for pkg in packages:

                if pkg.get("installed"):
                    installed_pkgs.append(pkg)
                elif pkg.get("featured"):
                    featured_pkgs.append(pkg)

            if installed_pkgs:

                self._render_section(
                    "Tus apps",
                    installed_pkgs[:12],
                    horizontal=True,
                    small=True
                )

            if featured_pkgs:

                self._render_section(
                    "Apps destacadas",
                    featured_pkgs[:12],
                    horizontal=True,
                    small=True
                )

            others = [
                p for p in packages
                if not p.get("installed") and not p.get("featured")
            ]

            if others:

                self._render_section(
                    "Explorar todo",
                    others[:60],
                    horizontal=False
                )

        elif cat == "installed":

            self._render_section(
                "Instalados",
                packages,
                horizontal=False
            )

        elif cat in CATEGORY_PROFILES:

            profile = CATEGORY_PROFILES[cat]
            title = profile["title"]

            self._render_section(
                title,
                packages,
                horizontal=False
            )

        else:

            title = query or cat.title()

            self._render_section(
                f"Resultados para {query!r}" if query else title,
                packages,
                horizontal=False
            )

    def _render_hero(self, packages):

        hero_pkg = None

        for pkg in packages:
            if not pkg.get("installed") and pkg.get("featured"):
                hero_pkg = pkg
                break

        if hero_pkg is None:
            return

        hero = FeaturedCard(hero_pkg, callback=lambda p: self.parent_window.show_detail(p))
        hero.add_css_class("store-hero")

        self.content.append(hero)

    def _render_section(self, title, packages, horizontal=False, small=False):

        section = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=12
        )

        header = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=8
        )

        title_label = Gtk.Label(label=title)
        title_label.set_xalign(0)
        title_label.add_css_class("store-section-title")

        header.append(title_label)

        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        header.append(spacer)

        count = Gtk.Label(label=f"{len(packages)} apps")
        count.add_css_class("store-section-count")
        header.append(count)

        section.append(header)

        if horizontal:

            scroller = Gtk.ScrolledWindow()
            scroller.set_policy(
                Gtk.PolicyType.AUTOMATIC,
                Gtk.PolicyType.NEVER
            )
            scroller.set_propagate_natural_height(True)
            scroller.set_min_content_height(small and 230 or 290)

            flow = Gtk.Box(
                orientation=Gtk.Orientation.HORIZONTAL,
                spacing=14
            )

            for pkg in packages:
                card = PackageCard(
                    pkg,
                    callback=lambda p, _w=self.parent_window: _w.show_detail(p),
                    small=small
                )
                flow.append(card)

            scroller.set_child(flow)
            section.append(scroller)

        else:

            grid = Gtk.FlowBox()
            grid.set_selection_mode(Gtk.SelectionMode.NONE)
            grid.set_max_children_per_line(5)
            grid.set_min_children_per_line(2)
            grid.set_row_spacing(14)
            grid.set_column_spacing(14)
            grid.set_halign(Gtk.Align.START)
            grid.set_valign(Gtk.Align.START)

            for pkg in packages:
                card = PackageCard(
                    pkg,
                    callback=lambda p, _w=self.parent_window: _w.show_detail(p),
                    small=small
                )
                grid.insert(card, -1)

            section.append(grid)

        self.content.append(section)
