import os

from widgets.page import Page
from widgets.group import Group
from widgets.row import Row

from services.wallpaper import WallpaperService


class WallpaperPage(Page):

    def __init__(self, navigator):

        super().__init__(
            navigator,
            "Fondos",
            "Selecciona un fondo de pantalla"
        )

        self.navigator = navigator

        group = Group(
            "Fondos disponibles"
        )

        current = WallpaperService.current()

        wallpapers = WallpaperService.available()

        if not wallpapers:

            group.add(

                Row(

                    title="No se encontraron fondos",

                    subtitle="Añade imágenes a la carpeta de fondos",

                    icon="wallpaper.svg"

                )

            )

        else:

            for wallpaper in wallpapers:

                name = os.path.splitext(

                    os.path.basename(
                        wallpaper
                    )

                )[0]

                group.add(

                    Row(

                        title=name,

                        subtitle=(
                            "Seleccionado"
                            if wallpaper == current
                            else None
                        ),

                        icon="wallpaper.svg",

                        callback=lambda _, w=wallpaper: self.select(w)

                    )

                )

        self.add(
            group
        )

    def select(
        self,
        wallpaper
    ):

        WallpaperService.set(
            wallpaper
        )

        self.navigator.show_page(
            "appearance"
        )