import shutil

from services.backends.pipewire import PipeWireBackend


class AudioService:

    backend = None

    @classmethod
    def available(cls):

        import shutil

        return shutil.which("wpctl") is not None

    @classmethod
    def _backend(cls):

        if cls.backend is not None:

            return cls.backend

        if shutil.which("wpctl"):

            cls.backend = PipeWireBackend()

            return cls.backend

        raise RuntimeError(

            "PipeWire no está instalado."

        )

    #
    # Salidas
    #

    @classmethod
    def outputs(cls):

        return cls._backend().outputs()

    @classmethod
    def set_output(
        cls,
        device
    ):

        cls._backend().set_output(
            device
        )

    #
    # Entradas
    #

    @classmethod
    def inputs(cls):

        return cls._backend().inputs()

    @classmethod
    def set_input(
        cls,
        device
    ):

        cls._backend().set_input(
            device
        )

    #
    # Volumen
    #

    @classmethod
    def output_volume(cls):

        return cls._backend().output_volume()

    @classmethod
    def input_volume(cls):

        return cls._backend().input_volume()

    @classmethod
    def set_output_volume(
        cls,
        value
    ):

        cls._backend().set_output_volume(
            value
        )

    @classmethod
    def set_input_volume(
        cls,
        value
    ):

        cls._backend().set_input_volume(
            value
        )

    #
    # Mute
    #

    @classmethod
    def output_muted(cls):

        return cls._backend().output_muted()

    @classmethod
    def input_muted(cls):

        return cls._backend().input_muted()

    @classmethod
    def set_output_mute(
        cls,
        muted
    ):

        cls._backend().set_output_mute(
            muted
        )

    @classmethod
    def set_input_mute(
        cls,
        muted
    ):

        cls._backend().set_input_mute(
            muted
        )