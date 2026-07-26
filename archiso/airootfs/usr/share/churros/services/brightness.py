import os
import subprocess


class BrightnessService:

    @staticmethod
    def _run_sync(cmd):

        try:

            return subprocess.run(

                cmd,

                capture_output=True,

                text=True,

                timeout=3

            ).stdout.strip()

        except Exception:

            return None

    @staticmethod
    def available():

        try:

            devices = os.listdir(
                "/sys/class/backlight"
            )

            return len(devices) > 0

        except Exception:

            return False

    @staticmethod
    def get():

        if not BrightnessService.available():

            return {
                "available": False,
                "brightness": 100
            }

        current = BrightnessService._run_sync(

            ["brightnessctl", "--class=backlight", "g"]

        )

        maximum = BrightnessService._run_sync(

            ["brightnessctl", "--class=backlight", "m"]

        )

        if current is None or maximum is None:

            return {
                "available": False,
                "brightness": 100
            }

        try:

            current_i = int(current)
            maximum_i = int(maximum)

            if maximum_i <= 0:

                return {
                    "available": False,
                    "brightness": 100
                }

            brightness = int(
                current_i * 100 / maximum_i
            )

            return {
                "available": True,
                "brightness": brightness
            }

        except ValueError:

            return {
                "available": False,
                "brightness": 100
            }

    @staticmethod
    def set(value):

        if not BrightnessService.available():

            return False

        try:

            subprocess.run(

                [
                    "brightnessctl",
                    "--class=backlight",
                    "set",
                    f"{int(value)}%"
                ],

                capture_output=True,
                timeout=3

            )

            return True

        except Exception:

            return False
