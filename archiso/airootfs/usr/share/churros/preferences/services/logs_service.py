import subprocess


class LogsService:

    @staticmethod
    def niri_logs(limit=400):

        try:

            result = subprocess.run(
                [
                    "journalctl",
                    "-b0",
                    "--no-pager",
                    "--no-hostname",
                    "-o", "short-iso",
                    "-n", str(int(limit)),
                    "_COMM=niri",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                timeout=8,
            )

            output = result.stdout.decode(
                "utf-8",
                errors="replace"
            )

            if output.strip():
                return output

        except Exception:
            pass

        try:

            result = subprocess.run(
                [
                    "journalctl",
                    "-b0",
                    "--no-pager",
                    "--no-hostname",
                    "-o", "short-iso",
                    "-n", str(int(limit)),
                    "-u", "greetd",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                timeout=8,
            )

            return result.stdout.decode(
                "utf-8",
                errors="replace"
            )

        except Exception:
            pass

        try:

            result = subprocess.run(
                [
                    "journalctl",
                    "-b0",
                    "--no-pager",
                    "--no-hostname",
                    "-o", "short-iso",
                    "-n", str(int(limit)),
                    "--grep=niri",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                timeout=8,
            )

            return result.stdout.decode(
                "utf-8",
                errors="replace"
            )

        except Exception:
            return ""

    @staticmethod
    def niri_validate():

        try:

            result = subprocess.run(
                [
                    "niri",
                    "validate",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=4,
            )

            stderr = result.stderr.decode(
                "utf-8",
                errors="replace"
            ).strip()

            if result.returncode == 0:
                return True, ""

            return False, stderr

        except FileNotFoundError:

            return True, ""

        except Exception as exc:

            return False, str(exc)
