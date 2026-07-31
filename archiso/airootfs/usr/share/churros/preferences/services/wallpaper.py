import os
import shutil
import subprocess
import time

from services.settings import SettingsService


class WallpaperService:

    PROJECT_DIR = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            ".."
        )
    )

    PROJECT_WALLPAPERS = os.path.join(
        PROJECT_DIR,
        "wallpapers"
    )

    WALLPAPER_DIRS = [
        PROJECT_WALLPAPERS,
        "/usr/share/churros/wallpapers",
        "/usr/share/backgrounds",
        os.path.expanduser("~/.local/share/churros/wallpapers"),
        os.path.expanduser("~/Pictures/Wallpapers"),
        os.path.expanduser("~/Pictures")
    ]

    USER_DIR = os.path.expanduser(
        "~/.local/share/churros/wallpapers"
    )

    EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp", ".gif")

    @classmethod
    def _build_env(cls):
        env = os.environ.copy()
        if not env.get("WAYLAND_DISPLAY"):
            xrd = env.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}")
            if os.path.isdir(xrd):
                for sock in sorted(os.listdir(xrd)):
                    if sock.startswith("wayland-"):
                        env["WAYLAND_DISPLAY"] = sock
                        break
        if not env.get("XDG_RUNTIME_DIR"):
            env["XDG_RUNTIME_DIR"] = f"/run/user/{os.getuid()}"
        return env

    @classmethod
    def current(cls):
        return SettingsService.get("wallpaper.path", "")

    @classmethod
    def set(cls, path):
        SettingsService.set("wallpaper.path", path)
        cls.apply(path)

    @classmethod
    def apply(cls, path):
        if not path or not os.path.isfile(path):
            return False

        env = cls._build_env()

        if shutil.which("churros-apply-wallpaper") is not None:
            try:
                r = subprocess.run(
                    ["churros-apply-wallpaper", path],
                    env=env,
                    capture_output=True,
                    timeout=10,
                )
                if r.returncode == 0:
                    return True
            except Exception:
                pass

        if shutil.which("awww") is not None:
            if cls._ensure_awww_daemon(env):
                try:
                    r = subprocess.run(
                        ["awww", "img", path],
                        env=env,
                        capture_output=True,
                        timeout=5,
                    )
                    if r.returncode == 0:
                        return True
                except Exception:
                    pass

        if shutil.which("swaybg") is not None:
            try:
                subprocess.run(
                    ["pkill", "-x", "swaybg"],
                    capture_output=True,
                    timeout=2,
                )
            except Exception:
                pass
            try:
                subprocess.Popen(
                    ["swaybg", "-i", path, "-m", "fill"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True,
                    env=env,
                )
                time.sleep(0.4)
                return True
            except Exception:
                pass

        return False

    @classmethod
    def _ensure_awww_daemon(cls, env):
        if shutil.which("awww-daemon") is None:
            return False
        try:
            r = subprocess.run(
                ["pgrep", "-x", "awww-daemon"],
                capture_output=True,
                timeout=2,
            )
            if r.returncode == 0:
                return True
        except Exception:
            pass

        try:
            subprocess.Popen(
                ["awww-daemon"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
                env=env,
            )
            for _ in range(20):
                time.sleep(0.1)
                r = subprocess.run(
                    ["pgrep", "-x", "awww-daemon"],
                    capture_output=True,
                    timeout=1,
                )
                if r.returncode == 0:
                    time.sleep(0.2)
                    return True
        except Exception:
            pass
        return False

    @classmethod
    def available(cls):
        wallpapers = []
        seen = set()
        for directory in cls.WALLPAPER_DIRS:
            if not os.path.isdir(directory):
                continue
            try:
                for file in sorted(os.listdir(directory)):
                    if file.lower().endswith(cls.EXTENSIONS):
                        full = os.path.join(directory, file)
                        if full not in seen:
                            seen.add(full)
                            wallpapers.append(full)
            except (PermissionError, OSError):
                continue
        return wallpapers

    @classmethod
    def import_image(cls, source_path):
        if not source_path or not os.path.isfile(source_path):
            return None
        try:
            os.makedirs(cls.USER_DIR, exist_ok=True)
        except OSError:
            return None
        base = os.path.basename(source_path)
        dest = os.path.join(cls.USER_DIR, base)
        n = 1
        name, ext = os.path.splitext(base)
        while os.path.exists(dest):
            dest = os.path.join(cls.USER_DIR, f"{name}_{n}{ext}")
            n += 1
        try:
            shutil.copyfile(source_path, dest)
        except Exception:
            return None
        return dest