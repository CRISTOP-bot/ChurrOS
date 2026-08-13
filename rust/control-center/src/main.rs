mod logging;
mod widgets;

use gtk::prelude::*;

const APP_ID: &str = "org.churros.controlcenter";

fn main() -> glib::ExitCode {
    logging::init("control-center");

    let app = gtk::Application::builder()
        .application_id(APP_ID)
        .build();
    logging::log("gtk app creada");

    app.connect_activate(|app| {
        logging::log("activate");
        load_css();
        logging::log("css cargado");
        let window = widgets::ControlCenterWindow::new(app);
        window.window().present();
        logging::log("ventana presentada");
    });

    // run() pasaría std::env::args() a GApplication (el nombre del popup
    // se interpretaría como fichero a abrir). Sin argumentos extra.
    let code = app.run_with_args(&[] as &[&str]);
    logging::log(&format!("salida code={code:?}"));
    code
}

fn load_css() {
    logging::log("cargando css");
    let display = gtk::gdk::Display::default().unwrap();
    logging::log("display ok");
    let shared = "/usr/share/churros/styles/churros.css";
    if std::path::Path::new(shared).is_file() {
        let provider = gtk::CssProvider::new();
        provider.load_from_path(shared);
        gtk::style_context_add_provider_for_display(
            &display,
            &provider,
            gtk::STYLE_PROVIDER_PRIORITY_APPLICATION,
        );
    }
    let css = assets::css_path();
    logging::log(&format!("css local: {} existe={}", css.display(), css.is_file()));
    let provider = gtk::CssProvider::new();
    provider.load_from_path(css);
    gtk::style_context_add_provider_for_display(
        &display,
        &provider,
        gtk::STYLE_PROVIDER_PRIORITY_APPLICATION + 1,
    );
}

mod assets {
    use std::path::PathBuf;

    // En runtime (ISO): /usr/share/churros/control-center/ con style.css,
    // logo.svg e icons/ dentro de assets/. En desarrollo, assets locales.
    const RUNTIME_ROOT: &str = "/usr/share/churros/control-center";
    const DEV_ROOT: &str = concat!(env!("CARGO_MANIFEST_DIR"), "/assets");

    fn resolve(runtime: &str, dev: &str) -> PathBuf {
        let path = PathBuf::from(runtime);
        if path.is_file() {
            path
        } else {
            PathBuf::from(DEV_ROOT).join(dev)
        }
    }

    pub fn css_path() -> PathBuf {
        resolve(&format!("{RUNTIME_ROOT}/style.css"), "style.css")
    }

    pub fn icon_path(name: &str) -> PathBuf {
        resolve(
            &format!("{RUNTIME_ROOT}/assets/icons/{name}"),
            &format!("icons/{name}"),
        )
    }

    pub fn logo_path() -> PathBuf {
        resolve(&format!("{RUNTIME_ROOT}/assets/logo.svg"), "logo.svg")
    }
}