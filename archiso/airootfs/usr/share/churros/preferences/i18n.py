import gettext
import os

DOMAIN = "churros"
LOCALEDIR = "/usr/share/locale"

_translation = None


def _resolve(localedir=None, languages=None):

    env_lang = os.environ.get(
        "LANGUAGE"
    )

    if env_lang and not languages:

        languages = env_lang.split(
            ":"
        )

    if not localedir:

        localedir = LOCALEDIR

    if not languages:

        env_lang = os.environ.get(
            "LC_ALL"
        ) or os.environ.get(
            "LC_MESSAGES"
        ) or os.environ.get(
            "LANG"
        )

        if env_lang:

            lang = env_lang.split(
                "."
            )[0].replace(
                "_",
                "-"
            )

            languages = [lang]

    return gettext.translation(

        DOMAIN,

        localedir=localedir,

        languages=languages,

        fallback=True

    )


def install():

    global _translation

    if _translation is None:

        _translation = _resolve()

    return _translation


def _(s):

    if _translation is None:

        install()

    return _translation.gettext(
        s
    )


install()
