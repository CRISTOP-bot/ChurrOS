import os
import pwd
import getpass


class UsersService:

    @staticmethod
    def username():

        try:

            return getpass.getuser()

        except Exception:

            return "Desconocido"

    @staticmethod
    def full_name():

        try:

            return pwd.getpwuid(
                os.getuid()
            ).pw_gecos.split(",")[0]

        except Exception:

            return UsersService.username()

    @staticmethod
    def home():

        try:

            return os.path.expanduser("~")

        except Exception:

            return ""

    @staticmethod
    def shell():

        try:

            return pwd.getpwuid(
                os.getuid()
            ).pw_shell

        except Exception:

            return "Desconocido"

    @staticmethod
    def uid():

        try:

            return str(
                os.getuid()
            )

        except Exception:

            return "0"

    @staticmethod
    def gid():

        try:

            return str(
                os.getgid()
            )

        except Exception:

            return "0"

    @staticmethod
    def hostname():

        try:

            return os.uname().nodename

        except Exception:

            return "Desconocido"

    @staticmethod
    def auto_login():

        import re

        try:

            with open(
                "/etc/greetd/config.toml",
                "r",
                encoding="utf-8"
            ) as file:

                content = file.read()

            return bool(
                re.search(
                    r"^\s*command\s*=\s*\"[^\"]+\"",
                    content,
                    re.MULTILINE
                )
            )

        except Exception:

            return False

    @staticmethod
    def set_auto_login(value):

        import os
        import re
        import tempfile

        path = "/etc/greetd/config.toml"

        try:

            with open(
                path,
                "r",
                encoding="utf-8"
            ) as file:

                content = file.read()

        except Exception:

            return False

        has_command = bool(
            re.search(
                r"^\s*command\s*=",
                content,
                re.MULTILINE
            )
        )

        if value and has_command:

            return True

        if not value and not has_command:

            return True

        if value:

            if re.search(
                r"^\s*\[default_session\]",
                content,
                re.MULTILINE
            ):

                new_content = re.sub(
                    r"^(\s*\[default_session\]\s*\n)",
                    r'\1command = "/usr/bin/niri"\n',
                    content,
                    count=1,
                    flags=re.MULTILINE
                )

            else:

                new_content = content + (
                    '\n[default_session]\n'
                    'command = "/usr/bin/niri"\n'
                )

        else:

            new_content = re.sub(
                r"^\s*command\s*=\s*\"[^\"]+\"\s*\n",
                "",
                content,
                count=1,
                flags=re.MULTILINE
            )

        if new_content == content:

            return True

        directory = os.path.dirname(path)

        fd, tmp = tempfile.mkstemp(
            prefix="greetd-",
            suffix=".toml",
            dir=directory
        )

        try:

            with os.fdopen(fd, "w", encoding="utf-8") as f:

                f.write(new_content)

            os.replace(tmp, path)

            return True

        except Exception:

            try:

                os.unlink(tmp)

            except OSError:

                pass

            return False