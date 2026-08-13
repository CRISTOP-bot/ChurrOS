use gtk::prelude::*;

pub fn new(
    icon_name: &str,
    title: &str,
    description: &str,
    callback: fn(&gtk::Button),
) -> gtk::Button {
    let button = gtk::Button::new();
    button.set_size_request(280, 340); // iguales para todas las cards
    button.add_css_class("action-card");

    button.connect_clicked(callback);

    // =====================================
    // Contenedor principal
    // =====================================

    let content = gtk::Box::new(gtk::Orientation::Vertical, 12);

    content.set_halign(gtk::Align::Center);
    content.set_valign(gtk::Align::Center);

    content.set_margin_top(20);
    content.set_margin_bottom(20);
    content.set_margin_start(20);
    content.set_margin_end(20);

    // =====================================
    // Icono
    // =====================================

    let icon = gtk::Picture::for_filename(crate::assets::icons_path(icon_name));

    icon.set_size_request(64, 64);

    icon.set_halign(gtk::Align::Center);

    icon.add_css_class("card-icon");

    // =====================================
    // Título
    // =====================================

    let title_label = gtk::Label::new(Some(title));

    title_label.add_css_class("card-title");

    title_label.set_halign(gtk::Align::Center);

    // =====================================
    // Descripción
    // =====================================

    let description_label = gtk::Label::new(Some(description));

    description_label.set_wrap(true);

    description_label.set_max_width_chars(24);

    description_label.set_justify(gtk::Justification::Center);

    description_label.set_halign(gtk::Align::Center);

    description_label.add_css_class("card-description");

    // =====================================
    // Construcción
    // =====================================

    content.append(&icon);
    content.append(&title_label);
    content.append(&description_label);

    button.set_child(Some(&content));

    button
}
