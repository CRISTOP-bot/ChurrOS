use gtk::prelude::*;

pub fn build() -> gtk::Label {
    let footer = gtk::Label::new(Some(&format!(
        "Linux • {} • ChurrOS {}",
        churros_services::version::desktop_name(),
        churros_services::version::distro()
    )));

    footer.add_css_class("footer");
    footer.set_halign(gtk::Align::Center);

    footer
}
