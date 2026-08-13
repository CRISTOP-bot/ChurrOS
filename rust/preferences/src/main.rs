// ==========================================
// churros-settings (preferences) — entry point
// (equivalente a main.py)
// ==========================================

mod assets;
mod pages;
mod services;
mod widgets;
mod window;

use gtk::prelude::*;
use gtk::gdk;

use services::accent::AccentService;
use window::PreferencesWindow;

const APP_ID: &str = "org.churros.preferences";

fn load_css() {
    let provider = gtk::CssProvider::new();

    // CSS compartido de ChurrOS
    let shared = "/usr/share/churros/styles/churros.css";
    if std::path::Path::new(shared).exists() {
        provider.load_from_path(shared);
    }

    // CSS local de preferences
    let local = assets::css_path();
    if local.exists() {
        provider.load_from_path(&local);
    }

    // accent.css del usuario (si existe)
    let accent = AccentService::accent_css_path();
    if accent.exists() {
        provider.load_from_path(&accent);
    }

    if let Some(display) = gdk::Display::default() {
        gtk::style_context_add_provider_for_display(
            &display,
            &provider,
            gtk::STYLE_PROVIDER_PRIORITY_APPLICATION,
        );
    }
}

fn activate(app: &gtk::Application) {
    // Regenerar accent.css si falta (como AccentService.ensure() en Python)
    AccentService::ensure();

    load_css();

    let win = PreferencesWindow::new(app);
    win.present();
}

fn main() -> glib::ExitCode {
    let app = gtk::Application::builder()
        .application_id(APP_ID)
        .build();

    app.connect_activate(activate);

    app.run()
}
