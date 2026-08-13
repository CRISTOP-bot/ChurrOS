use gtk::prelude::*;

const VERSION: &str = "0.2.0";

pub fn build() -> gtk::Label {
    let footer = gtk::Label::new(Some(&format!("Linux • Niri • ChurrOS {VERSION}")));

    footer.add_css_class("footer");
    footer.set_halign(gtk::Align::Center);

    footer
}
