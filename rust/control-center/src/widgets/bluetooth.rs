// ==========================================
// bluetooth.rs — tarjeta de bluetooth (port de widgets/bluetooth.py)
// ==========================================

use gtk::prelude::*;

use churros_services::bluetooth;

use super::card::Card;
use super::open_popup;

pub struct BluetoothCard {
    card: Card,
}

impl BluetoothCard {
    pub fn new(window: &gtk::ApplicationWindow) -> Self {
        let card = Card::new("bluetooth.svg", "Bluetooth", "Unavailable");

        let win = window.clone();
        card.button.connect_clicked(move |_| {
            open_popup(&win, "bluetooth");
        });

        Self { card }
    }

    pub fn button(&self) -> &gtk::Button {
        &self.card.button
    }

    pub fn update(&self) {
        if !bluetooth::available() {
            self.card
                .set_state(Some("Unavailable"), Some("bluetooth_disabled.svg"));
            return;
        }

        if bluetooth::is_blocked() {
            self.card
                .set_state(Some("Blocked"), Some("bluetooth_disabled.svg"));
            return;
        }

        if bluetooth::is_enabled() {
            let connected = bluetooth::list_devices()
                .iter()
                .filter(|device| device.connected)
                .count();

            if connected > 0 {
                let subtitle = format!("{connected} Connected");
                self.card
                    .set_state(Some(subtitle.as_str()), Some("bluetooth.svg"));
            } else {
                self.card.set_state(Some("On"), Some("bluetooth.svg"));
            }
        } else {
            self.card
                .set_state(Some("Off"), Some("bluetooth_disabled.svg"));
        }
    }
}