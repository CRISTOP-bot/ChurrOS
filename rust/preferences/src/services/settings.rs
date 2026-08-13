// ==========================================
// SettingsService — ~/.config/churros/settings.json
// (equivalente a services/settings.py)
// ==========================================

use std::fs;
use std::path::PathBuf;

use serde_json::{Map, Value};

pub struct SettingsService;

fn config_dir() -> PathBuf {
    let home = std::env::var("HOME").unwrap_or_else(|_| "/root".to_string());
    PathBuf::from(home).join(".config").join("churros")
}

fn config_file() -> PathBuf {
    config_dir().join("settings.json")
}

fn defaults() -> Value {
    serde_json::json!({
        "theme": { "dark": false, "dynamic_colors": true },
        "accent": { "color": "Orange" },
        "wallpaper": { "path": "" },
        "icons": { "theme": "Papirus" },
        "cursor": { "theme": "Bibata" },
        "fonts": { "family": "Inter", "scale": 1.0 }
    })
}

fn ensure() {
    let dir = config_dir();
    let file = config_file();
    if !dir.exists() {
        let _ = fs::create_dir_all(&dir);
    }
    if !file.exists() {
        let _ = fs::write(&file, serde_json::to_string_pretty(&defaults()).unwrap());
    }
}

pub fn load() -> Value {
    ensure();
    match fs::read_to_string(config_file()) {
        Ok(content) => serde_json::from_str(&content).unwrap_or_else(|_| defaults()),
        Err(_) => defaults(),
    }
}

pub fn save(data: &Value) {
    ensure();
    let _ = fs::write(config_file(), serde_json::to_string_pretty(data).unwrap());
}

/// get("theme.dark") — navega por claves separadas por puntos
pub fn get(key: &str, default: Value) -> Value {
    let data = load();
    let mut current = &data;
    for part in key.split('.') {
        match current {
            Value::Object(map) => match map.get(part) {
                Some(v) => current = v,
                None => return default,
            },
            _ => return default,
        }
    }
    current.clone()
}

/// get_string("accent.color", "Orange")
pub fn get_string(key: &str, default: &str) -> String {
    match get(key, Value::String(default.to_string())) {
        Value::String(s) => s,
        Value::Bool(b) => b.to_string(),
        Value::Number(n) => n.to_string(),
        _ => default.to_string(),
    }
}

pub fn get_bool(key: &str, default: bool) -> bool {
    match get(key, Value::Bool(default)) {
        Value::Bool(b) => b,
        Value::String(s) => s == "1" || s.eq_ignore_ascii_case("true"),
        _ => default,
    }
}

pub fn set(key: &str, value: Value) {
    let mut data = load();
    let mut current = data.as_object_mut().expect("settings.json raíz debe ser objeto");

    let mut parts: Vec<&str> = key.split('.').collect();
    let last = parts.pop().unwrap();

    for part in &parts {
        let entry = current
            .entry(part.to_string())
            .or_insert_with(|| Value::Object(Map::new()));
        match entry {
            Value::Object(map) => current = map,
            _ => {
                *entry = Value::Object(Map::new());
                current = entry.as_object_mut().unwrap();
            }
        }
    }

    current.insert(last.to_string(), value);
    save(&data);
}
