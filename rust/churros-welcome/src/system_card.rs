use gtk::prelude::*;

use crate::system_info;

// La SystemCard está definida pero NO se monta en el FlowBox, igual que en el
// Python original (widgets/system_card.py existe pero cards.py nunca la añade;
// docs/apps.md dice que debería ir primera — desajuste heredado).
#[allow(dead_code)]
pub fn build() -> gtk::Box {
    let card = gtk::Box::new(gtk::Orientation::Vertical, 12);

    card.set_size_request(280, 340); // mismo tamaño que las action cards
    card.add_css_class("system-card");

    card.set_margin_top(20);
    card.set_margin_bottom(20);
    card.set_margin_start(20);
    card.set_margin_end(20);

    //
    // Título
    //

    let title = gtk::Label::new(Some("Sistema"));

    title.add_css_class("card-title");

    title.set_halign(gtk::Align::Start);

    card.append(&title);

    //
    // Información
    //

    card.append(&create_row("CPU", &system_info::get_cpu()));
    card.append(&create_row("RAM", &system_info::get_memory()));
    card.append(&create_row("Kernel", &system_info::get_kernel()));
    card.append(&create_row("SO", &system_info::get_os()));
    card.append(&create_row("Arquitectura", &system_info::get_architecture()));
    card.append(&create_row("Hostname", &system_info::get_hostname()));

    card
}

fn create_row(key: &str, value: &str) -> gtk::Box {
    let row = gtk::Box::new(gtk::Orientation::Horizontal, 10);

    row.add_css_class("system-row");

    let key_label = gtk::Label::new(Some(key));

    key_label.add_css_class("system-key");

    key_label.set_halign(gtk::Align::Start);

    key_label.set_hexpand(true);

    let value_label = gtk::Label::new(Some(value));

    value_label.add_css_class("system-value");

    value_label.set_halign(gtk::Align::End);

    value_label.set_wrap(true);

    row.append(&key_label);
    row.append(&value_label);

    row
}
