// ==========================================
// SelectRow — fila con checkbutton de selección única por grupo
// (equivalente a widgets/select_row.py)
// ==========================================

use gtk::prelude::*;

use std::cell::RefCell;

use crate::widgets::row::Row;

pub struct SelectRow {
    pub row: Row,
    pub check: gtk::CheckButton,
    pub title: String,
}

impl SelectRow {
    pub fn new(
        title: &str,
        subtitle: Option<&str>,
        icon: Option<&str>,
        active: bool,
        group: Option<&gtk::CheckButton>,
        callback: Option<Box<dyn Fn(&str)>>,
    ) -> Self {
        let check = gtk::CheckButton::new();
        check.set_can_focus(false);
        check.set_focusable(false);
        check.set_active(active);

        // Grupo compartido: el primer check del grupo es la raíz
        if let Some(root) = group {
            check.set_group(Some(root));
        }

        let title_owned = title.to_string();
        let check_widget: &gtk::Widget = check.upcast_ref();
        let row = Row::new(
            title,
            subtitle,
            icon,
            None,
            Some(check_widget),
            None, // el clic en la fila se maneja abajo
        );

        // Click en la fila -> activar el check (el grupo desactiva el resto)
        let check_clone = check.clone();
        let title_cb = title_owned.clone();
        let cb = callback;
        row.widget().connect_clicked(move |_| {
            if !check_clone.is_active() {
                check_clone.set_active(true);
            }
        });

        // Toggled -> callback solo cuando se activa
        if let Some(cb) = cb {
            let title_for_cb = title_cb.clone();
            check.connect_toggled(move |check| {
                if check.is_active() {
                    cb(&title_for_cb);
                }
            });
        }

        Self {
            row,
            check,
            title: title_owned,
        }
    }

    pub fn widget(&self) -> &gtk::Button {
        self.row.widget()
    }

    pub fn set_active(&self, active: bool) {
        if active != self.check.is_active() {
            self.check.set_active(active);
        }
    }

    pub fn get_active(&self) -> bool {
        self.check.is_active()
    }
}

// Grupo de selección por página: RefCell<Option<CheckButton>> compartido
pub type SelectGroup = RefCell<Option<gtk::CheckButton>>;
