// ==========================================
// network.rs — tarjeta de red (port de widgets/network.py)
// ==========================================

use gtk::prelude::*;

use churros_services::ethernet;
use churros_services::wifi;

use super::card::Card;
use super::open_popup;

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

    pub fn update(&self) {
        let ethernet = ethernet::get();

        if ethernet.available && ethernet.connected {
            let mut subtitle = "Ethernet".to_string();
            if let Some(speed) = ethernet.speed {
                subtitle += &format!(" • {speed} Mbps");
            }
            self.card
                .set_state(Some(subtitle.as_str()), Some("ethernet.svg"));
            return;
        }

        let wifi = wifi::get();

        if !wifi.available {
            self.card.set_state(Some("Unavailable"), Some("wifi.svg"));
            return;
        }

        if !wifi.enabled {
            self.card.set_state(Some("Disabled"), Some("wifi.svg"));
            return;
        }

        match &wifi.connected {
            Some(ssid) => self.card.set_state(Some(ssid), Some("wifi.svg")),
            None => self.card.set_state(Some("Disconnected"), Some("wifi.svg")),
        }
    }
}