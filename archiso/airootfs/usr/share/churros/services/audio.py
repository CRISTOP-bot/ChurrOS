import subprocess


class AudioService:

    @staticmethod
    def get_volume():

        try:

            output = subprocess.check_output(
                ["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"],
                text=True
            ).strip()

            volume = float(output.split()[1])

            return int(volume * 100)

        except Exception:

            return 0

    @staticmethod
    def is_muted():

        try:

            output = subprocess.check_output(
                ["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"],
                text=True
            ).strip()

            return "MUTED" in output

        except Exception:

            return False

    @staticmethod
    def set_volume(value):

        subprocess.run(
            ["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", f"{value}%"]
        )