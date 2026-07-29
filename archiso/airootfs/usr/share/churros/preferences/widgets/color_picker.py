import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, Gdk


def hex_to_rgba(hex_color, alpha=1.0):

    hex_color = hex_color.lstrip("#")

    if len(hex_color) != 6:
        return Gdk.RGBA(red=1, green=1, blue=1, alpha=alpha)

    r = int(hex_color[0:2], 16) / 255
    g = int(hex_color[2:4], 16) / 255
    b = int(hex_color[4:6], 16) / 255

    return Gdk.RGBA(red=r, green=g, blue=b, alpha=alpha)


def rgba_to_hex(rgba):

    r = max(0, min(255, int(rgba.red * 255)))
    g = max(0, min(255, int(rgba.green * 255)))
    b = max(0, min(255, int(rgba.blue * 255)))

    return "#{:02x}{:02x}{:02x}".format(r, g, b)


class ColorPickerRow(Gtk.Box):

    def __init__(self, title, value, callback=None):

        super().__init__(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=12
        )

        self.add_css_class("row")

        self.set_margin_top(10)
        self.set_margin_bottom(10)
        self.set_margin_start(14)
        self.set_margin_end(14)

        self.color = value
        self.callback = callback

        self._swatch = Gtk.DrawingArea()
        self._swatch.set_size_request(40, 28)
        self._swatch.set_valign(Gtk.Align.CENTER)
        self._swatch.add_css_class("color-swatch")

        self._label = Gtk.Label(label=title)
        self._label.set_xalign(0)
        self._label.set_hexpand(True)
        self._label.add_css_class("row-title")

        self._value_label = Gtk.Label(label=value)
        self._value_label.set_xalign(1)
        self._value_label.add_css_class("row-value")

        self._button = Gtk.Button(label="Elegir")
        self._button.add_css_class("color-pick-button")
        self._button.set_valign(Gtk.Align.CENTER)
        self._button.connect("clicked", self._on_pick)

        self.append(self._label)
        self.append(self._swatch)
        self.append(self._value_label)
        self.append(self._button)

        self._swatch.set_draw_func(self._draw_swatch, None)

    def _draw_swatch(self, area, cr, w, h, user_data):

        try:
            rgba = hex_to_rgba(self.color, 1.0)
        except Exception:
            rgba = Gdk.RGBA(red=1, green=1, blue=1, alpha=1.0)

        cr.set_source_rgba(rgba.red, rgba.green, rgba.blue, rgba.alpha)
        cr.rectangle(0, 0, w, h)
        cr.fill()

    def _on_pick(self, *_):

        dialog = Gtk.ColorDialog()
        dialog.set_title("Elegir color")

        try:
            rgba = hex_to_rgba(self.color, 1.0)
        except Exception:
            rgba = Gdk.RGBA(red=0.85, green=0.55, blue=0.21, alpha=1.0)

        def on_result(d, result):

            try:
                picked = d.choose_rgba_finish(result)
            except Exception:
                return

            if picked is None:
                return

            self.color = rgba_to_hex(picked)
            self._value_label.set_label(self.color)
            self._swatch.queue_draw()

            if self.callback is not None:
                self.callback(self.color)

        try:
            dialog.choose_rgba(
                self.get_root(),
                None,
                on_result,
                rgba
            )
        except Exception as exc:
            print("[color-picker] dialog fallo:", exc)

    def get_value(self):

        return self.color
