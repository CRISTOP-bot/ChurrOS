from widgets.page import Page
from widgets.group import Group
from widgets.row import Row
from widgets.combo_row import ComboRow
from widgets.slider_row import SliderRow
from widgets.switch_row import SwitchRow

from services.display import DisplayService


class DisplayPage(Page):

    def __init__(
        self,
        navigator
    ):

        super().__init__(

            navigator,

            "Pantalla",

            "Configura tus monitores"

        )

        self.monitor = DisplayService.current_monitor()

        if self.monitor is None:

            group = Group(
                "Monitor"
            )

            group.add(

                Row(

                    title="No se encontró ningún monitor"

                )

            )

            self.add(
                group
            )

            return

        #
        # Información
        #

        info = Group(
            "Monitor"
        )

        info.add(

            Row(

                title=self.monitor.description,

                subtitle=self.monitor.name

            )

        )

        self.add(
            info
        )

        #
        # Configuración
        #

        config = Group(
            "Configuración"
        )

        #
        # Resoluciones
        #

        resolutions = [

            mode.label

            for mode in self.monitor.modes

        ]

        current = None

        for mode in self.monitor.modes:

            if mode.current:

                current = mode.label

                break

        self.resolution = ComboRow(

            title="Resolución",

            values=resolutions,

            selected=current,

            callback=self.on_resolution

        )

        config.add(
            self.resolution
        )

        #
        # Escala
        #

        scales = [

            "100 %",

            "125 %",

            "150 %",

            "175 %",

            "200 %"

        ]

        current_scale = (

            f"{self.monitor.scale_percent} %"

        )

        self.scale = ComboRow(

            title="Escala",

            values=scales,

            selected=current_scale,

            callback=self.on_scale

        )

        config.add(
            self.scale
        )

        #
        # Rotación
        #

        rotations = [

            "Normal",

            "90°",

            "180°",

            "270°"

        ]

        self.rotation = ComboRow(

            title="Rotación",

            values=rotations,

            selected=self.monitor.rotation,

            callback=self.on_rotation

        )

        config.add(
            self.rotation
        )

        #
        # VRR
        #

        self.vrr = SwitchRow(

            title="Frecuencia variable (VRR)",

            active=self.monitor.vrr,

            callback=self.on_vrr

        )

        config.add(
            self.vrr
        )

        self.add(
            config
        )

        #
        # Brillo
        #

        if DisplayService.has_brightness():

            brightness = Group(
                "Brillo"
            )

            self.slider = SliderRow(

                title="Nivel",

                value=DisplayService.brightness(),

                callback=self.on_brightness

            )

            brightness.add(
                self.slider
            )

            self.add(
                brightness
            )

    #
    # Eventos
    #

    def on_resolution(

        self,

        value

    ):

        for mode in self.monitor.modes:

            if mode.label == value:

                DisplayService.set_resolution(

                    self.monitor,

                    mode

                )

                break

    def on_scale(

        self,

        value

    ):

        scale = (

            float(

                value.replace(

                    "%",

                    ""

                )

            )

            / 100

        )

        DisplayService.set_scale(

            self.monitor,

            scale

        )

    def on_rotation(

        self,

        value

    ):

        mapping = {

            "Normal": "normal",

            "90°": "90",

            "180°": "180",

            "270°": "270"

        }

        DisplayService.set_rotation(

            self.monitor,

            mapping[value]

        )

    def on_vrr(

        self,

        switch,

        active

    ):

        DisplayService.set_vrr(

            self.monitor,

            active

        )

    def on_brightness(

        self,

        slider

    ):

        DisplayService.set_brightness(

            slider.get_value()

        )