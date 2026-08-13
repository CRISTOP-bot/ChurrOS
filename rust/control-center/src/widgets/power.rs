// ==========================================
// power.rs — botón de encendido (port de widgets/power.py)
// ==========================================

use gtk::prelude::*;

use super::super::assets;
use super::open_popup;

pub struct PowerButton {
    button: gtk::Button,
}

impl PowerButton {
    pub fn new(window: &gtk::ApplicationWindow) -> Self {
        let button = gtk::Button::new();
        button.add_css_class("power-button");

        let image = gtk::Image::from_file(assets::icon_path("powerbutton.svg"));
        image.set_pixel_size(24);

        button.set_child(Some(&image));

        let win = window.clone();
        button.connect_clicked(move |_| {
            open_popup(&win, "power");
        });

        Self { button }
    }

    pub fn button(&self) -> &gtk::Button {
        &self.button
    }
}