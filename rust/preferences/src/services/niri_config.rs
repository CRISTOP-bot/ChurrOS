// ==========================================
// NiriConfig — lee/edita ~/.config/niri/config.kdl
// (equivalente a services/dotfiles/niri_config.py, subset: animations + csd)
// ==========================================

use std::fs;
use std::path::PathBuf;
use std::process::Command;

pub struct NiriConfig;

fn config_path() -> PathBuf {
    let home = std::env::var("HOME").unwrap_or_else(|_| "/root".to_string());
    PathBuf::from(home).join(".config").join("niri").join("config.kdl")
}

fn read() -> String {
    fs::read_to_string(config_path()).unwrap_or_default()
}

fn write_atomic(content: &str) {
    let path = config_path();
    if let Some(parent) = path.parent() {
        let _ = fs::create_dir_all(parent);
    }
    // Escritura atómica: tmp + rename
    let tmp = path.with_extension("kdl.tmp");
    if fs::write(&tmp, content).is_ok() {
        let _ = fs::rename(&tmp, &path);
    }
}

/// Encuentra [start, end) de un bloque `name { ... }` (líneas, 0-indexado)
fn find_block(content: &str, names: &[&str]) -> Option<(usize, usize)> {
    let lines: Vec<&str> = content.lines().collect();
    let mut depth = 0i32;
    let mut start = None;

    for (i, raw) in lines.iter().enumerate() {
        let stripped = raw.trim();

        if let Some(s) = start {
            depth += stripped.matches('{').count() as i32;
            depth -= stripped.matches('}').count() as i32;
            if depth <= 0 {
                return Some((s, i + 1));
            }
            continue;
        }

        // Buscar "name {" al inicio de la línea
        for name in names {
            if stripped == format!("{name} {{") || stripped.starts_with(&format!("{name} {{")) {
                start = Some(i);
                depth = 1;
                // Si el bloque abre y cierra en la misma línea
                if stripped.matches('{').count() > stripped.matches('}').count() {
                    // sigue en la misma línea; se procesa en la siguiente iteración
                } else {
                    return Some((i, i + 1));
                }
                break;
            }
        }
    }
    None
}

impl NiriConfig {
    /// pkill -HUP niri (recarga la config en vivo)
    pub fn reload() {
        let _ = Command::new("pkill")
            .args(["-HUP", "niri"])
            .stdout(std::process::Stdio::null())
            .stderr(std::process::Stdio::null())
            .spawn();
    }

    // -------------------------------------------------------- Animations

    pub fn get_animations() -> bool {
        let content = read();
        let Some((start, end)) = find_block(&content, &["animations"]) else {
            return true;
        };

        let lines: Vec<&str> = content.lines().collect();
        for j in start + 1..end {
            let stripped = lines[j].trim();
            if stripped == "off" {
                return false;
            }
            if stripped == "on" {
                return true;
            }
        }
        true
    }

    pub fn set_animations(on: bool) {
        let content = read();
        let block = find_block(&content, &["animations"]);
        let (start, end) = match block {
            Some(b) => b,
            None => {
                if !on {
                    let mut content = content;
                    if !content.ends_with('\n') {
                        content.push('\n');
                    }
                    content.push_str("animations {\n    off\n}\n");
                    write_atomic(&content);
                }
                return;
            }
        };

        let mut lines: Vec<String> = content.lines().map(|s| s.to_string()).collect();

        if !on {
            // Asegurar que hay una línea "off" dentro del bloque
            let has_off = (start + 1..end).any(|j| lines[j].trim() == "off");
            if !has_off {
                let mut insert_idx = end;
                for j in start + 1..end {
                    if !lines[j].trim().is_empty() {
                        insert_idx = j;
                        break;
                    }
                }
                lines.insert(insert_idx, "    off".to_string());
                write_atomic(&lines.join("\n"));
            }
        } else {
            // Quitar "off" (y líneas vacías) del bloque
            let new_inner: Vec<String> = lines[start + 1..end]
                .iter()
                .filter(|l| !l.trim().is_empty() && l.trim() != "off")
                .cloned()
                .collect();

            if new_inner.is_empty() {
                // Bloque vacío -> eliminar el bloque entero
                lines.drain(start..=end);
                write_atomic(&lines.join("\n"));
            } else {
                lines.drain(start + 1..end);
                for (k, l) in new_inner.iter().enumerate() {
                    lines.insert(start + 1 + k, l.clone());
                }
                write_atomic(&lines.join("\n"));
            }
        }
    }

    // ------------------------------------------------------- prefer-no-csd

    pub fn get_prefer_no_csd() -> bool {
        let content = read();
        content
            .lines()
            .any(|l| l.trim() == "prefer-no-csd")
    }

    pub fn set_prefer_no_csd(on: bool) {
        let content = read();
        let mut lines: Vec<String> = content.lines().map(|s| s.to_string()).collect();

        for i in 0..lines.len() {
            if lines[i].trim() == "prefer-no-csd" {
                if !on {
                    lines.remove(i);
                    write_atomic(&lines.join("\n"));
                }
                return;
            }
        }

        // No existe
        if on {
            if !content.ends_with('\n') {
                if let Some(last) = lines.last_mut() {
                    last.push('\n');
                }
            }
            lines.push("prefer-no-csd".to_string());
            write_atomic(&lines.join("\n"));
        }
    }
}
