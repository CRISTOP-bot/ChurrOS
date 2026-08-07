import os
import subprocess


class NightLightService:

    CONFIG_DIR = os.path.join(
        os.path.expanduser("~"),
        ".config",
        "churros"
    )

    CONFIG_FILE = os.path.join(CONFIG_DIR, "night_light.json")

    DEFAULTS = {
        "enabled": False,
        "temp_day": 6500,
        "temp_night": 4500,
        "gamma": 1.0,
        "manual_lat": None,
        "manual_lng": None,
    }

    @classmethod
    def _read(cls):

        try:

            with open(cls.CONFIG_FILE, "r") as f:

                import json

                data = json.load(f)

                return {**cls.DEFAULTS, **data}

        except Exception:

            return cls.DEFAULTS.copy()

    @classmethod
    def _save(cls, data):

        os.makedirs(cls.CONFIG_DIR, exist_ok=True)

        try:

            import json

            with open(cls.CONFIG_FILE, "w") as f:

                json.dump(data, f, indent=2)

        except Exception:

            pass

    @classmethod
    def is_enabled(cls):

        return bool(cls._read().get("enabled"))

    @classmethod
    def set_enabled(cls, enabled):

        data = cls._read()
        data["enabled"] = bool(enabled)
        cls._save(data)
        cls._apply_state()

    @classmethod
    def get_temp_day(cls):

        return int(cls._read().get("temp_day") or 6500)

    @classmethod
    def get_temp_night(cls):

        return int(cls._read().get("temp_night") or 4500)

    @classmethod
    def set_temps(cls, day, night):

        data = cls._read()
        data["temp_day"] = int(day)
        data["temp_night"] = int(night)
        cls._save(data)
        cls._apply_state()

    @classmethod
    def get_gamma(cls):

        return float(cls._read().get("gamma") or 1.0)

    @classmethod
    def set_gamma(cls, gamma):

        data = cls._read()
        data["gamma"] = float(gamma)
        cls._save(data)
        cls._apply_state()

    @classmethod
    def get_location(cls):

        data = cls._read()
        return data.get("manual_lat"), data.get("manual_lng")

    @classmethod
    def set_location(cls, lat, lng):

        data = cls._read()
        data["manual_lat"] = float(lat) if lat is not None else None
        data["manual_lng"] = float(lng) if lng is not None else None
        cls._save(data)
        cls._apply_state()

    @classmethod
    def is_available(cls):

        for path in ("/usr/bin/wlsunset", "/usr/local/bin/wlsunset"):
            if os.path.exists(path):
                return True
        return False

    @classmethod
    def is_running(cls):

        try:

            r = subprocess.run(
                ["pgrep", "-x", "wlsunset"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=2,
            )

            return r.returncode == 0

        except Exception:

            return False

    @classmethod
    def _stop(cls):

        try:

            subprocess.Popen(
                ["pkill", "-x", "wlsunset"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

        except Exception:
            pass

    @classmethod
    def _apply_state(cls):

        data = cls._read()

        if not data.get("enabled"):

            cls._stop()
            return

        if not cls.is_available():

            return

        cls._stop()

        cmd = [
            "wlsunset",
            "-t", str(int(data["temp_day"])),
            "-T", str(int(data["temp_night"])),
            "-g", str(float(data["gamma"])),
        ]

        lat = data.get("manual_lat")
        lng = data.get("manual_lng")

        if lat is not None and lng is not None:

            cmd += ["-l", str(float(lat)), "-L", str(float(lng))]

        try:

            subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )

        except Exception as exc:

            print("[night-light] spawn fallo:", exc)
