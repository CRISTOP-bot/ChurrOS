// ==========================================
// ThemeService — dark/light + gtk settings + señales a waybar/foot
// (equivalente a services/theme.py)
// ==========================================

use std::fs;
use std::path::PathBuf;
use std::process::Command;

use serde_json::json;

use crate::services::settings;

fn cache_dir() -> PathBuf {
    let home = std::env::var("HOME").unwrap_or_else(|_| "/root".to_string());
    PathBuf::from(home).join(".cache").join("churros-theme")
}

fn dark_flag() -> PathBuf {
    cache_dir().join("dark-flag")
}

fn build_env() -> Vec<(String, String)> {
    let mut env: Vec<(String, String)> = std::env::vars().collect();
    if env.iter().all(|(k, _)| k != "WAYLAND_DISPLAY") {
        let uid = unsafe { libc_getuid() };
        let xrd = format!("/run/user/{uid}");
        if std::path::Path::new(&xrd).is_dir() {
            if let Ok(entries) = fs::read_dir(&xrd) {
                for entry in entries.flatten() {
                    let name = entry.file_name().to_string_lossy().to_string();
                    if name.starts_with("wayland-") {
                        env.push(("WAYLAND_DISPLAY".to_string(), name));
                        break;
                    }
                }
            }
        }
    }
    if env.iter().all(|(k, _)| k != "XDG_RUNTIME_DIR") {
        let uid = unsafe { libc_getuid() };
        env.push(("XDG_RUNTIME_DIR".to_string(), format!("/run/user/{uid}")));
    }
    env
}

// getuid sin dependencia libc: leer /proc/self/status o usar el uid del
// propietario del proceso via /proc/self (mejor: std no expone uid).
// Se usa el crate libc indirectamente a través de glib? No — lo resolvemos
// leyendo /proc/self/loginuid o simplemente el uid del archivo /proc/self.
fn libc_getuid() -> u32 {
    // Lectura de /proc/self/status línea Uid:
    if let Ok(content) = fs::read_to_string("/proc/self/status") {
        for line in content.lines() {
            if let Some(rest) = line.strip_prefix("Uid:") {
                if let Some(first) = rest.split_whitespace().next() {
                    if let Ok(uid) = first.parse::<u32>() {
                        return uid;
                    }
                }
            }
        }
    }
    1000
}

fn write_gtk_settings(dark: bool) {
    let home = std::env::var("HOME").unwrap_or_else(|_| "/root".to_string());
    let icon_theme = settings::get_string("icons.theme", if dark { "Papirus-Dark" } else { "Papirus" });

    let gtk_theme = if dark { "Adwaita-dark" } else { "Adwaita" };

    for dir in ["gtk-3.0", "gtk-4.0"] {
        let path = PathBuf::from(&home).join(".config").join(dir).join("settings.ini");
        if let Some(parent) = path.parent() {
            let _ = fs::create_dir_all(parent);
        }
        let content = format!(
            "[Settings]\ngtk-theme-name={}\ngtk-application-prefer-dark-theme={}\ngtk-icon-theme-name={}\n",
            gtk_theme,
            u8::from(dark),
            icon_theme
        );
        let _ = fs::write(path, content);
    }

    // Flag en caché para que is_dark() sea rápido sin leer settings.json
    if let Some(parent) = dark_flag().parent() {
        let _ = fs::create_dir_all(parent);
    }
    let _ = fs::write(dark_flag(), if dark { "1" } else { "0" });
}

pub struct ThemeService;

impl ThemeService {
    pub fn is_dark() -> bool {
        if let Ok(content) = fs::read_to_string(dark_flag()) {
            return content.trim() == "1";
        }
        if let Some(cached) = settings::get("theme.dark", json!(null)).as_bool() {
            return cached;
        }
        true
    }

    pub fn set(dark: bool) {
        settings::set("theme.dark", json!(dark));
        write_gtk_settings(dark);

        let env = build_env();

        // waybar: SIGUSR2 recarga; foot: SIGUSR1 dark, SIGUSR2 light
        let env_refs: Vec<(&str, &str)> = env
            .iter()
            .map(|(k, v)| (k.as_str(), v.as_str()))
            .collect();
        let _ = Command::new("pkill")
            .args(["-SIGUSR2", "waybar"])
            .envs(env_refs.iter().map(|(k, v)| (*k, *v)))
            .output();
        let _ = Command::new("pkill")
            .args([if dark { "-SIGUSR1" } else { "-SIGUSR2" }, "foot"])
            .envs(env_refs.iter().map(|(k, v)| (*k, *v)))
            .output();

        // TODO: pywal integration (services/pywal_service.py)
    }

    pub fn toggle() {
        Self::set(!Self::is_dark());
    }
}
