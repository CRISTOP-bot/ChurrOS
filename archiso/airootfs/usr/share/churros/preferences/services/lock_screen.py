import os
import shutil
import subprocess
import tempfile

from services.settings import SettingsService


class LockScreenService:

    CONFIG_DIR = os.path.join(
        os.path.expanduser("~"),
        ".config",
        "churros"
    )

    CONFIG_FILE = os.path.join(CONFIG_DIR, "lock_screen.json")

    DEFAULTS = {
        "enabled": False,
        "timeout_seconds": 600,
        "indicator": "auto",
        "wallpaper_path": "",
        "screenshot": False,
        "fade_in": 200,
        "grace": 0,
        "font": "JetBrainsMono Nerd Font",
        "font_size": 24,
        "ring_color": "7aa2f7ff",
        "inside_color": "00000088",
        "key_hl_color": "bb9af7ff",
        "bs_color": "f7768eff",
        "separator_color": "00000000",
    }

    INDICATORS = (
        "none",
        "ring",
        "bar",
        "dots",
        "auto",
    )

    @classmethod
    def _read(cls):

        try:

            import json

            with open(cls.CONFIG_FILE, "r") as f:

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
    def get(cls, key, default=None):

        return cls._read().get(key, default)

    @classmethod
    def set_all(cls, **kwargs):

        data = cls._read()
        data.update(kwargs)
        cls._save(data)

    @classmethod
    def is_enabled(cls):

        return bool(cls.get("enabled", False))

    @classmethod
    def is_available(cls):

        return shutil.which("swaylock") is not None

    @classmethod
    def is_idle_available(cls):

        return shutil.which("swayidle") is not None

    @classmethod
    def is_running_idle(cls):

        try:

            r = subprocess.run(
                ["pgrep", "-x", "swayidle"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=2,
            )

            return r.returncode == 0

        except Exception:

            return False

    @classmethod
    def is_running_lock(cls):

        try:

            r = subprocess.run(
                ["pgrep", "-x", "swaylock"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=2,
            )

            return r.returncode == 0

        except Exception:

            return False

    @classmethod
    def lock_now(cls):

        try:

            subprocess.Popen(
                ["swaylock"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )

        except Exception as exc:

            print("[lock-screen] lock_now fallo:", exc)

    @classmethod
    def _build_swaylock_cmd(cls, data):

        cmd = ["swaylock"]

        indicator = data.get("indicator", "auto")

        if indicator and indicator != "auto":

            cmd += ["-i", indicator]

        elif indicator == "auto":

            cmd += ["-i", "ring"]

        wp = data.get("wallpaper_path", "")

        if wp and os.path.isfile(wp):

            cmd += ["-i", wp]

        if data.get("screenshot"):

            cmd += ["-f"]

        if data.get("fade_in"):

            cmd += ["-F", str(int(data["fade_in"]))]

        if data.get("grace"):

            cmd += ["-g", str(int(data["grace"]))]

        font = data.get("font", "")

        font_size = int(data.get("font_size", 24))

        if font:

            cmd += ["--font", font]

        if font_size:

            cmd += ["--font-size", str(font_size)]

        for key, flag in (

            ("ring_color", "-r"),
            ("inside_color", "-s"),
            ("key_hl_color", "-k"),
            ("bs_color", "-b"),
            ("separator_color", "-n"),

        ):

            val = data.get(key, "")

            if val:

                cmd += [flag, str(val).lstrip("#")]

        return cmd

    @classmethod
    def preview(cls):

        if not cls.is_available():

            return False

        data = cls._read()

        cmd = cls._build_swaylock_cmd(data)

        try:

            subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )

            return True

        except Exception as exc:

            print("[lock-screen] preview fallo:", exc)
            return False

    @classmethod
    def _stop_idle(cls):

        try:

            subprocess.Popen(
                ["pkill", "-x", "swayidle"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

        except Exception:

            pass

    @classmethod
    def apply(cls):

        cls._stop_idle()

        data = cls._read()

        if not data.get("enabled"):

            return

        if not cls.is_idle_available() or not cls.is_available():

            return

        timeout = int(data.get("timeout_seconds", 600))

        swaylock_cmd = cls._build_swaylock_cmd(data)

        swayidle_cmd = [
            "swayidle",
            "-w",
            "timeout",
            str(timeout),
            " ".join(swaylock_cmd).replace("'", r"'\''"),
        ]

        try:

            env = os.environ.copy()

            xrd = env.get(
                "XDG_RUNTIME_DIR",
                f"/run/user/{os.getuid()}"
            )

            if os.path.isdir(xrd):

                env["XDG_RUNTIME_DIR"] = xrd

            subprocess.Popen(
                swayidle_cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
                env=env,
            )

        except Exception as exc:

            print("[lock-screen] swayidle fallo:", exc)

    @classmethod
    def get_wallpapers(cls):

        try:

            from services.wallpaper import WallpaperService

            return WallpaperService.available()

        except Exception:

            return []
