// ==========================================
// SidebarItem — botón del sidebar con icono + título
// (equivalente a widgets/sidebar_item.py)
// ==========================================

use gtk::prelude::*;

pub struct SidebarItem {
    pub button: gtk::Button,
}

impl SidebarItem {
    pub fn new(icon: &str, title: &str) -> Self {
        let button = gtk::Button::new();
        button.add_css_class("sidebar-item");

        let content = gtk::Box::new(gtk::Orientation::Horizontal, 12);
        content.set_margin_top(10);
        content.set_margin_bottom(10);
        content.set_margin_start(14);
        content.set_margin_end(14);

        let image = gtk::Image::from_file(crate::assets::icon_path(icon));
        image.set_pixel_size(20);
        content.append(&image);

        let label = gtk::Label::builder()
            .label(title)
            .xalign(0.0)
            .build();
        label.set_hexpand(true);
        content.append(&label);

        button.set_child(Some(&content));

        Self { button }
    }

    pub fn widget(&self) -> &gtk::Button {
        &self.button
    }

    pub fn activate(&self) {
        self.button.add_css_class("active");
        self.button.set_state_flags(gtk::StateFlags::CHECKED, false);
    }

    pub fn deactivate(&self) {
        self.button.remove_css_class("active");
        self.button.unset_state_flags(gtk::StateFlags::CHECKED);
    }
}
