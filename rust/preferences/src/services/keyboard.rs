// ==========================================
// KeyboardService (equivalente a services/keyboard.py)
// Porta el parseo de config.kdl SIN regex (el workspace no tiene crate regex).
// ==========================================

use std::fs;
use std::path::PathBuf;

fn config_path() -> PathBuf {
    let home = std::env::var("HOME").unwrap_or_else(|_| "/root".to_string());
    PathBuf::from(home).join(".config").join("niri").join("config.kdl")
}

fn backup_path() -> PathBuf {
    let home = std::env::var("HOME").unwrap_or_else(|_| "/root".to_string());
    PathBuf::from(home)
        .join(".config")
        .join("niri")
        .join("config.kdl.bak")
}

/// Un atajo de teclado parseado de config.kdl
#[derive(Clone)]
pub struct Bind {
    pub key: String,
    pub allow_when_locked: bool,
    /// "spawn" | "spawn-sh" | "builtin"
    pub kind: String,
    pub command: String,
    pub args: String,
}

/// ¿La clave coincide con el patrón del regex Python
/// `(Mod\S*|Print|Ctrl\+Print|Alt\+Print|XF86\S*)`?
fn key_is_recognized(key: &str) -> bool {
    key.starts_with("Mod") || key == "Print" || key == "Ctrl+Print" || key == "Alt+Print" || key.starts_with("XF86")
}

/// Extrae el contenido entre el primer '"' y el siguiente '"' de `s` (s empieza con '"').
fn split_quote(s: &str) -> (String, String) {
    let bytes = s.as_bytes();
    let mut end = 0usize;
    let mut escaped = false;
    for (i, &b) in bytes.iter().enumerate() {
        if i == 0 {
            continue;
        }
        if escaped {
            escaped = false;
            continue;
        }
        if b == b'\\' {
            escaped = true;
            continue;
        }
        if b == b'"' {
            end = i;
            break;
        }
    }
    if end == 0 {
        return (String::new(), String::new());
    }
    (s[1..end].to_string(), s[end + 1..].to_string())
}

/// Equivalente a _parse_action: "spawn \"cmd\" \"args\"" | "spawn-sh \"cmd\"" | builtin.
fn parse_action(raw: &str) -> (String, String, String) {
    let action = raw.trim().trim_end_matches(';');

    // spawn-sh "cmd"
    if let Some(rest) = action.strip_prefix("spawn-sh") {
        if let Some(q) = rest.trim_start().strip_prefix('"') {
            let (cmd, _) = split_quote(q);
            return ("spawn-sh".to_string(), cmd, String::new());
        }
    }

    // spawn "cmd" ["args"]
    if let Some(rest) = action.strip_prefix("spawn") {
        if rest.starts_with(|c: char| c.is_whitespace()) {
            if let Some(q) = rest.trim_start().strip_prefix('"') {
                let (cmd, tail) = split_quote(q);
                if !cmd.is_empty() {
                    if let Some(q2) = tail.trim_start().strip_prefix('"') {
                        let (args, _) = split_quote(q2);
                        return ("spawn".to_string(), cmd, args);
                    }
                    return ("spawn".to_string(), cmd, String::new());
                }
            }
        }
    }

    // builtin: primer token + resto
    let mut parts = action.split_whitespace();
    let func = parts.next().unwrap_or("").to_string();
    let args = parts.collect::<Vec<_>>().join(" ");
    ("builtin".to_string(), func, args)
}

/// Equivalente a _make_action_line.
fn make_action_line(bind_type: &str, command: &str, args: &str) -> String {
    match bind_type {
        "spawn" => {
            if !args.is_empty() {
                format!("spawn \"{command}\" \"{args}\"")
            } else {
                format!("spawn \"{command}\"")
            }
        }
        "spawn-sh" => format!("spawn-sh \"{command}\""),
        _ => {
            if !args.is_empty() {
                format!("{command} {args}")
            } else {
                command.to_string()
            }
        }
    }
}

/// ¿La línea (ya trimmeada) empieza por `key` seguido de espacio/fin/{/(?
/// (equivalente al regex de set_keybind: ^\s*KEY(\s|$|\s*{|\s*\()
fn line_matches_key(stripped: &str, key: &str) -> bool {
    if let Some(rest) = stripped.strip_prefix(key) {
        rest.is_empty()
            || rest.starts_with(|c: char| c.is_whitespace())
            || rest.starts_with('{')
            || rest.starts_with('(')
    } else {
        false
    }
}

/// Parsea una línea de bind "    Mod+X { spawn \"foot\"; }".
fn parse_bind_line(line: &str) -> Option<Bind> {
    let stripped = line.trim();
    let open = stripped.find('{')?;
    let close = stripped.rfind('}')?;
    if close < open {
        return None;
    }

    let head = stripped[..open].trim();
    let action = stripped[open + 1..close].trim();

    let mut tokens = head.split_whitespace();
    let key = tokens.next()?;
    if !key_is_recognized(key) {
        return None;
    }
    let allow_when_locked = tokens.any(|t| t.starts_with("allow-when-locked"));

    let (kind, command, args) = parse_action(action);
    Some(Bind {
        key: key.to_string(),
        allow_when_locked,
        kind,
        command,
        args,
    })
}

pub struct KeyboardService;

impl KeyboardService {
    /// Lee todos los atajos del bloque `binds` de config.kdl.
    pub fn get_keybinds() -> Vec<Bind> {
        let path = config_path();
        if !path.exists() {
            return Vec::new();
        }
        let content = match fs::read_to_string(&path) {
            Ok(c) => c,
            Err(_) => return Vec::new(),
        };

        let mut binds = Vec::new();
        let mut in_binds = false;
        for line in content.lines() {
            let stripped = line.trim();
            if stripped.starts_with("binds") {
                in_binds = true;
                continue;
            }
            if in_binds && stripped == "}" {
                break;
            }
            if !in_binds {
                continue;
            }
            if let Some(bind) = parse_bind_line(stripped) {
                binds.push(bind);
            }
        }
        binds
    }

    /// Sustituye la acción del atajo `key` (la tecla no cambia).
    /// FIX vs Python: el Python escribía "indent + new_action" perdiendo la tecla
    /// (config.kdl inválido); aquí se escribe la línea completa "key { action; }",
    /// que es lo que el propio Python construye en `new_line` (y usa add_keybind).
    pub fn set_keybind(key: &str, action_type: &str, command: &str, args: &str) -> bool {
        let path = config_path();
        if !path.exists() {
            return false;
        }
        // copia de seguridad previa (shutil.copyfile)
        let _ = fs::copy(&path, backup_path());

        let content = match fs::read_to_string(&path) {
            Ok(c) => c,
            Err(_) => return false,
        };

        let new_action = make_action_line(action_type, command, args);
        let new_line = format!("    {key} {{ {new_action}; }}");

        let mut out = String::new();
        let mut in_binds = false;
        let mut replaced = false;

        for line in content.lines() {
            let stripped = line.trim();
            if stripped.starts_with("binds") {
                in_binds = true;
                out.push_str(line);
                out.push('\n');
                continue;
            }
            if in_binds && stripped == "}" {
                out.push_str(line);
                out.push('\n');
                in_binds = false;
                continue;
            }
            if in_binds && !replaced && line_matches_key(stripped, key) {
                let indent: String = line.chars().take_while(|c| c.is_whitespace()).collect();
                out.push_str(&indent);
                out.push_str(&new_line);
                out.push('\n');
                replaced = true;
                continue;
            }
            out.push_str(line);
            out.push('\n');
        }

        if !replaced {
            return false;
        }
        fs::write(&path, out).is_ok()
    }

    /// Inserta un atajo nuevo justo antes del cierre del bloque `binds`.
    pub fn add_keybind(key: &str, action_type: &str, command: &str, args: &str) -> bool {
        let path = config_path();
        if !path.exists() {
            return false;
        }
        let _ = fs::copy(&path, backup_path());

        let content = match fs::read_to_string(&path) {
            Ok(c) => c,
            Err(_) => return false,
        };

        let new_line = format!(
            "    {key} {{ {}; }}",
            make_action_line(action_type, command, args)
        );

        let mut out_lines: Vec<String> = Vec::new();
        let mut in_binds = false;
        let mut insert_pos: Option<usize> = None;

        for line in content.lines() {
            out_lines.push(line.to_string());
            let stripped = line.trim();
            if stripped.starts_with("binds") {
                in_binds = true;
                continue;
            }
            if in_binds && stripped == "}" {
                insert_pos = Some(out_lines.len() - 1);
                in_binds = false;
                break;
            }
        }

        // Paridad con Python (insert(-1, ...)): sin bloque binds, inserta antes de la última línea
        let pos = insert_pos.unwrap_or_else(|| out_lines.len().saturating_sub(1));
        out_lines.insert(pos, new_line);

        let mut result = out_lines.join("\n");
        result.push('\n');
        fs::write(&path, result).is_ok()
    }

    /// Restaura config.kdl desde la copia de seguridad (config.kdl.bak).
    #[allow(dead_code)] // presente por paridad con services/keyboard.py (restore_backup)
    pub fn restore_backup() -> bool {
        let bak = backup_path();
        if bak.exists() {
            fs::copy(&bak, config_path()).is_ok()
        } else {
            false
        }
    }
}
