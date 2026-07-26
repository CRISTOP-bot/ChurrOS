import os
import subprocess


def _has_swap():

    try:

        out = subprocess.run(

            ["swapon", "--show", "--noheadings"],

            capture_output=True,
            text=True,
            timeout=2

        ).stdout.strip()

        return bool(out)

    except Exception:

        return False


def _current_desktop():

    return (

        os.environ.get("XDG_CURRENT_DESKTOP")

        or os.environ.get("XDG_SESSION_DESKTOP")

        or os.environ.get("DESKTOP_SESSION")

        or ""

    ).lower()


class PowerService:

    @staticmethod
    def lock():

        try:

            subprocess.Popen(
                ["loginctl", "lock-session"]
            )

        except Exception:
            pass

    @staticmethod
    def logout():

        desktop = _current_desktop()

        try:

            if "niri" in desktop:

                subprocess.Popen(["niri", "msg", "action", "quit"])

            elif "hyprland" in desktop:

                subprocess.Popen(["hyprctl", "dispatch", "exit"])

            elif "sway" in desktop:

                subprocess.Popen(["swaymsg", "exit"])

            else:

                subprocess.Popen(["loginctl", "terminate-user", str(os.getuid())])

        except Exception:
            pass

    @staticmethod
    def suspend():

        try:

            subprocess.Popen(["systemctl", "suspend"])

        except Exception:
            pass

    @staticmethod
    def can_hibernate():

        return _has_swap()

    @staticmethod
    def hibernate():

        try:

            subprocess.Popen(["systemctl", "hibernate"])

        except Exception:
            pass

    @staticmethod
    def restart():

        try:

            subprocess.Popen(["systemctl", "reboot"])

        except Exception:
            pass

    @staticmethod
    def shutdown():

        try:

            subprocess.Popen(["systemctl", "poweroff"])

        except Exception:
            pass
