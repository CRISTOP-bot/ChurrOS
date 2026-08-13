// ==========================================
// battery.rs — popup de batería (port de battery/window.py + widgets)
// ==========================================

use churros_services::battery;
use gtk::prelude::*;

use crate::popup::PopupWindow;

pub fn build(app: &gtk::Application) -> PopupWindow {
    let w = PopupWindow::new(app, "Battery", "󰁹", "battery.css");
    w.add(&battery_widget());
    w
}

fn state_label(state: &str) -> String {
    match state {
        "charging" => "Charging".to_string(),
        "discharging" => "Discharging".to_string(),
        "fully-charged" => "Full".to_string(),
        "pending-charge" => "Pending charge".to_string(),
        "pending-discharge" => "Pending discharge".to_string(),
        "empty" => "Empty".to_string(),
        "unknown" => "Unknown".to_string(),
        other => title_case(other),
    }
}

/// Equivalente a str.title() de Python.
fn title_case(s: &str) -> String {
    let mut out = String::with_capacity(s.len());
    let mut capitalize = true;
    for ch in s.chars() {
        if ch.is_alphanumeric() {
            if capitalize {
                out.extend(ch.to_uppercase());
                capitalize = false;
            } else {
                out.push(ch);
            }
        } else {
            out.push(ch);
            capitalize = true;
        }
    }
    out
}

/// Etiquetas de porcentaje/estado/tiempo con refresco de 5s
/// (port de battery/widgets/battery.py).
fn battery_widget() -> gtk::Box {
    let vbox = gtk::Box::new(gtk::Orientation::Vertical, 12);
    vbox.add_css_class("battery-widget");

    let percentage = gtk::Label::new(None);
    percentage.add_css_class("battery-percentage");

    let status = gtk::Label::new(None);
    status.add_css_class("battery-status");

    let remaining = gtk::Label::new(None);
    remaining.add_css_class("battery-remaining");

    vbox.append(&percentage);
    vbox.append(&status);
    vbox.append(&remaining);

    update(&percentage, &status, &remaining);

    glib::timeout_add_seconds_local(
        5,
        glib::clone!(#[strong] percentage, #[strong] status, #[strong] remaining, move || {
            update(&percentage, &status, &remaining);
            glib::ControlFlow::Continue
        }),
    );

    vbox
}

fn update(pct: &gtk::Label, status: &gtk::Label, remaining: &gtk::Label) {
    let data = battery::get();

    if !data.available {
        pct.set_label("No battery detected");
        status.set_visible(false);
        remaining.set_visible(false);
        return;
    }

    status.set_visible(true);
    remaining.set_visible(true);

    pct.set_label(&format!("{} {}%", data.icon, data.percentage));
    status.set_label(&state_label(&data.state));

    if data.state == "charging" && !data.time_to_full.is_empty() {
        remaining.set_label(&format!("{} until full", data.time_to_full));
    } else if data.state == "discharging" && !data.time_to_empty.is_empty() {
        remaining.set_label(&format!("{} until empty", data.time_to_empty));
    } else {
        remaining.set_label("");
    }
}
