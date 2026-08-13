// ==========================================
// battery.rs — tarjeta de batería (port de widgets/battery.py)
// ==========================================

use gtk::prelude::*;

use churros_services::battery;

use super::card::Card;
use super::open_popup;

pub struct BatteryCard {
    card: Card,
}

impl BatteryCard {
    pub fn new(window: &gtk::ApplicationWindow) -> Self {
        let card = Card::new("battery.svg", "Battery", "Loading...");

        let win = window.clone();
        card.button.connect_clicked(move |_| {
            open_popup(&win, "battery");
        });

        Self { card }
    }

    pub fn button(&self) -> &gtk::Button {
        &self.card.button
    }

    pub fn update(&self) {
        let battery = battery::get();

        if !battery.available {
            self.card.set_state(Some("Desktop"), Some("battery.svg"));
            return;
        }

        let percentage = battery.percentage;

        let icon = if percentage <= 15 {
            "battery_critical.svg"
        } else {
            "battery.svg"
        };

        let mut subtitle = format!("{percentage}%");

        match battery.state.as_str() {
            "charging" => subtitle += " • Charging",
            "fully-charged" => subtitle += " • Full",
            _ => {}
        }

        self.card.set_state(Some(subtitle.as_str()), Some(icon));
    }
}