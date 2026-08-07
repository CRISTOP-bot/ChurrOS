import os

from services.backends.hyprland import HyprlandBackend
from services.backends.niri import NiriBackend


class DisplayService:

    @staticmethod
    def backend():

        desktop = (

            os.environ.get(
                "XDG_CURRENT_DESKTOP",
                ""
            )

            or

            os.environ.get(
                "XDG_SESSION_DESKTOP",
                ""
            )

            or

            os.environ.get(
                "DESKTOP_SESSION",
                ""
            )

        ).lower()

        if "niri" in desktop:

            return NiriBackend()

        return HyprlandBackend()

    @classmethod
    def monitors(cls):

        return cls.backend().monitors()

    @classmethod
    def current_monitor(cls):

        return cls.backend().current_monitor()

    @classmethod
    def resolutions(
        cls,
        monitor
    ):

        return cls.backend().resolutions(
            monitor
        )

    @classmethod
    def refresh_rates(
        cls,
        monitor
    ):

        return cls.backend().refresh_rates(
            monitor
        )

    @classmethod
    def scale(
        cls,
        monitor
    ):

        return cls.backend().scale(
            monitor
        )

    @classmethod
    def rotation(
        cls,
        monitor
    ):

        return cls.backend().rotation(
            monitor
        )

    @classmethod
    def set_resolution(
        cls,
        monitor,
        mode
    ):

        cls.backend().set_resolution(
            monitor,
            mode
        )

    @classmethod
    def set_refresh_rate(
        cls,
        monitor,
        rate
    ):

        cls.backend().set_refresh_rate(
            monitor,
            rate
        )

    @classmethod
    def set_scale(
        cls,
        monitor,
        scale
    ):

        cls.backend().set_scale(
            monitor,
            scale
        )

    @classmethod
    def set_rotation(
        cls,
        monitor,
        rotation
    ):

        cls.backend().set_rotation(
            monitor,
            rotation
        )

    @classmethod
    def has_brightness(cls):

        return cls.backend().has_brightness()

    @classmethod
    def brightness(cls):

        return cls.backend().brightness()

    @classmethod
    def set_brightness(
        cls,
        value
    ):

        cls.backend().set_brightness(
            value
        )

    @classmethod
    def set_vrr(
        cls,
        monitor,
        enabled
    ):

        cls.backend().set_vrr(
            monitor,
            enabled
        )