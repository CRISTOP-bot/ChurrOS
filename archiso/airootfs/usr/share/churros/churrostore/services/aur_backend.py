import json
import shutil
import subprocess
import threading
import urllib.parse
import urllib.request
import urllib.error


AUR_RPC = "https://aur.archlinux.org/rpc"
AUR_WEB = "https://aur.archlinux.org"


class AurBackend:

    @staticmethod
    def available():
        return shutil.which("yay") is not None or shutil.which("paru") is not None

    @staticmethod
    def helper():

        if shutil.which("yay"):
            return "yay"

        if shutil.which("paru"):
            return "paru"

        return None

    @staticmethod
    def search(query="", callback=None):

        def worker():

            if not query:

                callback([])
                return

            url = f"{AUR_RPC}/?v=5&type=search&arg={urllib.parse.quote(query)}"

            try:

                with urllib.request.urlopen(url, timeout=15) as r:
                    data = json.loads(r.read().decode())

                results = []

                for pkg in data.get("results", []):

                    info = AurBackend._format(pkg)
                    if info:
                        results.append(info)

                callback(results)

            except Exception as exc:
                print("[aur] search fallo:", exc)
                callback([])

        threading.Thread(target=worker, daemon=True).start()

    @staticmethod
    def info(name, callback=None):

        def worker():

            url = f"{AUR_RPC}/?v=5&type=info&arg={urllib.parse.quote(name)}"

            try:

                with urllib.request.urlopen(url, timeout=10) as r:
                    data = json.loads(r.read().decode())

                results = data.get("results", [])

                if not results:
                    callback(None)
                    return

                callback(AurBackend._format(results[0]))

            except Exception as exc:
                print("[aur] info fallo:", exc)
                callback(None)

        threading.Thread(target=worker, daemon=True).start()

    @staticmethod
    def popular(callback=None):

        def worker():

            packages = [
                "spotify",
                "visual-studio-code-bin",
                "google-chrome",
                "brave-bin",
                "vscodium-bin",
                "obs-studio",
                "firefox",
                "discord",
                "zoom",
                "slack-desktop",
                "telegram-desktop-bin",
                "skypeforlinux-stable-bin",
                "etcher-bin",
                "mailspring",
                "mattermost-desktop",
                "element-desktop",
                "franz-bin",
                "dropbox",
                "nextcloud-client",
                "insync",
                "rambox-bin",
                "electronmail-bin",
                "github-desktop-bin",
                "screenshot-go",
                "bitwarden-bin",
                "1password",
                "bitwarden",
                "enpass-bin",
                "keepassxc",
                "standard-notes-bin",
            ]

            results = []

            for name in packages[:30]:

                info = AurBackend._info_sync(name)

                if info:
                    info["featured"] = True
                    results.append(info)

            callback(results)

        threading.Thread(target=worker, daemon=True).start()

    @staticmethod
    def _info_sync(name):

        url = f"{AUR_RPC}/?v=5&type=info&arg={urllib.parse.quote(name)}"

        try:

            with urllib.request.urlopen(url, timeout=8) as r:
                data = json.loads(r.read().decode())

            results = data.get("results", [])

            if results:
                return AurBackend._format(results[0])

        except Exception:
            pass

        return None

    @staticmethod
    def _format(pkg):

        name = pkg.get("Name", "")
        if not name:
            return None

        return {
            "id": f"aur:{name}",
            "name": name,
            "app_id": name,
            "version": pkg.get("Version", ""),
            "description": (pkg.get("Description") or "").strip(),
            "summary": (pkg.get("Description") or "").strip(),
            "developer": pkg.get("Maintainer", ""),
            "license": "",
            "homepage": AUR_WEB + pkg.get("URLPath", ""),
            "categories": [],
            "icon": "",
            "votes": pkg.get("NumVotes", 0),
            "popularity": pkg.get("Popularity", 0),
            "last_modified": pkg.get("LastModified", 0),
            "maintainer": pkg.get("Maintainer", ""),
            "source": "aur",
            "installed": False,
        }

    @staticmethod
    def installed():

        if not AurBackend.available():
            return {}

        helper = AurBackend.helper()

        try:

            r = subprocess.run(
                [helper, "-Qqm"],
                capture_output=True,
                text=True,
                timeout=15
            )

            installed = {}

            for line in r.stdout.splitlines():

                name = line.strip()

                if name:
                    installed[name] = {
                        "id": f"aur:{name}",
                        "name": name,
                        "app_id": name,
                        "source": "aur",
                        "installed": True,
                    }

            return installed

        except Exception:
            return {}
