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

/// Indicador de batería: icono + porcentaje, estado, tiempo y barra visual
/// (port de battery/widgets/battery.py + barra de progreso).
fn battery_widget() -> gtk::Box {
    let vbox = gtk::Box::new(gtk::Orientation::Vertical, 12);
    vbox.add_css_class("battery-widget");

    let row = gtk::Box::new(gtk::Orientation::Horizontal, 12);

    let icon = gtk::Label::new(None);
    icon.add_css_class("battery-icon");

    let percentage = gtk::Label::new(None);
    percentage.add_css_class("battery-percentage");

    row.append(&icon);
    row.append(&percentage);

    let status = gtk::Label::new(None);
    status.add_css_class("battery-status");
    status.set_halign(gtk::Align::Start);

    let bar = gtk::LevelBar::builder()
        .min_value(0.0)
        .max_value(100.0)
        .value(0.0)
        .build();
    bar.add_css_class("battery-bar");

    let remaining = gtk::Label::new(None);
    remaining.add_css_class("battery-remaining");
    remaining.set_halign(gtk::Align::Start);

    vbox.append(&row);
    vbox.append(&status);
    vbox.append(&bar);
    vbox.append(&remaining);

    update(&icon, &percentage, &status, &bar, &remaining);

    glib::timeout_add_seconds_local(
        5,
        glib::clone!(
            #[strong] icon,
            #[strong] percentage,
            #[strong] status,
            #[strong] bar,
            #[strong] remaining,
            move || {
                update(&icon, &percentage, &status, &bar, &remaining);
                glib::ControlFlow::Continue
            }
        ),
    );

    vbox
}

fn update(
    icon: &gtk::Label,
    pct: &gtk::Label,
    status: &gtk::Label,
    bar: &gtk::LevelBar,
    remaining: &gtk::Label,
) {
    let data = battery::get();

    if !data.available {
        icon.set_label("");
        pct.set_label("No battery detected");
        status.set_visible(false);
        bar.set_visible(false);
        remaining.set_visible(false);
        return;
    }

    status.set_visible(true);
    bar.set_visible(true);
    remaining.set_visible(true);

    icon.set_label(&data.icon);
    pct.set_label(&format!("{}%", data.percentage));
    bar.set_value(data.percentage as f64);

    let charging = data.state == "charging";
    if charging {
        status.add_css_class("charging");
        status.remove_css_class("low");
    } else if data.percentage < 20 {
        status.add_css_class("low");
        status.remove_css_class("charging");
    } else {
        status.remove_css_class("charging");
        status.remove_css_class("low");
    }
    status.set_label(&state_label(&data.state));

    if data.state == "charging" && !data.time_to_full.is_empty() {
        remaining.set_label(&format!("{} until full", data.time_to_full));
    } else if data.state == "discharging" && !data.time_to_empty.is_empty() {
        remaining.set_label(&format!("{} until empty", data.time_to_empty));
    } else {
        remaining.set_label("");
    }
}