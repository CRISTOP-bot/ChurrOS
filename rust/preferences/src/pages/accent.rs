// ==========================================
// AccentPage — color de acento del sistema
// (equivalente a pages/accent.py)
// ==========================================

use std::cell::RefCell;
use std::rc::Rc;

use crate::services::accent::AccentService;
use crate::widgets::group::Group;
use crate::widgets::page::Page;
use crate::widgets::select_row::{SelectGroup, SelectRow};

pub fn build(navigator: gtk::Stack) -> Page {
    let page = Page::new(
        Some(navigator),
        "Color de acento",
        Some("Personaliza el color principal del sistema"),
        Some("appearance".to_string()),
    );

    let mut group = Group::new("Colores");

    // Grupo de selección compartido entre las filas (como SelectRow.reset_group)
    let select_group: SelectGroup = SelectGroup::new(None);
    let current = AccentService::current();
    let rows: Rc<RefCell<Vec<SelectRow>>> = Rc::new(RefCell::new(Vec::new()));

    for color in AccentService::COLORS {
        let color_name = color.0;
        let active = color_name == current;

        // Callback: al seleccionar, aplicar color + refrescar filas
        let rows_rc = Rc::clone(&rows);
        let select_group_rc = &select_group;

        let row = SelectRow::new(
            color_name,
            None,
            None,
            active,
            select_group_rc.borrow().as_ref(),
            Some(Box::new(move |name| {
                AccentService::set(name);
                reload_accent_css();
                let new_current = AccentService::current();
                for r in rows_rc.borrow().iter() {
                    r.set_active(r.title == new_current);
                }
            })),
        );

        // Registrar el primer check como raíz del grupo
        if select_group.borrow().is_none() {
            *select_group.borrow_mut() = Some(row.check.clone());
        }

        group.add(&row);
        rows.borrow_mut().push(row);
    }

    page.add(group.widget());

    page
}

/// Recarga accent.css en runtime (equivalente a AccentPage._reload_accent_css)
fn reload_accent_css() {
    let accent_css = AccentService::accent_css_path();
    if !accent_css.exists() {
        return;
    }

    let provider = gtk::CssProvider::new();
    provider.load_from_path(&accent_css);

    if let Some(display) = gtk::gdk::Display::default() {
        gtk::style_context_add_provider_for_display(
            &display,
            &provider,
            gtk::STYLE_PROVIDER_PRIORITY_USER + 1,
        );
    }
}
