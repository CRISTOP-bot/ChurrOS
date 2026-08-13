use gtk::prelude::*;

pub fn build() -> gtk::Box {
    let container = gtk::Box::new(gtk::Orientation::Vertical, 18);
    container.set_halign(gtk::Align::Center);

    // =====================================
    // Logo
    // =====================================

    let logo = gtk::Picture::for_filename(crate::assets::icons_path("logo.svg"));
    logo.set_size_request(140, 140);
    logo.set_halign(gtk::Align::Center);
    logo.add_css_class("logo");

    // =====================================
    // Título
    // =====================================

    let title = gtk::Label::new(None);
    title.set_markup(
        "<span foreground='white'>Churr</span><span foreground='#ff8c00'>OS</span>",
    );
    title.add_css_class("title");
    title.set_halign(gtk::Align::Center);

    // =====================================
    // Subtítulo
    // =====================================

    let subtitle = gtk::Label::new(Some(
        "Bienvenido a ChurrOS\nUna distribución Linux moderna basada en Arch Linux.",
    ));
    subtitle.set_halign(gtk::Align::Center);
    subtitle.set_justify(gtk::Justification::Center);
    subtitle.set_wrap(true); // wrap en pantallas pequeñas
    subtitle.add_css_class("subtitle");

    // =====================================
    // Separador
    // =====================================

    let separator = gtk::Separator::new(gtk::Orientation::Horizontal);
    separator.set_margin_top(15);
    separator.set_margin_bottom(15);

    // =====================================
    // Construcción
    // =====================================

    container.append(&logo);
    container.append(&title);
    container.append(&subtitle);
    container.append(&separator);

    container
}
