import json
import subprocess

from models.monitor import Monitor
from models.display_mode import DisplayMode

from services.backends.base import DisplayBackend


class HyprlandBackend(DisplayBackend):

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

    def _outputs(self):

        try:

            return json.loads(

                self._run(

                    "hyprctl",

                    "monitors",

                    "-j"

                )

            )

        except Exception:

            return []

    def monitors(self):

        monitors = []

        for output in self._outputs():

            modes = [

                DisplayMode(

                    width=output.get(
                        "width",
                        0
                    ),

                    height=output.get(
                        "height",
                        0
                    ),

                    refresh=output.get(
                        "refreshRate",
                        60
                    ),

                    current=True,

                    preferred=True

                )

            ]

            monitors.append(

                Monitor(

                    name=output.get(
                        "name"
                    ),

                    description=output.get(
                        "description",
                        output.get(
                            "name"
                        )
                    ),

                    width=output.get(
                        "width"
                    ),

                    height=output.get(
                        "height"
                    ),

                    refresh=output.get(
                        "refreshRate"
                    ),

                    scale=output.get(
                        "scale",
                        1
                    ),

                    transform=str(

                        output.get(
                            "transform",
                            0
                        )

                    ),

                    focused=output.get(
                        "focused",
                        False
                    ),

                    modes=modes,

                    vrr=output.get(
                        "vrr",
                        False
                    )

                )

            )

        return monitors

    def current_monitor(self):

        for monitor in self.monitors():

            if monitor.focused:

                return monitor

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

        rates = []

        for mode in monitor.modes:

            if mode.refresh not in rates:

                rates.append(
                    mode.refresh
                )

        return sorted(
            rates
        )

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

    def set_scale(
        self,
        monitor,
        scale
    ):

        subprocess.run(

            [

                "hyprctl",

                "keyword",

                "monitor",

                f"{monitor.name},preferred,{scale}"

            ]

        )

    def set_rotation(
        self,
        monitor,
        rotation
    ):

        subprocess.run(

            [

                "hyprctl",

                "keyword",

                "monitor",

                f"{monitor.name},preferred,auto,{rotation}"

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

        import os

        try:

            device = os.listdir(

                "/sys/class/backlight"

            )[0]

            with open(

                f"/sys/class/backlight/{device}/max_brightness"

            ) as f:

                maximum = int(
                    f.read()
                )

            brightness = int(

                maximum

                *

                value

                /

                100

            )

            subprocess.run(

                [

                    "brightnessctl",

                    "set",

                    str(
                        brightness
                    )

                ]

            )

        except Exception:

            pass