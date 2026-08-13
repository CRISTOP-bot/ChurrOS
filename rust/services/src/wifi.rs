// Servicio de wifi vía nmcli (equivalente a services/wifi.py)

use crate::{run, spawn};

fn unescape(s: &str) -> String {
    s.replace("\\:", ":")
}

#[derive(Debug, Clone, PartialEq)]
pub struct Network {
    pub ssid: String,
    pub signal: u8,
    pub security: String,
    pub connected: bool,
    pub saved: bool,
}

#[derive(Debug, Clone, Default, PartialEq)]
pub struct WifiInfo {
    pub available: bool,
    pub enabled: bool,
    pub connected: Option<String>,
    pub networks: Vec<Network>,
}

fn run_stdout(command: &[&str]) -> Option<(i32, String)> {
    let (code, out, _) = run(command, 5000)?;
    Some((code, out))
}

pub fn available() -> bool {
    let (code, out) = run_stdout(&["nmcli", "-t", "-f", "DEVICE,TYPE", "device"])
        .unwrap_or((1, String::new()));
    if code != 0 {
        return false;
    }
    out.lines().any(|line| {
        line.splitn(2, ':').nth(1) == Some("wifi")
    })
}

pub fn enabled() -> bool {
    let (code, out) = run_stdout(&["nmcli", "radio", "wifi"])
        .unwrap_or((1, String::new()));
    code == 0 && out.trim().to_lowercase() == "enabled"
}

pub fn scan() {
    spawn(&["nmcli", "device", "wifi", "rescan"]);
}

/// Parsea una línea de nmcli --escape yes -t: respeta los `\:` escapados.
fn parse_escaped(line: &str) -> Vec<String> {
    let mut fields = Vec::new();
    let mut current = String::new();
    let mut escape = false;

    for ch in line.chars() {
        if escape {
            current.push(ch);
            escape = false;
        } else if ch == '\\' {
            escape = true;
        } else if ch == ':' {
            fields.push(std::mem::take(&mut current));
        } else {
            current.push(ch);
        }
    }
    fields.push(current);

    fields
}

fn saved_networks() -> Vec<String> {
    let mut saved = Vec::new();
    let (code, out) = run_stdout(&["nmcli", "-t", "-f", "NAME,TYPE", "connection", "show"])
        .unwrap_or((1, String::new()));
    if code != 0 {
        return saved;
    }
    for line in out.lines() {
        if let Some((name, conn_type)) = line.split_once(':') {
            if conn_type == "802-11-wireless" {
                saved.push(name.to_string());
            }
        }
    }
    saved
}

pub fn get() -> WifiInfo {
    let mut data = WifiInfo {
        available: available(),
        enabled: enabled(),
        ..Default::default()
    };

    if !data.available || !data.enabled {
        return data;
    }

    let (code, out) = run_stdout(&[
        "nmcli",
        "--escape",
        "yes",
        "-t",
        "-f",
        "ACTIVE,SSID,SIGNAL,SECURITY",
        "device",
        "wifi",
        "list",
        "--rescan",
        "no",
    ])
    .unwrap_or((1, String::new()));

    if code != 0 {
        return data;
    }

    let saved = saved_networks();

    for line in out.lines() {
        if line.is_empty() {
            continue;
        }

        let fields = parse_escaped(line);
        let active = fields.first().map(|s| s.as_str()).unwrap_or("");
        let ssid = fields.get(1).map(|s| unescape(s)).unwrap_or_default();
        let signal = fields
            .get(2)
            .and_then(|s| s.trim_start_matches('-').parse::<u8>().ok())
            .unwrap_or(0);
        let security = unescape(fields.get(3).map(|s| s.as_str()).unwrap_or(""));

        let network = Network {
            ssid: if ssid.is_empty() {
                "Hidden Network".to_string()
            } else {
                ssid.clone()
            },
            signal,
            security,
            connected: active == "yes",
            saved: saved.contains(&ssid),
        };

        if network.connected {
            data.connected = Some(network.ssid.clone());
        }

        data.networks.push(network);
    }

    let mut seen = std::collections::HashSet::new();
    data.networks.retain(|n| seen.insert(n.ssid.clone()));

    data.networks.sort_by_key(|n| {
        (
            !n.connected,
            !n.saved,
            std::cmp::Reverse(n.signal),
        )
    });

    data
}

fn connect_error(code: i32, err: &str) -> (bool, String) {
    if code == 0 {
        return (true, String::new());
    }
    let err = err.to_lowercase();
    if err.contains("secrets were required") {
        (false, "Password required.".to_string())
    } else if err.contains("invalid") {
        (false, "Incorrect password.".to_string())
    } else if err.contains("activation") {
        (false, "Unable to connect.".to_string())
    } else {
        (false, "Unknown error.".to_string())
    }
}

pub fn connect(ssid: &str, password: Option<&str>) -> (bool, String) {
    let mut command = vec![
        "nmcli".to_string(),
        "device".to_string(),
        "wifi".to_string(),
        "connect".to_string(),
        ssid.to_string(),
    ];
    if let Some(pw) = password {
        command.extend(["password".to_string(), pw.to_string()]);
    }
    let args: Vec<&str> = command.iter().map(|s| s.as_str()).collect();
    let (code, _, err) = run(&args, 5000).unwrap_or((1, String::new(), "execution error".to_string()));
    connect_error(code, &err)
}

pub fn connect_hidden(ssid: &str, password: Option<&str>) -> (bool, String) {
    let (code, _, _err) = run(
        &[
            "nmcli",
            "connection",
            "add",
            "type",
            "wifi",
            "ifname",
            "wlan0",
            "con-name",
            ssid,
            "ssid",
            ssid,
            "hidden",
            "yes",
        ],
        5000,
    )
    .unwrap_or((1, String::new(), "execution error".to_string()));

    if code != 0 {
        return (false, "Failed to create hidden profile.".to_string());
    }

    let mut command = vec![
        "nmcli".to_string(),
        "connection".to_string(),
        "up".to_string(),
        ssid.to_string(),
    ];
    if let Some(pw) = password {
        command.extend(["password".to_string(), pw.to_string()]);
    }
    let args: Vec<&str> = command.iter().map(|s| s.as_str()).collect();
    let (code, _, err) = run(&args, 5000).unwrap_or((1, String::new(), "execution error".to_string()));
    connect_error(code, &err)
}

pub fn disconnect() {
    let (code, out) = run_stdout(&["nmcli", "-t", "-f", "DEVICE,TYPE", "device"])
        .unwrap_or((1, String::new()));
    if code != 0 {
        return;
    }
    for line in out.lines() {
        if let Some((device, dev_type)) = line.split_once(':') {
            if dev_type == "wifi" {
                let _ = run(&["nmcli", "device", "disconnect", device], 5000);
                break;
            }
        }
    }
}

pub fn forget(ssid: &str) {
    let _ = run(&["nmcli", "connection", "delete", ssid], 5000);
}

pub fn enable() {
    let _ = run(&["nmcli", "radio", "wifi", "on"], 5000);
}

pub fn disable() {
    let _ = run(&["nmcli", "radio", "wifi", "off"], 5000);
}

pub fn toggle() {
    if enabled() {
        disable();
    } else {
        enable();
    }
}
