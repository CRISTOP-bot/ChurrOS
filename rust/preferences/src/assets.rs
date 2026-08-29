use std::path::PathBuf;

const RUNTIME_ROOTS: &[&str] = &[
    "/usr/share/churros/churros-settings/assets",
    "/usr/share/churros/churros-settings",
    "/usr/share/churros/preferences/assets",
    "/usr/share/churros/preferences",
];
const DEV_ROOT: &str = concat!(env!("CARGO_MANIFEST_DIR"), "/assets");

pub fn css_path() -> PathBuf {
    for root in RUNTIME_ROOTS {
        for name in ["style.css", "assets/style.css"] {
            let p = PathBuf::from(root).join(name);
            if p.is_file() {
                return p;
            }
        }
    }
    PathBuf::from(DEV_ROOT).join("style.css")
}

pub fn logo_path() -> PathBuf {
    for root in RUNTIME_ROOTS {
        for name in ["logo.svg", "assets/logo.svg"] {
            let p = PathBuf::from(root).join(name);
            if p.is_file() {
                return p;
            }
        }
    }
    PathBuf::from(DEV_ROOT).join("logo.svg")
}

pub fn icon_path(name: &str) -> PathBuf {
    for root in RUNTIME_ROOTS {
        for sub in [format!("icons/{name}"), format!("assets/icons/{name}")] {
            let p = PathBuf::from(root).join(&sub);
            if p.is_file() {
                return p;
            }
        }
    }
    PathBuf::from(DEV_ROOT).join(format!("icons/{name}"))
}

/// Carga un icono SVG de los assets como GtkImage (si existe)
pub fn icon_image(name: &str, pixel_size: i32) -> Option<gtk::Image> {
    let path = icon_path(name);
    if !path.is_file() {
        return None;
    }
    let image = gtk::Image::from_file(&path);
    image.set_pixel_size(pixel_size);
    Some(image)
}