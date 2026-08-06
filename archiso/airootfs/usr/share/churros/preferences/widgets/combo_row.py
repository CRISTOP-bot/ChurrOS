import os
import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

ICON_DIR = os.path.join(
    os.path.dirname(__file__),
    "..",
    "assets",
    "icons"
)


class ComboRow(Gtk.Box):

    def __init__(
        self,
        title,
        values,
        selected=None,
        subtitle=None,
        icon=None,
        callback=None
    ):

        super().__init__(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=14
        )

        self.add_css_class("row")

        self.set_margin_top(12)
        self.set_margin_bottom(12)
        self.set_margin_start(14)
        self.set_margin_end(14)

        self.callback = callback

        if icon is not None:

            image = Gtk.Image.new_from_file(
                os.path.join(ICON_DIR, icon)
            )
            image.set_pixel_size(22)
            self.append(image)

        labels = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=2
        )
        labels.set_hexpand(True)

        title_label = Gtk.Label(label=title)
        title_label.set_xalign(0)
        title_label.add_css_class("row-title")
        labels.append(title_label)

        if subtitle is not None:

            sub_label = Gtk.Label(label=subtitle)
            sub_label.set_xalign(0)
            sub_label.add_css_class("row-subtitle")
            labels.append(sub_label)

        self.append(labels)

        self.combo = Gtk.DropDown()

        model = Gtk.StringList()

        for value in values:
            model.append(value)

        self.combo.set_model(model)

        if selected in values:
            self.combo.set_selected(values.index(selected))

        self.combo.set_valign(Gtk.Align.CENTER)

        self.combo.connect(
            "notify::selected",
            self.on_changed
        )

        self.append(self.combo)

    def on_changed(
        self,
        combo,
        param
    ):

        if self.callback is None:
            return

        item = combo.get_selected_item()

        if item is None:
            return

        self.callback(item.get_string())

    def value(self):

        item = self.combo.get_selected_item()

        if item is None:
            return None

        return item.get_string()

    def set_values(
        self,
        values,
        selected=None
    ):

        # Avoid spurious notify::selected while rebuilding
        handler = self.combo.disconnect_by_func(
            self.on_changed
        ) if self.callback is not None else None

        model = Gtk.StringList()

        for value in values:
            model.append(value)

        self.combo.set_model(model)

        if selected in values:
            self.combo.set_selected(values.index(selected))

        if self.callback is not None:
            self.combo.connect("notify::selected", self.on_changed)