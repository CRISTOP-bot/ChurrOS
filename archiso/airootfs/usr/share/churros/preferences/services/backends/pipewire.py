import re
import subprocess

from models.audio_device import AudioDevice
from services.backends.base import AudioBackend


class PipeWireBackend(AudioBackend):

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

    #
    # Dispositivos
    #

    def outputs(self):

        return self._devices("Sinks")

    def inputs(self):

        return self._devices("Sources")

    def _devices(
        self,
        section
    ):

        text = self._run(

            "wpctl",

            "status"

        )

        devices = []

        inside = False

        default = None

        current = None

        for line in text.splitlines():

            if section in line:

                inside = True

                continue

            if inside:

                if line.strip() == "":

                    break

                match = re.search(

                    r'(\*?)\s*([0-9]+)\.\s+(.*)',

                    line.strip()

                )

                if not match:

                    continue

                current = AudioDevice(

                    id=int(

                        match.group(2)

                    ),

                    name=match.group(3),

                    default=match.group(1) == "*"

                )

                devices.append(

                    current

                )

        return devices

    #
    # Volumen
    #

    def output_volume(self):

        return self._volume(

            "@DEFAULT_AUDIO_SINK@"

        )

    def input_volume(self):

        return self._volume(

            "@DEFAULT_AUDIO_SOURCE@"

        )

    def _volume(
        self,
        target
    ):

        text = self._run(

            "wpctl",

            "get-volume",

            target

        )

        match = re.search(

            r'([0-9.]+)',

            text

        )

        if not match:

            return 100

        return float(

            match.group(1)

        ) * 100

    #
    # Mute
    #

    def output_muted(self):

        return self._muted(

            "@DEFAULT_AUDIO_SINK@"

        )

    def input_muted(self):

        return self._muted(

            "@DEFAULT_AUDIO_SOURCE@"

        )

    def _muted(
        self,
        target
    ):

        text = self._run(

            "wpctl",

            "get-volume",

            target

        )

        return "MUTED" in text

    #
    # Cambios
    #

    def set_output_volume(
        self,
        value
    ):

        subprocess.run(

            [

                "wpctl",

                "set-volume",

                "@DEFAULT_AUDIO_SINK@",

                f"{int(value)}%"

            ]

        )

    def set_input_volume(
        self,
        value
    ):

        subprocess.run(

            [

                "wpctl",

                "set-volume",

                "@DEFAULT_AUDIO_SOURCE@",

                f"{int(value)}%"

            ]

        )

    def set_output_mute(
        self,
        muted
    ):

        subprocess.run(

            [

                "wpctl",

                "set-mute",

                "@DEFAULT_AUDIO_SINK@",

                "1" if muted else "0"

            ]

        )

    def set_input_mute(
        self,
        muted
    ):

        subprocess.run(

            [

                "wpctl",

                "set-mute",

                "@DEFAULT_AUDIO_SOURCE@",

                "1" if muted else "0"

            ]

        )

    #
    # Predeterminados
    #

    def set_output(
        self,
        device
    ):

        subprocess.run(

            [

                "wpctl",

                "set-default",

                str(device.id)

            ]

        )

    def set_input(
        self,
        device
    ):

        subprocess.run(

            [

                "wpctl",

                "set-default",

                str(device.id)

            ]

        )