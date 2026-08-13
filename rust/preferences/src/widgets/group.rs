// ==========================================
// Group — tarjeta con título y separadores entre filas
// (equivalente a widgets/group.py)
// ==========================================

use gtk::prelude::*;

use crate::widgets::AsWidget;

pub struct Group {
    pub root: gtk::Box,
    pub card: gtk::Box,
    first: bool,
}

impl Group {
    pub fn new(title: &str) -> Self {
        let root = gtk::Box::new(gtk::Orientation::Vertical, 10);
        root.set_margin_bottom(24);

        let label = gtk::Label::builder()
            .label(title)
            .xalign(0.0)
            .build();
        label.add_css_class("group-title");
        root.append(&label);

        let card = gtk::Box::new(gtk::Orientation::Vertical, 0);
        card.add_css_class("group-card");
        root.append(&card);

        Self {
            root,
            card,
            first: true,
        }
    }

    pub fn widget(&self) -> &gtk::Box {
        &self.root
    }

    pub fn clear(&mut self) {
        while let Some(child) = self.card.first_child() {
            self.card.remove(&child);
        }
        self.first = true;
    }

    pub fn add(&mut self, widget: &impl AsWidget) {
        if !self.first {
            let separator = gtk::Separator::new(gtk::Orientation::Horizontal);
            separator.add_css_class("group-separator");
            self.card.append(&separator);
        }
        self.card.append(widget.widget());
        self.first = false;
    }
}
