use std::path::PathBuf;

// En runtime (ISO): style.css en la raíz de /usr/share/churros/churros-settings/
// y logo.svg + icons/ dentro de assets/. En desarrollo se usan los assets
// locales del crate, que replican ese mismo layout.
const RUNTIME_ROOT: &str = "/usr/share/churros/churros-settings";
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
    resolve(
        &format!("{RUNTIME_ROOT}/style.css"),
        "style.css",
    )
}

pub fn logo_path() -> PathBuf {
    resolve(
        &format!("{RUNTIME_ROOT}/assets/logo.svg"),
        "logo.svg",
    )
}

pub fn icon_path(name: &str) -> PathBuf {
    resolve(
        &format!("{RUNTIME_ROOT}/assets/icons/{name}"),
        &format!("icons/{name}"),
    )
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