from gi.repository import Gtk

from widgets.action_card import ActionCard
from widgets.system_card import SystemCard

from utils.browser import (
    open_discord,
    open_repository,
)
from utils.desktop import (
    launch_installer,
    open_terminal,
    open_browser,
)


# =====================================
# Callbacks
# =====================================

def github_clicked(button):
    open_repository()

def discord_clicked(button):
    open_discord()

def install_clicked(button):

    window = button.get_root()

    launch_installer(parent_window=window)

def docs_clicked(button):
    from utils.browser import open_wiki
    open_wiki()

def terminal_clicked(button):
    open_terminal()

def browser_clicked(button):
    open_browser()


# =====================================
# Tarjetas
# =====================================

CARDS = [
    {
        "icon": "install.svg",
        "title": "Install ChurrOS",
        "description": "Instala ChurrOS en tu disco duro.",
        "callback": install_clicked,
    },
    {
        "icon": "github.svg",
        "title": "GitHub",
        "description": "Repositorio oficial del proyecto.",
        "callback": github_clicked,
    },
    {
        "icon": "community.svg",
        "title": "Discord",
        "description": "Únete a la comunidad de ChurrOS.",
        "callback": discord_clicked,
    },
    {
        "icon": "documentation.svg",
        "title": "Documentation",
        "description": "Lee la documentación del proyecto.",
        "callback": docs_clicked,
    },
    {
        "icon": "terminal.svg",
        "title": "Terminal",
        "description": "Abre una terminal de comandos.",
        "callback": terminal_clicked,
    },
    {
        "icon": "browser.svg",
        "title": "Browser",
        "description": "Abre el navegador web.",
        "callback": browser_clicked,
    },
]


# =====================================
# Construcción
# =====================================

def build_cards():

    flow = Gtk.FlowBox()

    flow.set_selection_mode(Gtk.SelectionMode.NONE)

    flow.set_max_children_per_line(4)

    flow.set_min_children_per_line(1)
    flow.set_row_spacing(20)
    flow.set_column_spacing(20)
    flow.set_halign(Gtk.Align.CENTER)

    flow.insert(SystemCard(), -1)

    for card in CARDS:

        flow.insert(

            ActionCard(

                icon_name=card["icon"],

                title=card["title"],

                description=card["description"],

                callback=card["callback"],

            ),

            -1,

        )

    return flow
