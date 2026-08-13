// ==========================================
// brightness.rs — tarjeta de brillo (port de widgets/brightness.py)
// ==========================================

use gtk::prelude::*;

use churros_services::brightness;

use super::card::Card;
use super::open_popup;

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

    pub fn update(&self) {
        let brightness = brightness::get();

        if !brightness.available {
            self.card
                .set_state(Some("Unavailable"), Some("brightness.svg"));
            return;
        }

        let subtitle = format!("{}%", brightness.brightness);
        self.card.set_state(Some(subtitle.as_str()), Some("brightness.svg"));
    }
}