class Monitor:

    def __init__(
        self,
        name,
        description,
        width,
        height,
        refresh,
        scale,
        transform,
        focused,
        modes=None,
        vrr=False
    ):

        self.name = name
        self.description = description

        self.width = width
        self.height = height

        self.refresh = refresh

        self.scale = scale

        self.transform = transform

        self.focused = focused

        self.modes = modes or []

        self.vrr = vrr

    @property
    def resolution(self):

        return f"{self.width} × {self.height}"

    @property
    def mode(self):

        return f"{self.width}x{self.height}@{self.refresh:.3f}"

    @property
    def scale_percent(self):

        return int(self.scale * 100)

    @property
    def rotation(self):

        mapping = {

            "normal": "Normal",
            "90": "90°",
            "180": "180°",
            "270": "270°",

            "flipped": "Volteado",

            "flipped-90": "Volteado 90°",

            "flipped-180": "Volteado 180°",

            "flipped-270": "Volteado 270°"

        }

        return mapping.get(

            self.transform,

            "Normal"

        )

    @property
    def refresh_string(self):

        return f"{self.refresh:.0f} Hz"

    def __repr__(self):

        return (

            f"<Monitor "

            f"{self.name} "

            f"{self.width}x{self.height}"

            f"@{self.refresh}>"

        )