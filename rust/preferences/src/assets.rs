use std::path::PathBuf;

// En runtime (ISO) los assets viven en /usr/share/churros/preferences/.
// En desarrollo se usan los assets locales del crate.
const RUNTIME_ROOT: &str = "/usr/share/churros/preferences";
const DEV_ROOT: &str = concat!(env!("CARGO_MANIFEST_DIR"), "/assets");

fn assets_root() -> PathBuf {
    let runtime = PathBuf::from(RUNTIME_ROOT);
    if runtime.is_dir() {
        runtime
    } else {
        PathBuf::from(DEV_ROOT)
    }
}

pub fn css_path() -> PathBuf {
    assets_root().join("style.css")
}

pub fn logo_path() -> PathBuf {
    assets_root().join("logo.svg")
}

pub fn icon_path(name: &str) -> PathBuf {
    assets_root().join("icons").join(name)
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
