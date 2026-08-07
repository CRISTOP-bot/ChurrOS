import os
import subprocess


class DatetimeService:

    @staticmethod
    def get_timezone():

        try:

            r = subprocess.run(
                ["timedatectl", "show", "--property=Timezone", "--value"],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=3
            )

            return r.stdout.strip()

        except Exception:

            return ""

    @staticmethod
    def get_ntp():

        try:

            r = subprocess.run(
                ["timedatectl", "show", "--property=NTP", "--value"],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=3
            )

            return r.stdout.strip().lower() == "yes"

        except Exception:

            return False

    @staticmethod
    def get_rtc_time():

        try:

            r = subprocess.run(
                ["timedatectl", "show", "--property=RTCTime", "--value"],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=3
            )

            raw = r.stdout.strip()

            if raw and raw != "n/a":
                return raw

            return ""

        except Exception:

            return ""

    @staticmethod
    def list_timezones():

        try:

            r = subprocess.run(
                ["timedatectl", "list-timezones"],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=5
            )

            return [z.strip() for z in r.stdout.splitlines() if z.strip()]

        except Exception:

            return []

    @staticmethod
    def set_timezone(tz):

        try:

            r = subprocess.run(
                ["churros-pkexec", "timedatectl", "set-timezone", tz],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=10
            )

            return r.returncode == 0

        except Exception:

            return False

    @staticmethod
    def set_ntp(enabled):

        try:

            r = subprocess.run(
                ["churros-pkexec", "timedatectl", "set-ntp",
                 "true" if enabled else "false"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=10
            )

            return r.returncode == 0

        except Exception:

            return False

    @staticmethod
    def current_zone_short():

        tz = DatetimeService.get_timezone()

        if not tz:
            return ""

        parts = tz.split("/")

        if len(parts) >= 2:
            return parts[-1].replace("_", " ")

        return tz
