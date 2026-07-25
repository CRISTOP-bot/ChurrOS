import json
import os


class SettingsService:

    CONFIG_DIR = os.path.join(

        os.path.expanduser("~"),

        ".config",

        "churros"

    )

    CONFIG_FILE = os.path.join(

        CONFIG_DIR,

        "settings.json"

    )

    DEFAULTS = {

        "theme": {

            "dark": False,

            "dynamic_colors": True

        },

        "accent": {

            "color": "#ff8c2a"

        },

        "wallpaper": {

            "path": ""

        },

        "icons": {

            "theme": "Papirus"

        },

        "cursor": {

            "theme": "Bibata"

        },

        "fonts": {

            "family": "Inter",

            "scale": 1.0

        }

    }

    @classmethod
    def _ensure(cls):

        os.makedirs(

            cls.CONFIG_DIR,

            exist_ok=True

        )

        if not os.path.exists(

            cls.CONFIG_FILE

        ):

            with open(

                cls.CONFIG_FILE,

                "w"

            ) as file:

                json.dump(

                    cls.DEFAULTS,

                    file,

                    indent=4

                )

    @classmethod
    def load(cls):

        cls._ensure()

        try:

            with open(

                cls.CONFIG_FILE,

                "r"

            ) as file:

                return json.load(

                    file

                )

        except Exception:

            return cls.DEFAULTS.copy()

    @classmethod
    def save(

        cls,

        data

    ):

        cls._ensure()

        with open(

            cls.CONFIG_FILE,

            "w"

        ) as file:

            json.dump(

                data,

                file,

                indent=4

            )

    @classmethod
    def get(

        cls,

        key,

        default=None

    ):

        data = cls.load()

        current = data

        for part in key.split("."):

            if not isinstance(

                current,

                dict

            ):

                return default

            current = current.get(

                part

            )

            if current is None:

                return default

        return current

    @classmethod
    def set(

        cls,

        key,

        value

    ):

        data = cls.load()

        current = data

        keys = key.split(".")

        for part in keys[:-1]:

            current = current.setdefault(

                part,

                {}

            )

        current[

            keys[-1]

        ] = value

        cls.save(

            data

        )