// ==========================================
// bluetooth.rs — tarjeta de bluetooth (port de widgets/bluetooth.py)
// ==========================================

use gtk::prelude::*;

use super::card::Card;
use super::open_popup;
use crate::widgets::SystemInfo;

pub struct BluetoothCard {
    card: Card,
}

impl BluetoothCard {
    pub fn new(window: &gtk::ApplicationWindow) -> Self {
        let card = Card::new("bluetooth.svg", "Bluetooth", "Loading...");

        let win = window.clone();
        card.button.connect_clicked(move |_| {
            open_popup(&win, "bluetooth");
        });

        Self { card }
    }

    pub fn button(&self) -> &gtk::Button {
        &self.card.button
    }

    pub fn apply_info(&self, info: &SystemInfo) {
        if !info.bluetooth_enabled {
            self.card
                .set_state(Some("Unavailable"), Some("bluetooth_disabled.svg"));
            return;
        }

        if info.bluetooth_connected {
            let subtitle = if !info.bluetooth_device.is_empty() {
                info.bluetooth_device.as_str()
            } else {
                "Connected"
            };
            self.card
                .set_state(Some(subtitle), Some("bluetooth.svg"));
        } else {
            self.card.set_state(Some("On"), Some("bluetooth.svg"));
        }
    }
}