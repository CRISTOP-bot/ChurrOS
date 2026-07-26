import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from widgets.row import Row


class SelectRow(Row):

    group = None

    def __init__(
        self,
        title,
        subtitle=None,
        icon=None,
        active=False,
        callback=None
    ):

        self.title = title
        self.callback = callback

        self.check = Gtk.CheckButton()

        self.check.set_can_focus(False)
        self.check.set_focusable(False)
        self.check.set_active(active)

        # Grupo compartido entre SelectRows instancia a instancia
        if SelectRow.group is not None:
            self.check.set_group(SelectRow.group)
        else:
            SelectRow.group = self.check

        super().__init__(
            title=title,
            subtitle=subtitle,
            icon=icon,
            suffix=self.check
        )

        # Click en la fila -> toggle del check (y emite toggled)
        self.connect("clicked", self.on_row_clicked)

        # Click directo en el check -> callback
        self.check.connect("toggled", self.on_toggled)

    def on_row_clicked(self, *args):
        # Hacer que el check se active (y desactive el anterior del grupo)
        if not self.check.get_active():
            self.check.set_active(True)
        # toggled emite auto => callback ejecutado

    def on_toggled(self, *args):
        # Solo llama al callback cuando se activa (no cuando se desactiva)
        if self.check.get_active() and self.callback is not None:
            self.callback()

    def set_active(self, active):
        if active != self.check.get_active():
            self.check.set_active(active)
        # No llamamos callback aquí: sólo el usuario hace toggle => callback

    def get_active(self):
        return self.check.get_active()

    @classmethod
    def reset_group(cls):
        """Llamar al crear una nueva página para reiniciar el grupo de selección."""
        cls.group = None
