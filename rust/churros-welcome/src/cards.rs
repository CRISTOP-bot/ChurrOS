use gtk::prelude::*;

use crate::action_card;
use crate::actions;

const CARDS: [(&str, &str, &str, fn(&gtk::Button)); 3] = [
    (
        "install.svg",
        "Install ChurrOS",
        "Instala ChurrOS en tu disco duro.",
        actions::install_clicked,
    ),
    (
        "github.svg",
        "GitHub",
        "Repositorio oficial del proyecto.",
        actions::github_clicked,
    ),
    (
        "community.svg",
        "Comunidad",
        "Unete a la comunidad de ChurrOS.",
        actions::discord_clicked,
    ),
];

pub fn build() -> gtk::FlowBox {
    let flow = gtk::FlowBox::new();

    flow.set_selection_mode(gtk::SelectionMode::None);

    flow.set_max_children_per_line(3);
    flow.set_min_children_per_line(1);

    flow.set_row_spacing(20);
    flow.set_column_spacing(20);

    flow.set_halign(gtk::Align::Center);

    for (icon, title, description, callback) in CARDS {
        flow.append(&action_card::new(icon, title, description, callback));
    }

    flow
}
