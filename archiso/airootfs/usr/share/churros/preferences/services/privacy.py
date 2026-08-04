import os
import subprocess

from services.settings import SettingsService


class PrivacyService:

    @staticmethod
    def location():

        return SettingsService.get(
            "privacy.location",
            False
        )

    @staticmethod
    def set_location(value):

        SettingsService.set(
            "privacy.location",
            value
        )

    @staticmethod
    def camera():

        return SettingsService.get(
            "privacy.camera",
            True
        )

    @staticmethod
    def set_camera(value):

        SettingsService.set(
            "privacy.camera",
            value
        )

    @staticmethod
    def microphone():

        return SettingsService.get(
            "privacy.microphone",
            True
        )

    @staticmethod
    def set_microphone(value):

        SettingsService.set(
            "privacy.microphone",
            value
        )

    @staticmethod
    def telemetry():

        return SettingsService.get(
            "privacy.telemetry",
            False
        )

    @staticmethod
    def set_telemetry(value):

        SettingsService.set(
            "privacy.telemetry",
            value
        )

    @staticmethod
    def firewall():

        try:

            return subprocess.call(
                [
                    "systemctl",
                    "is-active",
                    "--quiet",
                    "ufw"
                ]
            ) == 0

        except Exception:

            return False

    @staticmethod
    def set_firewall(value):

        action = "enable" if value else "disable"

        try:

            if os.geteuid() == 0:

                subprocess.call(
                    [
                        "systemctl",
                        action,
                        "ufw.service"
                    ]
                )

                subprocess.call(
                    ["ufw", "--force", "enable" if value else "disable"]
                )

            else:

                subprocess.call(
                    [
                        "pkexec",
                        "systemctl",
                        action,
                        "ufw.service"
                    ]
                )

                subprocess.call(
                    [
                        "pkexec",
                        "ufw",
                        "--force",
                        "enable" if value else "disable"
                    ]
                )

            return True

        except Exception:

            return False

    @staticmethod
    def screen_lock():

        return SettingsService.get(
            "privacy.screen_lock",
            True
        )

    @staticmethod
    def history():

        return SettingsService.get(
            "privacy.history",
            True
        )

    @staticmethod
    def crash_reports():

        return SettingsService.get(
            "privacy.crash_reports",
            False
        )