// ==========================================
// audio.rs — popup de audio (port de audio/window.py + widgets)
// ==========================================

use std::cell::Cell;
use std::rc::Rc;

use churros_services::audio;
use gtk::prelude::*;

use crate::popup::PopupWindow;

pub fn build(app: &gtk::Application) -> PopupWindow {
    let w = PopupWindow::new(app, "Audio", "󰕾", "audio.css");

    w.add(&section_label("Output"));
    w.add(&volume_widget(false));
    w.add(&device_widget(false));
    w.add(&mute_widget(false));
    w.add(&gtk::Separator::new(gtk::Orientation::Horizontal));
    w.add(&section_label("Input"));
    w.add(&volume_widget(true));
    w.add(&device_widget(true));
    w.add(&mute_widget(true));

    w
}

fn section_label(text: &str) -> gtk::Label {
    let label = gtk::Label::new(Some(text));
    label.add_css_class("audio-section-label");
    label.set_xalign(0.0);
    label
}

/// Slider de volumen con refresco de 1s (port de audio/widgets/volume.py).
fn volume_widget(source: bool) -> gtk::Box {
    let vbox = gtk::Box::new(gtk::Orientation::Vertical, 8);
    vbox.add_css_class("volume-widget");

    let box_ = gtk::Box::new(gtk::Orientation::Horizontal, 12);

    let icon = gtk::Label::new(Some(if source { "󰍜" } else { "󰕾" }));
    icon.add_css_class("volume-icon");

    let slider = gtk::Scale::with_range(gtk::Orientation::Horizontal, 0.0, 100.0, 1.0);
    slider.set_draw_value(false);
    slider.set_hexpand(true);
    slider.set_digits(0);
    slider.set_round_digits(0);

    let label = gtk::Label::new(None);
    label.set_xalign(1.0);
    label.add_css_class("volume-label");

    box_.append(&icon);
    box_.append(&slider);
    box_.append(&label);
    vbox.append(&box_);

    if !audio::available() {
        label.set_label("—");
        slider.set_sensitive(false);
        return vbox;
    }

    let get_volume = move || {
        if source {
            audio::get_input_volume()
        } else {
            audio::get_volume()
        }
    };
    let set_volume = move |value: u8| {
        if source {
            audio::set_input_volume(value);
        } else {
            audio::set_volume(value);
        }
    };

    let initial = get_volume();
    slider.set_value(initial as f64);
    label.set_label(&format!("{initial}%"));

    let suppress = Rc::new(Cell::new(false));

    let lab1 = label.clone();
    let suppress1 = suppress.clone();
    slider.connect_value_changed(move |s| {
        let value = s.value() as u8;
        suppress1.set(true);
        set_volume(value);
        lab1.set_label(&format!("{value}%"));
        suppress1.set(false);
    });

    let s2 = slider.clone();
    let lab2 = label.clone();
    let suppress2 = suppress.clone();
    glib::timeout_add_seconds_local(1, move || {
        if suppress2.get() {
            return glib::ControlFlow::Continue;
        }
        let current = get_volume();
        let active = s2.state_flags().contains(gtk::StateFlags::ACTIVE);
        if current != s2.value() as u8 && !active {
            suppress2.set(true);
            s2.set_value(current as f64);
            lab2.set_label(&format!("{current}%"));
            suppress2.set(false);
        }
        glib::ControlFlow::Continue
    });

    vbox
}

/// Selector de dispositivo con refresco (port de audio/widgets/device.py).
fn device_widget(source: bool) -> gtk::Box {
    let vbox = gtk::Box::new(gtk::Orientation::Vertical, 6);
    vbox.add_css_class("device-widget");

    let list = gtk::StringList::new(&[] as &[&str]);
    let dropdown = gtk::DropDown::new(Some(list), None::<&gtk::Expression>);
    dropdown.add_css_class("device-dropdown");

    let devices = Rc::new(std::cell::RefCell::new(Vec::<audio::AudioDevice>::new()));
    let updating = Rc::new(Cell::new(true));

    update_devices(&dropdown, &devices, &updating, source);

    let d1 = devices.clone();
    let u1 = updating.clone();
    dropdown.connect_notify_local(Some("selected"), move |dd, _| {
        if u1.get() {
            return;
        }
        let idx = dd.selected() as usize;
        let devs = d1.borrow();
        if idx < devs.len() {
            audio::set_default_sink(devs[idx].id);
        }
    });

    vbox.append(&dropdown);
    vbox
}

fn update_devices(
    dropdown: &gtk::DropDown,
    devices: &Rc<std::cell::RefCell<Vec<audio::AudioDevice>>>,
    updating: &Rc<Cell<bool>>,
    source: bool,
) {
    let list = if source {
        audio::list_sources()
    } else {
        audio::list_sinks()
    };

    *devices.borrow_mut() = list;

    let names: Vec<String> = devices.borrow().iter().map(|d| d.name.clone()).collect();
    let refs: Vec<&str> = names.iter().map(|s| s.as_str()).collect();
    let model = gtk::StringList::new(&refs);
    dropdown.set_model(Some(&model));

    updating.set(true);
    for (i, d) in devices.borrow().iter().enumerate() {
        if d.default {
            dropdown.set_selected(i as u32);
            break;
        }
    }
    updating.set(false);
}

/// Botón de mute con refresco de 1s (port de audio/widgets/mute.py).
fn mute_widget(source: bool) -> gtk::Button {
    let btn = gtk::Button::new();
    btn.add_css_class("mute-button");

    let is_muted = move || {
        if source {
            audio::is_input_muted()
        } else {
            audio::is_muted()
        }
    };
    let set_muted = move |value: bool| {
        if source {
            audio::set_input_mute(value);
        } else {
            audio::set_mute(value);
        }
    };
    let prefix = if source { "󰍚" } else { "󰝟" };

    let update_label = move |b: &gtk::Button, muted: bool| {
        let text = if muted { "Mute" } else { "Unmute" };
        if muted {
            b.add_css_class("muted");
        } else {
            b.remove_css_class("muted");
        }
        b.set_label(&format!("{prefix}  {text}"));
    };

    update_label(&btn, is_muted());

    btn.connect_clicked(move |b| {
        let current = is_muted();
        set_muted(!current);
        update_label(b, !current);
    });

    let b2 = btn.clone();
    glib::timeout_add_seconds_local(1, move || {
        update_label(&b2, is_muted());
        glib::ControlFlow::Continue
    });

    btn
}
