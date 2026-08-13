// ==========================================
// Search — entrada de búsqueda con señal "search"
// (equivalente a widgets/search.py)
// ==========================================

use gtk::prelude::*;

use std::cell::RefCell;
use std::rc::Rc;

pub struct Search {
    pub entry: gtk::SearchEntry,
    callbacks: Rc<RefCell<Vec<Box<dyn Fn(&str)>>>>,
}

impl Search {
    pub fn new() -> Self {
        let entry = gtk::SearchEntry::new();
        entry.set_placeholder_text(Some("Buscar configuración..."));
        entry.add_css_class("preferences-search");

        let callbacks: Rc<RefCell<Vec<Box<dyn Fn(&str)>>>> =
            Rc::new(RefCell::new(Vec::new()));

        // Cablear la señal GTK en el constructor: los callbacks se registran
        // después con connect_search().
        let cb_rc = Rc::clone(&callbacks);
        entry.connect_search_changed(move |entry| {
            let text = entry.text().to_string();
            for cb in cb_rc.borrow().iter() {
                cb(&text);
            }
        });

        Search { entry, callbacks }
    }

    pub fn widget(&self) -> &gtk::SearchEntry {
        &self.entry
    }

    pub fn connect_search(&self, cb: impl Fn(&str) + 'static) {
        self.callbacks.borrow_mut().push(Box::new(cb));
    }

    pub fn set_text(&self, text: &str) {
        self.entry.set_text(text);
    }
}
