class DisplayBackend:

    #
    # Monitores
    #

    def monitors(self):
        raise NotImplementedError

    def current_monitor(self):
        raise NotImplementedError

    #
    # Resoluciones
    #

    def resolutions(
        self,
        monitor
    ):
        raise NotImplementedError

    def refresh_rates(
        self,
        monitor
    ):
        raise NotImplementedError

    #
    # Escala
    #

    def scale(
        self,
        monitor
    ):
        raise NotImplementedError

    def set_scale(
        self,
        monitor,
        scale
    ):
        raise NotImplementedError

    #
    # Rotación
    #

    def rotation(
        self,
        monitor
    ):
        raise NotImplementedError

    def set_rotation(
        self,
        monitor,
        rotation
    ):
        raise NotImplementedError

    #
    # Resolución
    #

    def set_resolution(
        self,
        monitor,
        mode
    ):
        raise NotImplementedError

    #
    # VRR
    #

    def set_vrr(
        self,
        monitor,
        enabled
    ):
        raise NotImplementedError

    #
    # Brillo
    #

    def has_brightness(self):
        return False

    def brightness(self):
        return 100

    def set_brightness(
        self,
        value
    ):
        raise NotImplementedError


class AudioBackend:

    #
    # Dispositivos
    #

    def outputs(self):
        raise NotImplementedError

    def inputs(self):
        raise NotImplementedError

    def set_output(
        self,
        device
    ):
        raise NotImplementedError

    def set_input(
        self,
        device
    ):
        raise NotImplementedError

    #
    # Volumen
    #

    def output_volume(self):
        raise NotImplementedError

    def input_volume(self):
        raise NotImplementedError

    def set_output_volume(
        self,
        value
    ):
        raise NotImplementedError

    def set_input_volume(
        self,
        value
    ):
        raise NotImplementedError

    #
    # Silenciar
    #

    def output_muted(self):
        raise NotImplementedError

    def input_muted(self):
        raise NotImplementedError

    def set_output_mute(
        self,
        muted
    ):
        raise NotImplementedError

    def set_input_mute(
        self,
        muted
    ):
        raise NotImplementedError