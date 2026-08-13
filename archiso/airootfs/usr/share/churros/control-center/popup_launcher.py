def _open(name, window=None):

    if window is not None:
        try:
            window.close()
        except Exception:
            pass

    subprocess.Popen(
        [
            "churros-popup",
            name
        ]
    )
