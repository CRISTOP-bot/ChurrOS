// Servicio de brillo vía brightnessctl (equivalente a services/brightness.py)

use std::path::Path;

use crate::run;

fn backlight_devices_exist() -> bool {
    Path::new("/sys/class/backlight")
        .read_dir()
        .map(|mut d| d.next().is_some())
        .unwrap_or(false)
}

#[derive(Debug, Clone)]
pub struct BrightnessInfo {
    pub available: bool,
    pub brightness: u8,
}

pub fn available() -> bool {
    backlight_devices_exist()
}

pub fn get() -> BrightnessInfo {
    if !backlight_devices_exist() {
        return BrightnessInfo { available: false, brightness: 100 };
    }

    let current = run(&["brightnessctl", "--class=backlight", "g"], 3000);
    let maximum = run(&["brightnessctl", "--class=backlight", "m"], 3000);
    let (Some((_, cur, _)), Some((_, max, _))) = (current, maximum) else {
        return BrightnessInfo { available: false, brightness: 100 };
    };

    let (Ok(cur_i), Ok(max_i)) = (cur.trim().parse::<u32>(), max.trim().parse::<u32>()) else {
        return BrightnessInfo { available: false, brightness: 100 };
    };

    if max_i == 0 {
        return BrightnessInfo { available: false, brightness: 100 };
    }

    BrightnessInfo {
        available: true,
        brightness: (cur_i * 100 / max_i) as u8,
    }
}

pub fn set(value: u8) -> bool {
    if !backlight_devices_exist() {
        return false;
    }
    run(
        &["brightnessctl", "--class=backlight", "set", &format!("{value}%")],
        3000,
    ).is_some()
}
