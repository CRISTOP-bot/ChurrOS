// ==========================================
// audio.rs — tarjeta de audio (port de widgets/audio.py)
// ==========================================

use gtk::prelude::*;

use churros_services::audio;

use super::super::assets;

pub struct AudioCard {
    box_: gtk::Box,
    icon: gtk::Image,
    subtitle: gtk::Label,
    scale: gtk::Scale,
}

impl AudioCard {
    pub fn new() -> Self {
        let box_ = gtk::Box::new(gtk::Orientation::Vertical, 12);
        box_.add_css_class("card");
        box_.set_margin_top(18);
        box_.set_margin_bottom(18);
        box_.set_margin_start(18);
        box_.set_margin_end(18);

        let header = gtk::Box::new(gtk::Orientation::Horizontal, 12);

        let icon = gtk::Image::from_file(assets::icon_path("audio.svg"));
        icon.set_pixel_size(28);

        let labels = gtk::Box::new(gtk::Orientation::Vertical, 0);

        let title = gtk::Label::new(Some("Audio"));
        title.add_css_class("card-title");
        title.set_xalign(0.0);

        let subtitle = gtk::Label::new(None::<&str>);
        subtitle.add_css_class("card-subtitle");
        subtitle.set_xalign(0.0);

        labels.append(&title);
        labels.append(&subtitle);

        header.append(&icon);
        header.append(&labels);

        let scale = gtk::Scale::with_range(gtk::Orientation::Horizontal, 0.0, 100.0, 1.0);
        scale.set_hexpand(true);

        scale.connect_value_changed(|scale| {
            audio::set_volume(scale.value() as u8);
        });

        box_.append(&header);
        box_.append(&scale);

        Self {
            box_,
            icon,
            subtitle,
            scale,
        }
    }

    pub fn box_(&self) -> &gtk::Box {
        &self.box_
    }

    pub fn update(&self) {
        let volume = audio::get_volume();

        self.scale.set_value(volume as f64);
        self.subtitle.set_label(&format!("{volume}%"));

        let icon = if volume == 0 {
            "audio_muted.svg"
        } else {
            "audio.svg"
        };

        self.icon.set_from_file(Some(assets::icon_path(icon)));
    }
}