import os
import shutil
import tarfile
import subprocess
import tempfile

from services.settings import SettingsService


class BackupService:

    HOME = os.path.expanduser("~")

    CHURROS_DIR = os.path.join(
        HOME,
        ".config",
        "churros"
    )

    SETTINGS_FILE = os.path.join(
        CHURROS_DIR,
        "settings.json"
    )

    DOTFILES = [
        ("niri", os.path.join(HOME, ".config", "niri")),
        ("foot", os.path.join(HOME, ".config", "foot")),
        ("fuzzel", os.path.join(HOME, ".config", "fuzzel")),
        ("mako", os.path.join(HOME, ".config", "mako")),
        ("waybar", os.path.join(HOME, ".config", "waybar")),
    ]

    DEFAULTS_DIR = "/usr/share/churros/defaults"

    @classmethod
    def export_to(cls, dest_path):

        if not os.path.isdir(cls.CHURROS_DIR) and not any(
            os.path.exists(p) for _, p in cls.DOTFILES
        ):

            raise RuntimeError(
                "No hay configuracion que exportar"
            )

        directory = os.path.dirname(
            os.path.abspath(dest_path)
        )

        os.makedirs(
            directory,
            exist_ok=True
        )

        fd, tmp = tempfile.mkstemp(
            prefix="churros-backup-",
            suffix=".tar.zst",
            dir=directory
        )

        os.close(fd)

        try:

            with tarfile.open(
                tmp,
                "w"
            ) as tar:

                if os.path.exists(cls.SETTINGS_FILE):

                    tar.add(
                        cls.SETTINGS_FILE,
                        arcname="churros/settings.json"
                    )

                for name, path in cls.DOTFILES:

                    if os.path.exists(path):

                        tar.add(
                            path,
                            arcname="dotfiles/" + name
                        )

            shutil.move(
                tmp,
                dest_path
            )

        except Exception:

            try:
                os.unlink(tmp)
            except OSError:
                pass

            raise

        return dest_path

    @classmethod
    def import_from(cls, src_path):

        if not os.path.isfile(src_path):

            raise RuntimeError(
                "El archivo no existe: " + src_path
            )

        try:

            with tarfile.open(
                src_path,
                "r"
            ) as tar:

                members = tar.getmembers()

                has_churros = any(
                    m.name.startswith("churros/")
                    or m.name == "churros"
                    for m in members
                )

                has_dotfiles = any(
                    m.name.startswith("dotfiles/")
                    or m.name == "dotfiles"
                    for m in members
                )

                if not has_churros and not has_dotfiles:

                    raise RuntimeError(
                        "El archivo no es un backup de ChurrOS"
                    )

                for m in members:

                    if m.name.startswith("churros/"):

                        if m.isdir():
                            continue

                        target = os.path.join(
                            cls.CHURROS_DIR,
                            os.path.relpath(
                                m.name,
                                "churros"
                            )
                        )

                        os.makedirs(
                            os.path.dirname(target),
                            exist_ok=True
                        )

                        with tarfile.open(src_path) as t2:

                            with t2.extractfile(m) as src:

                                with open(target, "wb") as dst:

                                    shutil.copyfileobj(
                                        src,
                                        dst
                                    )

                    elif m.name.startswith("dotfiles/"):

                        parts = m.name.split("/", 2)

                        if len(parts) < 2:
                            continue

                        df_name = parts[1]

                        target_dir = os.path.join(
                            cls.HOME,
                            ".config",
                            df_name
                        )

                        if m.isdir():
                            os.makedirs(
                                target_dir,
                                exist_ok=True
                            )
                            continue

                        if not parts[2]:
                            continue

                        target = os.path.join(
                            target_dir,
                            parts[2]
                        )

                        os.makedirs(
                            os.path.dirname(target),
                            exist_ok=True
                        )

                        with tarfile.open(src_path) as t3:

                            with t3.extractfile(m) as src:

                                with open(target, "wb") as dst:

                                    shutil.copyfileobj(
                                        src,
                                        dst
                                    )

        except tarfile.TarError as exc:

            raise RuntimeError(
                "Archivo invalido: " + str(exc)
            )

        cls._reload_services()

        return True

    @classmethod
    def reset_to_defaults(cls):

        if not os.path.isdir(cls.DEFAULTS_DIR):

            raise RuntimeError(
                "Defaults no encontrados: " + cls.DEFAULTS_DIR
            )

        cls._restore_settings()

        cls._restore_dotfiles()

        cls._reload_services()

        return True

    @classmethod
    def _restore_settings(cls):

        SettingsService.save(
            SettingsService.DEFAULTS.copy()
        )

    @classmethod
    def _restore_dotfiles(cls):

        for entry in os.listdir(cls.DEFAULTS_DIR):

            src = os.path.join(
                cls.DEFAULTS_DIR,
                entry
            )

            dst = os.path.join(
                cls.HOME,
                ".config",
                entry
            )

            if not os.path.isdir(src):
                continue

            if os.path.exists(dst):

                shutil.rmtree(dst)

            shutil.copytree(
                src,
                dst
            )

    @classmethod
    def _reload_services(cls):

        for cmd in (
            ["pkill", "-HUP", "waybar"],
            ["makoctl", "reload"],
            ["pkill", "-fuzzel"],
        ):

            try:

                subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )

            except Exception:

                pass
