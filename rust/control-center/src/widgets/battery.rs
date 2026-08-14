// ==========================================
// battery.rs — tarjeta de batería (port de widgets/battery.py)
// ==========================================

use gtk::prelude::*;

use super::card::Card;
use super::open_popup;
use crate::widgets::SystemInfo;

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

    pub fn apply_info(&self, info: &SystemInfo) {
        if info.battery_percent == 0 && !info.battery_charging {
            self.card.set_state(Some("Desktop"), Some("battery.svg"));
            return;
        }

        let icon = if info.battery_percent <= 15 {
            "battery_critical.svg"
        } else {
            "battery.svg"
        };

        let mut subtitle = format!("{}%", info.battery_percent);

        if info.battery_charging {
            subtitle += " • Charging";
        }

        self.card.set_state(Some(&subtitle), Some(icon));
    }
}