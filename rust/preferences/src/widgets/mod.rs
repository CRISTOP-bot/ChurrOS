pub mod group;
pub mod navigation_row;
pub mod page;
pub mod row;
pub mod search;
pub mod select_row;
pub mod sidebar;
pub mod sidebar_item;
pub mod switch_row;

use gtk::prelude::*;

/// Trait para widgets envueltos (Row, Group, ...): expone el widget GTK
/// interno para poder añadirlos a contenedores.
pub trait AsWidget {
    fn widget(&self) -> &gtk::Widget;
}

impl AsWidget for row::Row {
    fn widget(&self) -> &gtk::Widget {
        self.button.upcast_ref()
    }
}

impl AsWidget for group::Group {
    fn widget(&self) -> &gtk::Widget {
        self.root.upcast_ref()
    }
}

impl AsWidget for sidebar_item::SidebarItem {
    fn widget(&self) -> &gtk::Widget {
        self.button.upcast_ref()
    }
}

impl AsWidget for page::Page {
    fn widget(&self) -> &gtk::Widget {
        self.scrolled.upcast_ref()
    }
}

impl AsWidget for select_row::SelectRow {
    fn widget(&self) -> &gtk::Widget {
        self.row.widget().upcast_ref()
    }
}

impl AsWidget for switch_row::SwitchRow {
    fn widget(&self) -> &gtk::Widget {
        self.row.widget().upcast_ref()
    }
}
