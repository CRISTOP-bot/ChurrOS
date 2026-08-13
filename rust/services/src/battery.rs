// Servicio de batería vía upower (equivalente a services/battery.py)

use crate::run;

fn find_battery() -> Option<String> {
    let out = run(&["upower", "-e"], 3000)?;
    out.1
        .lines()
        .find(|l| l.to_lowercase().contains("battery"))
        .map(|l| l.to_string())
}

fn battery_icon(percentage: u8, charging: bool) -> &'static str {
    if charging {
        if percentage < 10 {
            "󰢜"
        } else if percentage < 30 {
            "󰂆"
        } else if percentage < 50 {
            "󰂇"
        } else if percentage < 70 {
            "󰂈"
        } else if percentage < 85 {
            "󰢝"
        } else if percentage < 95 {
            "󰂉"
        } else {
            "󰂊"
        }
    } else if percentage >= 95 {
        "󰁹"
    } else if percentage >= 80 {
        "󰂂"
    } else if percentage >= 60 {
        "󰂀"
    } else if percentage >= 40 {
        "󰁾"
    } else if percentage >= 20 {
        "󰁼"
    } else {
        "󰂎"
    }
}

#[derive(Debug, Clone)]
pub struct BatteryInfo {
    pub available: bool,
    pub percentage: u8,
    pub state: String,
    pub time_to_full: String,
    pub time_to_empty: String,
    pub icon: String,
}

pub fn available() -> bool {
    find_battery().is_some()
}

pub fn get() -> BatteryInfo {
    let mut info = BatteryInfo {
        available: false,
        percentage: 0,
        state: "unknown".to_string(),
        time_to_full: String::new(),
        time_to_empty: String::new(),
        icon: "󰂎".to_string(),
    };

    let Some(battery) = find_battery() else {
        return info;
    };
    let Some((_, out, _)) = run(&["upower", "-i", &battery], 3000) else {
        return info;
    };

    info.available = true;

    for line in out.lines() {
        let line = line.trim();
        if let Some(v) = line.strip_prefix("state:") {
            info.state = v.trim().to_string();
        } else if let Some(v) = line.strip_prefix("percentage:") {
            info.percentage = v
                .replace('%', "")
                .trim()
                .parse()
                .unwrap_or(info.percentage);
        } else if let Some(v) = line.strip_prefix("time to full:") {
            info.time_to_full = v.trim().to_string();
        } else if let Some(v) = line.strip_prefix("time to empty:") {
            info.time_to_empty = v.trim().to_string();
        }
    }

    let charging = matches!(
        info.state.as_str(),
        "charging" | "fully-charged" | "pending-charge"
    );
    info.icon = battery_icon(info.percentage, charging).to_string();

    info
}
