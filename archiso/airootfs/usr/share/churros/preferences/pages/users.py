from widgets.page import Page
from widgets.group import Group
from widgets.row import Row
from widgets.switch_row import SwitchRow

from services.users import UsersService


class UsersPage(Page):

    def __init__(self, navigator):

        super().__init__(
            navigator,
            "Usuarios",
            "Administrar cuentas del sistema"
        )

        #
        # Usuario actual
        #

        account = Group(
            "Cuenta"
        )

        account.add(

            Row(

                title="Usuario",

                subtitle="Sesión actual",

                icon="users.svg",

                value=UsersService.username()

            )

        )

        account.add(

            Row(

                title="Nombre",

                subtitle="Nombre completo",

                icon="users.svg",

                value=UsersService.full_name()

            )

        )

        self.add(
            account
        )

        #
        # Seguridad
        #

        security = Group(
            "Seguridad"
        )

        security.add(

            SwitchRow(

                title="Inicio automático",

                subtitle="Iniciar sesión automáticamente",

                icon="users.svg",

                active=UsersService.auto_login(),

                callback=UsersService.set_auto_login

            )

        )

        self.add(
            security
        )