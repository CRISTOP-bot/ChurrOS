// ==========================================
// CursorPage — tema y tamaño del cursor (equivalente a pages/cursor.py)
// ==========================================

use std::cell::RefCell;
use std::rc::Rc;

use crate::services::cursor::CursorService;
use crate::widgets::group::Group;
use crate::widgets::page::Page;
use crate::widgets::select_row::{SelectGroup, SelectRow};
use crate::widgets::slider_row::SliderRow;

pub fn build(navigator: gtk::Stack) -> Page {
    let page = Page::new(
        Some(navigator),
        "Cursor",
        Some("Selecciona el tema y tamano del cursor"),
        Some("appearance".to_string()),
    );

    // SelectRow.reset_group()
    let select_group: SelectGroup = SelectGroup::new(None);

    let rows: Rc<RefCell<Vec<SelectRow>>> = Rc::new(RefCell::new(Vec::new()));

    // ===== Tema =====
    let mut group = Group::new("Temas disponibles");

    let current = CursorService::current();

    for cursor in CursorService::available() {
        let cursor_name = cursor.clone();
        let active = cursor == current;

        // Callback: aplicar el tema + refrescar las filas (equivalente a self.select)
        let rows_rc = Rc::clone(&rows);

        let row = SelectRow::new(
            &cursor,
            None,
            None,
            active,
            select_group.borrow().as_ref(),
            Some(Box::new(move |_| {
                CursorService::set(&cursor_name);
                let new_current = CursorService::current();
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

    // ===== Tamano =====
    let mut size_group = Group::new("Tamano del cursor");

    let size_slider = SliderRow::new(
        "Tamano",
        None,
        None,
        8.0,
        64.0,
        1.0,
        CursorService::size(),
        Some(Box::new(on_size_changed)),
    );

    // SliderRow no implementa AsWidget; se añade su Row interno (contiene la scale)
    size_group.add(&size_slider.row);

    page.add(size_group.widget());

    page
}

/// Equivalente a CursorPage.on_size_changed:
/// CursorService.set_size + NiriConfig.set_cursor_size (try/except en el Python;
/// aquí set_size ya silencia los fallos de niri).
fn on_size_changed(size: f64) {
    CursorService::set_size(size);
}
