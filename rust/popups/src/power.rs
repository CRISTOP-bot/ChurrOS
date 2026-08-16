// ==========================================
// power.rs — popup de energía (port de power/window.py + widgets)
// ==========================================

use churros_services::power;
use gtk::prelude::*;

use crate::popup::PopupWindow;

pub fn build(app: &gtk::Application) -> PopupWindow {
    let w = PopupWindow::new(app, "Power", "󰐥", "power.css");
    w.add(&power_widget());
    w
}

/// Lista de acciones de energía (port de power/widgets/power.py).
fn power_widget() -> gtk::Box {
    let vbox = gtk::Box::new(gtk::Orientation::Vertical, 8);
    vbox.add_css_class("power-widget");

    let actions: [(&str, &str, fn()); 6] = [
        ("󰌾", "Lock", power::lock),
        ("󰍃", "Logout", power::logout),
        ("󰒲", "Suspend", power::suspend),
        ("󰤅", "Hibernate", power::hibernate),
        ("󰜉", "Restart", power::restart),
        ("󰐥", "Shutdown", power::shutdown),
    ];

    let can_hibernate = power::can_hibernate();

    for (icon, title, action) in actions {
        if title == "Hibernate" && !can_hibernate {
            continue;
        }
        let danger = title == "Restart" || title == "Shutdown";
        vbox.append(&power_button(icon, title, danger, action));
    }

    vbox
}

/// Botón de acción: icono + texto (port de power/widgets/button.py).
fn power_button(icon: &str, title: &str, danger: bool, action: fn()) -> gtk::Button {
    let btn = gtk::Button::new();
    btn.add_css_class("power-button");
    if danger {
        btn.add_css_class("danger");
    }

    let box_ = gtk::Box::new(gtk::Orientation::Horizontal, 12);

    let icon_label = gtk::Label::new(Some(icon));
    icon_label.add_css_class("power-icon");

    let text = gtk::Label::new(Some(title));
    text.set_hexpand(true);
    text.set_xalign(0.0);
    text.add_css_class("power-text");

    box_.append(&icon_label);
    box_.append(&text);
    btn.set_child(Some(&box_));

    btn.connect_clicked(move |_| action());

    btn
}
