// ==========================================
// SliderRow — fila con Gtk::Scale
// (equivalente a widgets/slider_row.py)
// ==========================================

use gtk::prelude::*;

use crate::widgets::row::Row;

pub struct SliderRow {
    pub row: Row,
    pub scale: gtk::Scale,
}

impl SliderRow {
    pub fn new(
        title: &str,
        icon: Option<&str>,
        subtitle: Option<&str>,
        minimum: f64,
        maximum: f64,
        step: f64,
        value: f64,
        callback: Option<Box<dyn Fn(f64)>>,
    ) -> Self {
        let scale = gtk::Scale::with_range(gtk::Orientation::Horizontal, minimum, maximum, step);
        scale.set_draw_value(false);
        scale.set_hexpand(true);
        scale.set_value(value);
        scale.set_size_request(180, -1);

        if let Some(cb) = callback {
            scale.connect_value_changed(move |scale| {
                cb(scale.value());
            });
        }

        let scale_widget: &gtk::Widget = scale.upcast_ref();
        let row = Row::new(title, subtitle, icon, None, Some(scale_widget), None);

        Self { row, scale }
    }

    #[allow(dead_code)]
    pub fn widget(&self) -> &gtk::Button {
        self.row.widget()
    }

    pub fn get_value(&self) -> f64 {
        self.scale.value()
    }

    #[allow(dead_code)]
    pub fn set_value(&self, value: f64) {
        self.scale.set_value(value);
    }
}
