// ==========================================
// brightness.rs — tarjeta de brillo (port de widgets/brightness.py)
// ==========================================

use gtk::prelude::*;

use super::card::Card;
use super::open_popup;
use crate::widgets::SystemInfo;

pub struct BrightnessCard {
    card: Card,
}

impl BrightnessCard {
    pub fn new(window: &gtk::ApplicationWindow) -> Self {
        let card = Card::new("brightness.svg", "Brightness", "Loading...");

        let win = window.clone();
        card.button.connect_clicked(move |_| {
            open_popup(&win, "brightness");
        });

        Self { card }
    }

    pub fn button(&self) -> &gtk::Button {
        &self.card.button
    }

    pub fn apply_info(&self, info: &SystemInfo) {
        let subtitle = format!("{}%", info.brightness_percent);
        self.card.set_state(Some(&subtitle), Some("brightness.svg"));
    }
}