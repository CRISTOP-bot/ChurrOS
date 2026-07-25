import subprocess


def run(command):

    try:

        result = subprocess.run(

            command,

            capture_output=True,

            text=True,

            timeout=1

        )

        return result.stdout.strip()

    except Exception:

        return None