class DisplayMode:

    def __init__(
        self,
        width,
        height,
        refresh,
        current=False,
        preferred=False
    ):

        self.width = int(width)

        self.height = int(height)

        self.refresh = float(refresh)

        self.current = current

        self.preferred = preferred

    @property
    def resolution(self):

        return f"{self.width} × {self.height}"

    @property
    def refresh_string(self):

        return f"{self.refresh:.0f} Hz"

    @property
    def label(self):

        return (

            f"{self.width} × {self.height}"

            f" @ "

            f"{self.refresh:.0f} Hz"

        )

    @property
    def mode(self):

        return (

            f"{self.width}x{self.height}"

            f"@"

            f"{self.refresh:.3f}"

        )

    def __eq__(
        self,
        other
    ):

        if not isinstance(
            other,
            DisplayMode
        ):

            return False

        return (

            self.width == other.width

            and

            self.height == other.height

            and

            abs(

                self.refresh

                -

                other.refresh

            ) < 0.01

        )

    def __repr__(self):

        return (

            f"<DisplayMode "

            f"{self.mode}>"

        )