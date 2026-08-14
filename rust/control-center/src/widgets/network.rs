// ==========================================
// network.rs — tarjeta de red (port de widgets/network.py)
// ==========================================

use gtk::prelude::*;

use super::card::Card;
use super::open_popup;
use crate::widgets::SystemInfo;

pub struct NetworkCard {
    card: Card,
}

impl NetworkCard {
    pub fn new(window: &gtk::ApplicationWindow) -> Self {
        let card = Card::new("wifi.svg", "Network", "Loading...");

        let win = window.clone();
        card.button.connect_clicked(move |_| {
            open_popup(&win, "network");
        });

        Self { card }
    }

    pub fn button(&self) -> &gtk::Button {
        &self.card.button
    }

    pub fn apply_info(&self, info: &SystemInfo) {
        if info.ethernet_connected {
            let subtitle = format!("Ethernet{}", 
                if !info.ethernet_name.is_empty() { format!(" • {}", info.ethernet_name) } else { String::new() });
            self.card.set_state(Some(&subtitle), Some("ethernet.svg"));
            return;
        }

        if !info.wifi_connected && info.wifi_strength == 0 && info.wifi_name.is_empty() {
            self.card.set_state(Some("Unavailable"), Some("wifi.svg"));
            return;
        }

        if info.wifi_connected {
            self.card.set_state(Some(&info.wifi_name), Some("wifi.svg"));
        } else {
            self.card.set_state(Some("Disconnected"), Some("wifi.svg"));
        }
    }
}