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
    // IMPORTANTE: cada archivo necesita su PROPIO CssProvider —
    // gtk_css_provider_load_from_path REEMPLAZA el contenido previo
    // del provider (cargar 3 CSS en 1 provider deja solo el último).
    // Prioridades idénticas a main.py:
    //   churros.css -> APPLICATION, style.css -> APPLICATION+1,
    //   accent.css  -> USER (la más alta, pisa a las demás).

    // CSS compartido de ChurrOS
    let shared = "/usr/share/churros/styles/churros.css";
    if std::path::Path::new(shared).exists() {
        let provider = gtk::CssProvider::new();
        provider.load_from_path(shared);
        if let Some(display) = gdk::Display::default() {
            gtk::style_context_add_provider_for_display(
                &display,
                &provider,
                gtk::STYLE_PROVIDER_PRIORITY_APPLICATION,
            );
        }
    }

    // CSS local de preferences (pisa a churros.css)
    let local = assets::css_path();
    if local.exists() {
        let provider = gtk::CssProvider::new();
        provider.load_from_path(&local);
        if let Some(display) = gdk::Display::default() {
            gtk::style_context_add_provider_for_display(
                &display,
                &provider,
                gtk::STYLE_PROVIDER_PRIORITY_APPLICATION + 1,
            );
        }
    }

    // accent.css del usuario (si existe) — prioridad USER como en el Python
    let accent = AccentService::accent_css_path();
    if accent.exists() {
        let provider = gtk::CssProvider::new();
        provider.load_from_path(&accent);
        if let Some(display) = gdk::Display::default() {
            gtk::style_context_add_provider_for_display(
                &display,
                &provider,
                gtk::STYLE_PROVIDER_PRIORITY_USER,
            );
        }
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
