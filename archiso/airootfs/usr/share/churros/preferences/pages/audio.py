from widgets.page import Page
from widgets.group import Group
from widgets.combo_row import ComboRow
from widgets.slider_row import SliderRow
from widgets.switch_row import SwitchRow

from services.audio import AudioService


class AudioPage(Page):

    def __init__(
        self,
        navigator
    ):

        super().__init__(
            navigator,
            "Audio",
            "Configura los dispositivos de sonido"
        )

        if not AudioService.available():

            group = Group("Audio")
            group.add(
                SliderRow(
                    title="Audio",
                    value=0,
                    callback=lambda *args: None
                )
            )
            err = Group("Estado")
            err.add(
                SwitchRow(
                    title="WirePlumber no disponible",
                    active=False,
                    callback=lambda *args: None
                )
            )
            self.add(group)
            return

        #
        # Salida
        #

        output_group = Group(
            "Salida"
        )

        try:

            self.outputs = AudioService.outputs()

        except Exception:

            self.outputs = []

        current_output = None

        for device in self.outputs:

            if device.default:

                current_output = device.name

                break

        self.output_combo = ComboRow(
            title="Dispositivo",
            values=[d.name for d in self.outputs],
            selected=current_output,
            callback=self.on_output_changed
        )

        output_group.add(
            self.output_combo
        )

        self.output_volume = SliderRow(
            title="Volumen",
            value=AudioService.output_volume(),
            callback=self.on_output_volume
        )

        output_group.add(
            self.output_volume
        )

        self.output_mute = SwitchRow(
            title="Silenciar",
            active=AudioService.output_muted(),
            callback=self.on_output_mute
        )

        output_group.add(
            self.output_mute
        )

        self.add(
            output_group
        )

        #
        # Entrada
        #

        input_group = Group(
            "Micrófono"
        )

        self.inputs = []

        try:

            self.inputs = AudioService.inputs()

        except Exception:

            pass

        current_input = None

        for device in self.inputs:

            if device.default:

                current_input = device.name

                break

        self.input_combo = ComboRow(
            title="Dispositivo",
            values=[d.name for d in self.inputs],
            selected=current_input,
            callback=self.on_input_changed
        )

        input_group.add(
            self.input_combo
        )

        self.input_volume = SliderRow(
            title="Volumen",
            value=AudioService.input_volume(),
            callback=self.on_input_volume
        )

        input_group.add(
            self.input_volume
        )

        self.input_mute = SwitchRow(
            title="Silenciar",
            active=AudioService.input_muted(),
            callback=self.on_input_mute
        )

        input_group.add(
            self.input_mute
        )

        self.add(
            input_group
        )

    #
    # Salida
    #

    def on_output_changed(
        self,
        value
    ):

        for device in self.outputs:

            if device.name == value:

                AudioService.set_output(
                    device
                )

                break

    def on_output_volume(
        self,
        slider
    ):

        AudioService.set_output_volume(
            slider.get_value()
        )

    def on_output_mute(
        self,
        active
    ):

        AudioService.set_output_mute(
            active
        )

    #
    # Entrada
    #

    def on_input_changed(
        self,
        value
    ):

        for device in self.inputs:

            if device.name == value:

                AudioService.set_input(
                    device
                )

                break

    def on_input_volume(
        self,
        slider
    ):

        AudioService.set_input_volume(
            slider.get_value()
        )

    def on_input_mute(
        self,
        active
    ):

        AudioService.set_input_mute(
            active
        )