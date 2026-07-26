import subprocess


class BatteryService:

    @staticmethod
    def _run(cmd):

        try:

            return subprocess.run(

                cmd,

                capture_output=True,
                text=True,
                timeout=3

            ).stdout

        except Exception:

            return None

    @staticmethod
    def _find_battery():

        out = BatteryService._run(["upower", "-e"])

        if out is None:

            return None

        for line in out.splitlines():

            if "battery" in line.lower():

                return line

        return None

    @staticmethod
    def available():

        return BatteryService._find_battery() is not None

    @staticmethod
    def get():

        battery = BatteryService._find_battery()

        if battery is None:

            return {"available": False}

        info_out = BatteryService._run(["upower", "-i", battery])

        if info_out is None:

            return {"available": False}

        info = {

            "available": True,
            "percentage": 0,

            "state": "unknown",

            "time_to_full": "",
            "time_to_empty": "",

            "icon": "󰂎",
            "charging_icon": ""
        }

        for line in info_out.splitlines():

            line = line.strip()

            if line.startswith("state:"):

                info["state"] = line.split(":", 1)[1].strip()

            elif line.startswith("percentage:"):

                try:

                    info["percentage"] = int(
                        line.split(":", 1)[1]
                        .replace("%", "")
                        .strip()
                    )

                except ValueError:
                    pass

            elif line.startswith("time to full:"):

                info["time_to_full"] = line.split(":", 1)[1].strip()

            elif line.startswith("time to empty:"):

                info["time_to_empty"] = line.split(":", 1)[1].strip()

        p = info["percentage"]

        charging = info["state"] in ("charging", "fully-charged", "pending-charge")

        if charging:
            if p < 10:
                info["icon"] = "󰢜"
            elif p < 30:
                info["icon"] = "󰂆"
            elif p < 50:
                info["icon"] = "󰂇"
            elif p < 70:
                info["icon"] = "󰂈"
            elif p < 85:
                info["icon"] = "󰢝"
            elif p < 95:
                info["icon"] = "󰂉"
            else:
                info["icon"] = "󰂊"
        else:
            if p >= 95:
                info["icon"] = "󰁹"
            elif p >= 80:
                info["icon"] = "󰂂"
            elif p >= 60:
                info["icon"] = "󰂀"
            elif p >= 40:
                info["icon"] = "󰁾"
            elif p >= 20:
                info["icon"] = "󰁼"
            else:
                info["icon"] = "󰂎"

        return info
