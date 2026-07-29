import json
import os
import shutil
import subprocess
import threading
import urllib.request
import urllib.error


FLATHUB_API = "https://flathub.org/api/v2"

CACHE_DIR = os.path.expanduser("~/.cache/churros/flatpak")
INDEX_PATH = os.path.join(CACHE_DIR, "index.json")
INDEX_MAX_AGE = 86400  # 1 day


def _ensure_cache_dir():
    os.makedirs(CACHE_DIR, exist_ok=True)


def _is_cache_fresh():

    if not os.path.exists(INDEX_PATH):
        return False

    import time
    age = time.time() - os.path.getmtime(INDEX_PATH)
    return age < INDEX_MAX_AGE


def _download_index():

    _ensure_cache_dir()

    try:

        with urllib.request.urlopen(
            f"{FLATHUB_API}/appstream",
            timeout=20
        ) as r:
            data = json.loads(r.read().decode())

        with open(INDEX_PATH, "w") as f:
            json.dump(data, f)

        return data

    except Exception:
        return None


def _load_index():

    if _is_cache_fresh():

        try:
            with open(INDEX_PATH) as f:
                return json.load(f)
        except Exception:
            pass

    data = _download_index()

    if data is not None:
        return data

    if os.path.exists(INDEX_PATH):

        try:
            with open(INDEX_PATH) as f:
                return json.load(f)
        except Exception:
            pass

    return []


def _fetch_index_async(callback):

    def worker():

        data = _load_index()
        callback(data or [])

    threading.Thread(target=worker, daemon=True).start()


class FlatpakBackend:

    @staticmethod
    def available():
        return shutil.which("flatpak") is not None

    @staticmethod
    def remotes():

        if not FlatpakBackend.available():
            return []

        try:

            result = subprocess.run(
                ["flatpak", "remotes", "--columns=name"],
                capture_output=True,
                text=True,
                timeout=5
            )

            remotes = []

            for line in result.stdout.splitlines():

                name = line.strip()

                if name and name != "Name":
                    remotes.append(name)

            return remotes

        except Exception:
            return []

    @staticmethod
    def index(callback):

        def deliver(data):

            def _build():

                results = []

                for app_id in data:

                    if isinstance(app_id, str):

                        results.append({
                            "id": f"flatpak:{app_id}",
                            "name": app_id,
                            "app_id": app_id,
                            "version": "",
                            "description": "",
                            "icon": "",
                            "source": "flatpak",
                            "installed": False,
                        })

                callback(results)

            threading.Thread(target=_build, daemon=True).start()

        _fetch_index_async(deliver)

    @staticmethod
    def search(query="", callback=None):

        def deliver(index_data):

            def _filter():

                matches = []

                q = query.lower().strip()

                for app_id in index_data:

                    if not isinstance(app_id, str):
                        continue

                    if q and q not in app_id.lower():

                        continue

                    matches.append(app_id)

                return matches[:200]

            ids = _filter()

            def _build_results():

                results = []

                for app_id in ids:

                    meta = FlatpakBackend._load_meta(app_id)

                    icon_url = FlatpakBackend._best_icon(meta) if meta else ""

                    name = app_id

                    summary = ""

                    if meta:

                        name = meta.get("name", app_id)
                        summary = meta.get("summary", "")

                    results.append({
                        "id": f"flatpak:{app_id}",
                        "name": name,
                        "app_id": app_id,
                        "version": (meta or {}).get("currentReleaseVersion", ""),
                        "description": summary,
                        "icon": icon_url,
                        "source": "flatpak",
                        "installed": False,
                    })

                callback(results)

            threading.Thread(target=_build_results, daemon=True).start()

        _fetch_index_async(deliver)

    @staticmethod
    def info(app_id, callback=None):

        def deliver(meta):

            if meta is None:
                callback(None)
                return

            info = {
                "id": f"flatpak:{app_id}",
                "name": meta.get("name", app_id),
                "app_id": app_id,
                "version": meta.get("currentReleaseVersion", ""),
                "description": meta.get("description", meta.get("summary", "")),
                "summary": meta.get("summary", ""),
                "developer": meta.get("developer_name", ""),
                "license": meta.get("project_license", ""),
                "homepage": meta.get("homepage", ""),
                "categories": meta.get("categories", []),
                "icon": FlatpakBackend._best_icon(meta),
                "screenshots": FlatpakBackend._screenshots(meta),
                "source": "flatpak",
                "installed": False,
            }

            callback(info)

        FlatpakBackend._fetch_meta_async(app_id, deliver)

    @staticmethod
    def installed():

        if not FlatpakBackend.available():
            return {}

        installed = {}

        try:

            r = subprocess.run(
                ["flatpak", "list", "--columns=application,name"],
                capture_output=True,
                text=True,
                timeout=10
            )

            for line in r.stdout.splitlines():

                parts = line.split("\t")

                if len(parts) < 2:
                    continue

                app_id = parts[0].strip()
                name = parts[1].strip() if len(parts) > 1 else app_id

                if not app_id:
                    continue

                installed[app_id] = {
                    "id": f"flatpak:{app_id}",
                    "name": name,
                    "app_id": app_id,
                    "source": "flatpak",
                    "installed": True,
                }

        except Exception:
            pass

        return installed

    @staticmethod
    def _best_icon(meta):

        icons = meta.get("icons", []) or []

        for icon in icons:

            if isinstance(icon, dict):

                url = icon.get("url") or icon.get("cached")
                if url:
                    return url

            elif isinstance(icon, str):
                return icon

        return ""

    @staticmethod
    def _screenshots(meta):

        shots = []

        for shot in meta.get("screenshots", []) or []:

            if not isinstance(shot, dict):
                continue

            for sub in shot.get("shots", []) or []:

                if isinstance(sub, dict) and sub.get("url"):

                    shots.append(sub["url"])

        return shots[:4]

    @staticmethod
    def _meta_path(app_id):

        safe = app_id.replace("/", "_").replace(".", "_")
        return os.path.join(CACHE_DIR, f"app_{safe}.json")

    @staticmethod
    def _meta_cache_fresh(path):

        if not os.path.exists(path):
            return False

        import time
        age = time.time() - os.path.getmtime(path)
        return age < 604800  # 7 days

    @staticmethod
    def _load_meta(app_id):

        path = FlatpakBackend._meta_path(app_id)

        if FlatpakBackend._meta_cache_fresh(path):

            try:
                with open(path) as f:
                    return json.load(f)
            except Exception:
                pass

        return None

    @staticmethod
    def _fetch_meta_async(app_id, callback):

        def worker():

            path = FlatpakBackend._meta_path(app_id)

            try:

                with urllib.request.urlopen(
                    f"{FLATHUB_API}/appstream/{app_id}",
                    timeout=10
                ) as r:
                    meta = json.loads(r.read().decode())

                try:
                    os.makedirs(CACHE_DIR, exist_ok=True)
                    with open(path, "w") as f:
                        json.dump(meta, f)
                except Exception:
                    pass

            except Exception:
                meta = FlatpakBackend._load_meta(app_id)

            callback(meta)

        threading.Thread(target=worker, daemon=True).start()

    @staticmethod
    def popular():

        if not FlatpakBackend.available():
            return []

        data = _load_index() or []

        if not isinstance(data, list):
            return []

        sample = data[:30]

        results = []

        for app_id in sample:

            meta = FlatpakBackend._load_meta(app_id)

            results.append({
                "id": f"flatpak:{app_id}",
                "name": (meta or {}).get("name", app_id),
                "app_id": app_id,
                "version": (meta or {}).get("currentReleaseVersion", ""),
                "description": (meta or {}).get("summary", ""),
                "icon": (meta or {}).get("icon", "") or FlatpakBackend._best_icon(meta or {}),
                "source": "flatpak",
                "installed": False,
                "featured": True,
            })

        return results
