// ==========================================
// UsersPage — cuenta del sistema y autologin
// (equivalente a pages/users.py)
// ==========================================

use gtk::prelude::*;

use crate::services::users::UsersService;
use crate::widgets::group::Group;
use crate::widgets::page::Page;
use crate::widgets::row::Row;
use crate::widgets::switch_row::SwitchRow;

pub fn build(navigator: gtk::Stack) -> Page {
    let page = Page::new(
        Some(navigator),
        "Usuarios",
        Some("Administrar cuentas del sistema"),
        None,
    );

    // Cuenta
    let mut account = Group::new("Cuenta");

    account.add(&Row::new(
        "Usuario",
        Some("Sesión actual"),
        Some("users.svg"),
        Some(&UsersService::username()),
        None,
        None,
    ));

    account.add(&Row::new(
        "Nombre",
        Some("Nombre completo"),
        Some("users.svg"),
        Some(&UsersService::full_name()),
        None,
        None,
    ));

    page.add(account.widget());

    // Seguridad
    let mut security = Group::new("Seguridad");

    security.add(&SwitchRow::new(
        "Inicio automático",
        Some("users.svg"),
        Some("Iniciar sesión automáticamente"),
        UsersService::auto_login(),
        Some(Box::new(|value| {
            UsersService::set_auto_login(value);
        })),
    ));

    page.add(security.widget());

    page
}
