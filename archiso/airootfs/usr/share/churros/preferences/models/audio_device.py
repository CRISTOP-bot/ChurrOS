class AudioDevice:

    def __init__(
        self,
        id,
        name,
        default=False
    ):

        self.id = int(id)

        self.name = name

        self.default = default

    def __repr__(
        self
    ):

        return (

            f"<AudioDevice "

            f"{self.id} "

            f"{self.name}>"

        )

    @property
    def label(
        self
    ):

        return self.name