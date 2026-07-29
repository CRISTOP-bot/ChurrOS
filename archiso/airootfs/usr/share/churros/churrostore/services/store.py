import shutil
import subprocess
import threading

from services.pacman_backend import PacmanBackend
from services.flatpak_backend import FlatpakBackend
from services.aur_backend import AurBackend


class StoreService:

    _flatpak_installed_cache = None
    _pacman_installed_cache = None
    _aur_installed_cache = None

    @classmethod
    def pacman_available(cls):
        return PacmanBackend.available()

    @classmethod
    def flatpak_available(cls):
        return FlatpakBackend.available()

    @classmethod
    def aur_available(cls):
        return AurBackend.available()

    @classmethod
    def installed(cls):

        result = {}

        if cls.flatpak_available():
            for app_id, info in FlatpakBackend.installed().items():
                result[f"flatpak:{app_id}"] = info

        if cls.pacman_available():
            for name, info in PacmanBackend.installed().items():
                result[f"pacman:{name}"] = info

        if cls.aur_available():
            for name, info in AurBackend.installed().items():
                result[f"aur:{name}"] = info

        return result

    @classmethod
    def is_installed(cls, package_id):

        if package_id.startswith("flatpak:"):

            app_id = package_id[len("flatpak:"):]

            if cls._flatpak_installed_cache is None:
                cls._flatpak_installed_cache = FlatpakBackend.installed()

            return app_id in cls._flatpak_installed_cache

        if package_id.startswith("pacman:"):

            name = package_id[len("pacman:"):]

            if cls._pacman_installed_cache is None:
                cls._pacman_installed_cache = PacmanBackend.installed()

            return name in cls._pacman_installed_cache

        if package_id.startswith("aur:"):

            name = package_id[len("aur:"):]

            if cls._aur_installed_cache is None:
                cls._aur_installed_cache = AurBackend.installed()

            return name in cls._aur_installed_cache

        return False

    @classmethod
    def invalidate_installed_cache(cls):

        cls._flatpak_installed_cache = None
        cls._pacman_installed_cache = None
        cls._aur_installed_cache = None

    @classmethod
    def search(cls, query="", source="all", callback=None):

        if not query and callback is None:

            return cls._search_default_sync(source)

        if callback is None:

            return cls._search_blocking(query, source)

        cls._search_async(query, source, callback)

    @classmethod
    def _search_default_sync(cls, source):

        results = []

        installed = cls.installed()

        for pkg_id, info in installed.items():

            results.append({
                "id": pkg_id,
                "name": info.get("name", pkg_id.split(":", 1)[-1]),
                "version": info.get("version", ""),
                "description": info.get("description", ""),
                "icon": info.get("icon", ""),
                "source": pkg_id.split(":", 1)[0],
                "installed": True,
            })

        if cls.pacman_available():
            try:
                results.extend(PacmanBackend.popular())
            except Exception:
                pass

        if cls.flatpak_available() and source in ("all", "flatpak"):
            try:
                results.extend(FlatpakBackend.popular())
            except Exception:
                pass

        if cls.aur_available() and source in ("all", "aur"):

            aur_results = []
            done = threading.Event()
            AurBackend.popular(callback=lambda r: (
                aur_results.extend(r),
                done.set()
            ))
            done.wait(timeout=10)
            results.extend(aur_results)

        seen = set()
        deduped = []

        for pkg in results:
            if pkg["id"] in seen:
                continue
            seen.add(pkg["id"])
            deduped.append(pkg)

        results = deduped

        results.sort(key=lambda p: (
            not p.get("installed", False),
            not p.get("featured", False),
            p.get("name", "").lower()
        ))

        return results

    @classmethod
    def _search_blocking(cls, query, source):

        results = []

        if source in ("all", "pacman") and cls.pacman_available():

            try:
                results.extend(PacmanBackend.search(query))
            except Exception:
                pass

        if source in ("all", "flatpak") and cls.flatpak_available():

            flatpak_results = []

            done = threading.Event()
            FlatpakBackend.search(query, callback=lambda r: (
                flatpak_results.extend(r),
                done.set()
            ))

            done.wait(timeout=30)

            results.extend(flatpak_results)

        if source in ("all", "aur") and cls.aur_available():

            aur_results = []

            done = threading.Event()
            AurBackend.search(query, callback=lambda r: (
                aur_results.extend(r),
                done.set()
            ))

            done.wait(timeout=30)

            results.extend(aur_results)

        results.sort(key=lambda p: (
            not cls.is_installed(p["id"]),
            p.get("name", "").lower()
        ))

        return results

    @classmethod
    def _search_async(cls, query, source, callback):

        def worker():

            if not query:

                results = cls._search_default_sync(source)

            else:

                results = cls._search_blocking(query, source)

            callback(results)

        threading.Thread(target=worker, daemon=True).start()

    @classmethod
    def info(cls, package_id, callback=None):

        if package_id.startswith("flatpak:"):

            app_id = package_id[len("flatpak:"):]

            if callback is None:

                import time

                result = [None]
                done = threading.Event()

                FlatpakBackend.info(app_id, callback=lambda r: (
                    result.__setitem__(0, r),
                    done.set()
                ))

                done.wait(timeout=30)
                return result[0]

            FlatpakBackend.info(app_id, callback=callback)
            return None

        if package_id.startswith("pacman:"):

            name = package_id[len("pacman:"):]

            try:
                info = PacmanBackend.info(name)
            except Exception:
                info = None

            if callback is not None:
                callback(info)

            return info

        if package_id.startswith("aur:"):

            name = package_id[len("aur:"):]

            if callback is None:

                result = [None]
                done = threading.Event()

                AurBackend.info(name, callback=lambda r: (
                    result.__setitem__(0, r),
                    done.set()
                ))

                done.wait(timeout=15)
                return result[0]

            AurBackend.info(name, callback=callback)
            return None

        if callback is not None:
            callback(None)

        return None

    @classmethod
    def install(cls, package_id, callback=None):

        helper = ["churros-pkexec"]

        if package_id.startswith("flatpak:"):

            app_id = package_id[len("flatpak:"):]
            cmd = helper + ["flatpak", "install", "-y", "flathub", app_id]

        elif package_id.startswith("pacman:"):

            name = package_id[len("pacman:"):]
            cmd = helper + ["pacman", "-S", "--noconfirm", name]

        elif package_id.startswith("aur:"):

            helper_bin = AurBackend.helper()
            if not helper_bin:
                if callback:
                    callback(False, "AUR helper no disponible")
                return
            name = package_id[len("aur:"):]
            cmd = helper + [helper_bin, "-S", "--noconfirm", name]

        else:
            if callback:
                callback(False, "Tipo de paquete desconocido")
            return

        cls._run(cmd, callback, success_message=f"Instalado: {package_id}")

    @classmethod
    def remove(cls, package_id, callback=None):

        helper = ["churros-pkexec"]

        if package_id.startswith("flatpak:"):

            app_id = package_id[len("flatpak:"):]
            cmd = helper + ["flatpak", "uninstall", "-y", app_id]

        elif package_id.startswith("pacman:"):

            name = package_id[len("pacman:"):]
            cmd = helper + ["pacman", "-R", "--noconfirm", name]

        elif package_id.startswith("aur:"):

            helper_bin = AurBackend.helper()
            if not helper_bin:
                if callback:
                    callback(False, "AUR helper no disponible")
                return
            name = package_id[len("aur:"):]
            cmd = helper + [helper_bin, "-Rns", "--noconfirm", name]

        else:
            if callback:
                callback(False, "Tipo de paquete desconocido")
            return

        cls._run(cmd, callback, success_message=f"Desinstalado: {package_id}")

    @classmethod
    def _run(cls, cmd, callback, success_message=""):

        def worker():

            ok = False
            message = ""

            try:

                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300
                )

                ok = result.returncode == 0
                message = (
                    success_message
                    if ok
                    else (result.stderr.strip() or result.stdout.strip() or "Comando fallo")
                )

            except FileNotFoundError:

                ok = False
                message = "pkexec no esta instalado"

            except Exception as exc:

                ok = False
                message = str(exc)

            cls.invalidate_installed_cache()

            if callback:
                callback(ok, message)

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
