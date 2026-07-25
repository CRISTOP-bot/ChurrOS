from services.settings import SettingsService


class AccentService:

    COLORS = [

        "Blue",
        "Purple",
        "Pink",
        "Red",
        "Orange",
        "Yellow",
        "Green",
        "Teal"

    ]

    @classmethod
    def current(cls):

        return SettingsService.get(

            "accent.color",

            "Blue"

        )

    @classmethod
    def set(

        cls,

        color

    ):

        SettingsService.set(

            "accent.color",

            color

        )

        #
        # Más adelante aquí podremos:
        #
        # - actualizar CSS
        # - regenerar colores
        # - avisar a Quickshell
        #

    @classmethod
    def available(cls):

        return cls.COLORS