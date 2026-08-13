// ==========================================
// brightness.rs — popup de brillo (port de brightness/window.py + widgets)
// ==========================================

use std::cell::Cell;
use std::rc::Rc;

use churros_services::brightness;
use gtk::prelude::*;

use crate::popup::PopupWindow;

pub fn build(app: &gtk::Application) -> PopupWindow {
    let w = PopupWindow::new(app, "Brightness", "󰃠", "brightness.css");
    w.add(&brightness_widget());
    w
}

/// Slider de brillo con refresco de 2s (port de brightness/widgets/brightness.py).
fn brightness_widget() -> gtk::Box {
    let vbox = gtk::Box::new(gtk::Orientation::Vertical, 12);
    vbox.add_css_class("brightness-widget");

    let label = gtk::Label::new(None);
    label.add_css_class("brightness-label");
    vbox.append(&label);

    let slider = gtk::Scale::with_range(gtk::Orientation::Horizontal, 0.0, 100.0, 1.0);
    slider.set_draw_value(false);
    slider.add_css_class("brightness-slider");
    slider.set_hexpand(true);
    vbox.append(&slider);

    let data = brightness::get();

    if data.available {
        slider.set_value(data.brightness as f64);
        label.set_label(&format!("󰃠 {}%", data.brightness));

        let suppress = Rc::new(Cell::new(false));

        let lab1 = label.clone();
        let suppress1 = suppress.clone();
        slider.connect_value_changed(move |s| {
            let value = s.value() as u8;
            suppress1.set(true);
            churros_services::spawn(&[
                "brightnessctl",
                "--class=backlight",
                "set",
                &format!("{value}%"),
            ]);
            lab1.set_label(&format!("󰃠 {value}%"));
            suppress1.set(false);
        });

        let s2 = slider.clone();
        let lab2 = label.clone();
        let suppress2 = suppress.clone();
        glib::timeout_add_seconds_local(2, move || {
            if suppress2.get() {
                return glib::ControlFlow::Continue;
            }
            let data = brightness::get();
            if data.available {
                let current = data.brightness;
                let active = s2.state_flags().contains(gtk::StateFlags::ACTIVE);
                if current != s2.value() as u8 && !active {
                    suppress2.set(true);
                    s2.set_value(current as f64);
                    lab2.set_label(&format!("󰃠 {current}%"));
                    suppress2.set(false);
                }
            }
            glib::ControlFlow::Continue
        });
    } else {
        slider.set_value(100.0);
        slider.set_sensitive(false);
        label.set_label("Brightness unavailable");

        let info = gtk::Label::new(Some("No software brightness control on this display."));
        info.set_wrap(true);
        info.set_xalign(0.0);
        info.add_css_class("brightness-info");
        vbox.append(&info);
    }

    vbox
}
