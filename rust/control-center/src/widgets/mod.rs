mod audio;
mod battery;
mod bluetooth;
mod brightness;
mod card;
mod network;
mod power;
mod window;

pub use window::{ControlCenterWindow, SystemInfo};

use gtk::prelude::*;

use churros_services::spawn;

/// Abre un popup cerrando primero la ventana del control center
/// (mismo comportamiento que popup_launcher.py).
pub fn open_popup(window: &gtk::ApplicationWindow, name: &str) {
    window.close();
    spawn(&["churros-popup", name]);
}