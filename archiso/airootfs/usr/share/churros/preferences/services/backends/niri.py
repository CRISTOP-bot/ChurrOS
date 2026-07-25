import re
import subprocess

from models.monitor import Monitor
from models.display_mode import DisplayMode

from services.backends.base import DisplayBackend


class NiriBackend(DisplayBackend):

    def _run(
        self,
        *command
    ):

        try:

            result = subprocess.run(

                command,

                capture_output=True,

                text=True,

                check=True

            )

            return result.stdout

        except Exception:

            return ""

    def monitors(self):

        text = self._run(

            "niri",

            "msg",

            "outputs"

        )

        monitors = []

        current = None

        modes = []

        for line in text.splitlines():

            line = line.rstrip()

            #
            # Nuevo monitor
            #

            if line.startswith("Output"):

                if current is not None:

                    current.modes = modes

                    monitors.append(current)

                modes = []

                match = re.search(

                    r'\((.*?)\)',

                    line

                )

                name = match.group(1)

                description = (

                    line

                    .split('"')[1]

                )

                current = Monitor(

                    name=name,

                    description=description,

                    width=0,

                    height=0,

                    refresh=60,

                    scale=1,

                    transform="normal",

                    focused=True,

                    modes=[],

                    vrr=False

                )

                continue

            #
            # Modo actual
            #

            if "Current mode:" in line:

                match = re.search(

                    r'(\d+)x(\d+) @ ([0-9.]+)',

                    line

                )

                if match:

                    current.width = int(

                        match.group(1)

                    )

                    current.height = int(

                        match.group(2)

                    )

                    current.refresh = float(

                        match.group(3)

                    )

                continue

            #
            # Escala
            #

            if "Scale:" in line:

                current.scale = float(

                    line.split(":")[1]

                )

                continue

            #
            # Rotación
            #

            if "Transform:" in line:

                current.transform = (

                    line

                    .split(":")[1]

                    .strip()

                )

                continue

            #
            # VRR
            #

            if "Variable refresh rate:" in line:

                current.vrr = (

                    "supported"

                    in line

                )

                continue

            #
            # Modos
            #

            match = re.match(

                r'\s+(\d+)x(\d+)@([0-9.]+)',

                line

            )

            if match:

                current_mode = (

                    "current"

                    in line

                )

                preferred = (

                    "preferred"

                    in line

                )

                modes.append(

                    DisplayMode(

                        width=match.group(1),

                        height=match.group(2),

                        refresh=match.group(3),

                        current=current_mode,

                        preferred=preferred

                    )

                )

        if current is not None:

            current.modes = modes

            monitors.append(

                current

            )

        return monitors

    def current_monitor(self):

        monitors = self.monitors()

        if monitors:

            return monitors[0]

        return None

    def resolutions(
        self,
        monitor
    ):

        return monitor.modes

    def refresh_rates(
        self,
        monitor
    ):

        values = []

        for mode in monitor.modes:

            if mode.refresh not in values:

                values.append(

                    mode.refresh

                )

        return sorted(values)

    def scale(
        self,
        monitor
    ):

        return monitor.scale

    def rotation(
        self,
        monitor
    ):

        return monitor.transform

    def set_resolution(
        self,
        monitor,
        mode
    ):

        subprocess.run(

            [

                "niri",

                "msg",

                "output",

                monitor.name,

                "mode",

                mode.mode

            ]

        )

    def set_scale(
        self,
        monitor,
        scale
    ):

        subprocess.run(

            [

                "niri",

                "msg",

                "output",

                monitor.name,

                "scale",

                str(scale)

            ]

        )

    def set_rotation(
        self,
        monitor,
        rotation
    ):

        subprocess.run(

            [

                "niri",

                "msg",

                "output",

                monitor.name,

                "transform",

                rotation

            ]

        )

    def set_vrr(
        self,
        monitor,
        enabled
    ):

        subprocess.run(

            [

                "niri",

                "msg",

                "output",

                monitor.name,

                "vrr",

                "on" if enabled else "off"

            ]

        )

    def has_brightness(self):

        import os

        return os.path.isdir(

            "/sys/class/backlight"

        )

    def brightness(self):

        import os

        try:

            device = os.listdir(

                "/sys/class/backlight"

            )[0]

            with open(

                f"/sys/class/backlight/{device}/brightness"

            ) as f:

                current = int(

                    f.read()

                )

            with open(

                f"/sys/class/backlight/{device}/max_brightness"

            ) as f:

                maximum = int(

                    f.read()

                )

            return (

                current

                /

                maximum

            ) * 100

        except Exception:

            return 100

    def set_brightness(
        self,
        value
    ):

        subprocess.run(

            [

                "brightnessctl",

                "set",

                f"{int(value)}%"

            ]

        )