mod action_card;
mod actions;
mod assets;
mod cards;
mod footer;
mod header;
mod system_card;
mod system_info;

use gtk::prelude::*;
use adw::prelude::*;

const APP_ID: &str = "org.churros.Welcome";

fn load_css() {
    // Cada archivo en su propio provider: load_from_path REEMPLAZA el
    // contenido previo del provider, así que compartir provider perdería
    // el churros.css (el style.css de welcome es autocontenido, pero el
    // CSS compartido aporta tokens/paleta a la ISO).
    let shared = "/usr/share/churros/styles/churros.css";
    if std::path::Path::new(shared).exists() {
        let provider = gtk::CssProvider::new();
        provider.load_from_path(shared);
        if let Some(display) = gtk::gdk::Display::default() {
            gtk::style_context_add_provider_for_display(
                &display,
                &provider,
                gtk::STYLE_PROVIDER_PRIORITY_APPLICATION,
            );
        }
    }

    // CSS local de la app (pisa al compartido)
    let local = assets::css_path();
    if local.exists() {
        let provider = gtk::CssProvider::new();
        provider.load_from_path(&local);
        if let Some(display) = gtk::gdk::Display::default() {
            gtk::style_context_add_provider_for_display(
                &display,
                &provider,
                gtk::STYLE_PROVIDER_PRIORITY_APPLICATION + 1,
            );
        }
    }
}

fn activate(app: &adw::Application) {
    load_css();

    let window = adw::ApplicationWindow::builder()
        .application(app)
        .title("Welcome — ChurrOS")
        .build();

    window.set_default_size(700, 520);
    window.set_size_request(640, 480);
    window.set_decorated(false);

    let desktop = churros_services::version::edition();
    if desktop.contains("niri") {
        window.maximize();
    }

    let content = gtk::Box::new(gtk::Orientation::Vertical, 30);
    content.set_margin_top(40);
    content.set_margin_bottom(40);
    content.set_margin_start(40);
    content.set_margin_end(40);

    content.set_halign(gtk::Align::Center);
    content.set_valign(gtk::Align::Start);

    content.append(&header::build());
    content.append(&cards::build());
    content.append(&footer::build());

    let scroller = gtk::ScrolledWindow::new();
    scroller.set_policy(gtk::PolicyType::Automatic, gtk::PolicyType::Automatic);
    scroller.set_child(Some(&content));
    scroller.add_css_class("content-scroller");

    window.set_content(Some(&scroller));

    window.present();
}

fn main() -> glib::ExitCode {
    let app = adw::Application::builder()
        .application_id(APP_ID)
        .build();

    app.connect_activate(activate);

    app.run()
}
