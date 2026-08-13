// ==========================================
// WallpaperService — estado del wallpaper (equivalente a services/wallpaper.py)
// ==========================================

use std::path::PathBuf;

use crate::services::settings;

pub struct WallpaperService;

impl WallpaperService {
    /// Ruta del wallpaper actual (settings.json wallpaper.path)
    pub fn current() -> String {
        settings::get_string("wallpaper.path", "")
    }

    pub fn user_dir() -> PathBuf {
        let home = std::env::var("HOME").unwrap_or_else(|_| "/root".to_string());
        PathBuf::from(home)
            .join(".local/share/churros/wallpapers")
    }

    /// Directorios donde se buscan wallpapers (orden de prioridad)
    pub fn wallpaper_dirs() -> Vec<PathBuf> {
        let home = std::env::var("HOME").unwrap_or_else(|_| "/root".to_string());
        vec![
            PathBuf::from("/usr/share/churros/wallpapers"),
            PathBuf::from("/usr/share/backgrounds"),
            Self::user_dir(),
            PathBuf::from(&home).join("Pictures/Wallpapers"),
            PathBuf::from(&home).join("Pictures"),
        ]
    }

    /// Escanea los directorios y devuelve wallpapers (ext: jpg jpeg png webp gif)
    pub fn list() -> Vec<PathBuf> {
        let mut found = Vec::new();
        for dir in Self::wallpaper_dirs() {
            if let Ok(entries) = std::fs::read_dir(&dir) {
                for entry in entries.flatten() {
                    let path = entry.path();
                    if path.is_file() {
                        if let Some(ext) = path.extension().and_then(|e| e.to_str()) {
                            let ext = ext.to_lowercase();
                            if matches!(ext.as_str(), "jpg" | "jpeg" | "png" | "webp" | "gif") {
                                found.push(path);
                            }
                        }
                    }
                }
            }
        }
        found.sort();
        found.dedup();
        found
    }
}
