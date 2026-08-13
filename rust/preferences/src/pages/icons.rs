// ==========================================
// IconsPage — temas de iconos (equivalente a pages/icons.py)
// ==========================================

use std::cell::RefCell;
use std::rc::Rc;

use crate::services::icons::IconsService;
use crate::widgets::group::Group;
use crate::widgets::page::Page;
use crate::widgets::select_row::{SelectGroup, SelectRow};

pub fn build(navigator: gtk::Stack) -> Page {
    let page = Page::new(
        Some(navigator),
        "Iconos",
        Some("Selecciona el tema de iconos"),
        Some("appearance".to_string()),
    );

    // SelectRow.reset_group() — grupo de selección compartido entre las filas
    let select_group: SelectGroup = SelectGroup::new(None);

    let mut group = Group::new("Temas disponibles");

    let current = IconsService::current();
    let rows: Rc<RefCell<Vec<SelectRow>>> = Rc::new(RefCell::new(Vec::new()));

    for theme in IconsService::available() {
        let theme_name = theme.clone();
        let active = theme == current;

        // Callback: aplicar el tema + refrescar las filas (equivalente a self.select)
        let rows_rc = Rc::clone(&rows);

        let row = SelectRow::new(
            &theme,
            None,
            None,
            active,
            select_group.borrow().as_ref(),
            Some(Box::new(move |_| {
                IconsService::set(&theme_name);
                let new_current = IconsService::current();
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
