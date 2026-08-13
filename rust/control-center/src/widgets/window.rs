// ==========================================
// window.rs — ventana del control center (port de window.py)
// ==========================================

use std::rc::Rc;

use gtk::prelude::*;

use churros_services::spawn;

use super::super::assets;
use super::audio::AudioCard;
use super::battery::BatteryCard;
use super::bluetooth::BluetoothCard;
use super::brightness::BrightnessCard;
use super::network::NetworkCard;
use super::power::PowerButton;

pub struct ControlCenterWindow {
    window: gtk::ApplicationWindow,
    network: NetworkCard,
    bluetooth: BluetoothCard,
    brightness: BrightnessCard,
    battery: BatteryCard,
    audio: AudioCard,
}

impl ControlCenterWindow {
    pub fn new(app: &gtk::Application) -> Rc<Self> {
        let window = gtk::ApplicationWindow::builder()
            .application(app)
            .title("Control Center")
            .build();

        window.set_default_size(430, 650);
        window.set_resizable(false);
        window.set_decorated(false);
        window.add_css_class("control-center");

        let network = NetworkCard::new(&window);
        let bluetooth = BluetoothCard::new(&window);
        let brightness = BrightnessCard::new(&window);
        let battery = BatteryCard::new(&window);
        let audio = AudioCard::new();

        let root = gtk::Box::new(gtk::Orientation::Vertical, 20);
        root.set_margin_top(20);
        root.set_margin_bottom(20);
        root.set_margin_start(20);
        root.set_margin_end(20);

        root.append(&Self::build_header(&window));

        let grid = gtk::Grid::new();
        grid.set_column_homogeneous(true);
        grid.set_row_spacing(16);
        grid.set_column_spacing(16);

        grid.attach(network.button(), 0, 0, 1, 1);
        grid.attach(bluetooth.button(), 1, 0, 1, 1);
        grid.attach(brightness.button(), 0, 1, 1, 1);
        grid.attach(battery.button(), 1, 1, 1, 1);

        root.append(&grid);
        root.append(audio.box_());

        window.set_child(Some(&root));

        let win = Rc::new(Self {
            window,
            network,
            bluetooth,
            brightness,
            battery,
            audio,
        });

        win.wire();
        win
    }

    fn build_header(window: &gtk::ApplicationWindow) -> gtk::Box {
        let header = gtk::Box::new(gtk::Orientation::Horizontal, 12);

        let logo = gtk::Image::from_file(assets::logo_path());
        logo.set_pixel_size(40);

        let titles = gtk::Box::new(gtk::Orientation::Vertical, 0);
        titles.set_hexpand(true);

        let title = gtk::Label::new(Some("ChurrOS"));
        title.add_css_class("title");
        title.set_xalign(0.0);

        let subtitle = gtk::Label::new(Some("Control Center"));
        subtitle.add_css_class("subtitle");
        subtitle.set_xalign(0.0);

        titles.append(&title);
        titles.append(&subtitle);

        let settings_btn = gtk::Button::from_icon_name("preferences-system");
        settings_btn.set_tooltip_text(Some("Settings"));
        settings_btn.add_css_class("settings-button");

        let win = window.clone();
        settings_btn.connect_clicked(move |_| {
            spawn(&["churros-settings"]);
            win.close();
        });

        header.append(&logo);
        header.append(&titles);
        header.append(&settings_btn);
        header.append(PowerButton::new(window).button());

        header
    }

    pub fn window(&self) -> &gtk::ApplicationWindow {
        &self.window
    }

    fn wire(self: &Rc<Self>) {
        let controller = gtk::EventControllerKey::new();
        let win = self.window.clone();
        controller.connect_key_pressed(move |_, key, _, _| {
            if key == gtk::gdk::Key::Escape {
                win.close();
                glib::Propagation::Stop
            } else {
                glib::Propagation::Proceed
            }
        });
        self.window.add_controller(controller);

        glib::timeout_add_seconds_local(2, glib::clone!(#[strong(rename_to = this)] self, move || {
            this.refresh();
            glib::ControlFlow::Continue
        }));
    }

    fn refresh(&self) {
        self.network.update();
        self.bluetooth.update();
        self.brightness.update();
        self.battery.update();
        self.audio.update();
    }
}