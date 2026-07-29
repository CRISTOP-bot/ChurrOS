import os
import shutil
import subprocess


class PacmanBackend:

    @staticmethod
    def available():
        return shutil.which("pacman") is not None

    @staticmethod
    def search(query=""):

        if not PacmanBackend.available():
            return []

        cmd = ["pacman", "-Ss", "--quiet", query] if query else ["pacman", "-Ss", "--quiet"]

        try:

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=15
            )

            return PacmanBackend._parse_search(result.stdout)

        except Exception:
            return []

    @staticmethod
    def info(name):

        if not PacmanBackend.available():
            return None

        try:

            result = subprocess.run(
                ["pacman", "-Si", name],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                return None

            return PacmanBackend._parse_info(result.stdout)

        except Exception:
            return None

    @staticmethod
    def installed():

        if not PacmanBackend.available():
            return []

        try:

            result = subprocess.run(
                ["pacman", "-Qq"],
                capture_output=True,
                text=True,
                timeout=10
            )

            names = [line.strip() for line in result.stdout.splitlines() if line.strip()]

            installed = {}

            for name in names:

                try:

                    r = subprocess.run(
                        ["pacman", "-Qi", name],
                        capture_output=True,
                        text=True,
                        timeout=2
                    )

                    if r.returncode == 0:
                        info = PacmanBackend._parse_info(r.stdout)
                        if info:
                            installed[name] = info

                except Exception:
                    continue

            return installed

        except Exception:
            return {}

    @staticmethod
    def _parse_search(text):

        packages = []
        lines = text.splitlines()

        for i in range(0, len(lines) - 1, 2):

            header = lines[i].strip()
            description = lines[i + 1].strip() if i + 1 < len(lines) else ""

            if not header or "/" not in header:
                continue

            try:

                repo, name = header.split(" ", 1)
                repo = repo.strip()
                name_part = name.strip()

                if " " in name_part:
                    version = name_part.split(" ", 1)[1]
                    name_clean = name_part.split(" ", 1)[0]
                else:
                    version = ""
                    name_clean = name_part

                if name_clean.startswith("["):

                    end = name_clean.find("]")
                    if end > 0:
                        installed_marker = name_clean[1:end]
                        name_clean = name_clean[end + 1:].strip()
                    else:
                        installed_marker = ""
                else:
                    installed_marker = ""

                packages.append({
                    "id": f"pacman:{name_clean}",
                    "name": name_clean,
                    "version": version,
                    "description": description,
                    "repo": repo,
                    "source": "pacman",
                    "installed": "installed" in installed_marker.lower(),
                })

            except Exception:
                continue

        return packages

    @staticmethod
    def _parse_info(text):

        info = {}

        for line in text.splitlines():

            if ":" not in line:
                continue

            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip()

            if key in (
                "Name",
                "Version",
                "Description",
                "URL",
                "Licenses",
                "Repository",
                "Installed Size",
                "Download Size",
                "Depends On",
                "Optional Deps",
                "Provides",
                "Required By",
                "Optional For",
                "Conflicts With",
                "Replaces",
                "Downloaded From",
                "Groups",
                "Packager",
                "Maintainer",
                "Validated By",
                "Build Date",
                "Install Date",
                "Install Reason",
                "Last Modified",
                "Installed Reason",
            ):
                info[key.lower().replace(" ", "_")] = value

        if "name" in info:
            info["id"] = f"pacman:{info['name']}"
            info["source"] = "pacman"

        return info if info else None

    @staticmethod
    def popular():

        keywords = [
            "firefox",
            "chromium",
            "vlc",
            "mpv",
            "gimp",
            "inkscape",
            "blender",
            "thunderbird",
            "libreoffice",
            "code",
            "git",
            "neovim",
            "obs-studio",
            "steam",
            "lutris",
            "spotify",
            "telegram",
            "discord",
            "keepassxc",
            "godot",
            "darktable",
            "audacity",
            "kdenlive",
            "krita",
            "obsidian",
        ]

        results = []
        seen = set()

        for keyword in keywords:

            try:
                pkgs = PacmanBackend.search(keyword)

                for pkg in pkgs:
                    if pkg["name"] in seen:
                        continue

                    seen.add(pkg["name"])
                    pkg["featured"] = True
                    results.append(pkg)

                    if len(results) >= 30:
                        return results

            except Exception:
                continue

        return results
