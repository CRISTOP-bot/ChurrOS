import os
import sys
import traceback

LOG = os.environ.get(
    "CHURROS_SETTINGS_LOG",
    "/tmp/churros-settings.log"
)


def log(msg):

    try:

        with open(LOG, "a") as f:
            f.write(msg + "\n")

    except Exception:

        try:

            sys.stderr.write(msg + "\n")
            sys.stderr.flush()

        except Exception:
            pass


log("")
log("=== main.py start pid=" + str(os.getpid()))
log("WAYLAND_DISPLAY=" + str(os.environ.get("WAYLAND_DISPLAY")))
log("XDG_RUNTIME_DIR=" + str(os.environ.get("XDG_RUNTIME_DIR")))
log("GDK_BACKEND=" + str(os.environ.get("GDK_BACKEND")))
log("DISPLAY=" + str(os.environ.get("DISPLAY")))

if not os.environ.get("WAYLAND_DISPLAY"):

    xrd = os.environ.get("XDG_RUNTIME_DIR") or \
        ("/run/user/" + str(os.getuid()))

    if os.path.isdir(xrd):

        for sock in sorted(os.listdir(xrd)):

            if sock.startswith("wayland-"):

                os.environ["WAYLAND_DISPLAY"] = sock
                log("autodetect WAYLAND_DISPLAY=" + sock)
                break

os.environ.setdefault("GDK_BACKEND", "wayland")
os.environ.setdefault("NO_AT_BRIDGE", "1")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:

    import gi

    gi.require_version("Gtk", "4.0")

    from gi.repository import Gtk, Gdk

except Exception as exc:

    log("FATAL: gi/Gtk import fallo: " + repr(exc))
    log(traceback.format_exc())
    sys.exit(1)

try:

    from services.accent import AccentService
    from window import PreferencesWindow

except Exception as exc:

    log("FATAL: imports locales fallo: " + repr(exc))
    log(traceback.format_exc())
    sys.exit(1)


class PreferencesApplication(Gtk.Application):

    def __init__(self):

        super().__init__(
            application_id="org.churros.preferences"
        )

    def _load_css(self, path, priority):

        if not os.path.exists(path):

            log("CSS no existe: " + path)
            return

        try:

            provider = Gtk.CssProvider()

            provider.load_from_path(path)

            display = Gdk.Display.get_default()

            if display is None:

                log("Gdk.Display.get_default() = None; skip CSS " + path)
                return

            Gtk.StyleContext.add_provider_for_display(
                display,
                provider,
                priority
            )

            log("CSS cargado: " + path)

        except Exception as exc:

            log("No se pudo cargar CSS " + path + ": " + repr(exc))

    def do_activate(self):

        log("[preferences] do_activate")

        try:

            AccentService.ensure()

        except Exception as e:

            log("[preferences] AccentService fallo: " + repr(e))

        base = os.path.dirname(os.path.abspath(__file__))

        shared = "/usr/share/churros/styles/churros.css"

        self._load_css(shared, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self._load_css(
            os.path.join(base, "style.css"),
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION + 1
        )

        accent_css = AccentService.ACCENT_CSS

        self._load_css(accent_css, Gtk.STYLE_PROVIDER_PRIORITY_USER)

        try:

            window = PreferencesWindow(self)
            window.present()
            log("[preferences] ventana abierta")

        except Exception as e:

            log("[preferences] ventana fallo: " + repr(e))
            log(traceback.format_exc())


try:

    app = PreferencesApplication()

    app.run()

except KeyboardInterrupt:

    log("[preferences] KeyboardInterrupt")
    sys.exit(0)

except Exception as exc:

    log("FATAL: app.run() fallo: " + repr(exc))
    log(traceback.format_exc())
    sys.exit(1)
