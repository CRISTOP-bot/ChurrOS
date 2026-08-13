// ==========================================
// PreferencesWindow — ventana principal
// (equivalente a window.py)
// ==========================================

use gtk::prelude::*;

use std::cell::RefCell;
use std::rc::Rc;

use crate::pages;
use crate::services::settings;
use crate::services::theme::ThemeService;
use crate::widgets::sidebar::Sidebar;

pub struct PreferencesWindow {
    pub window: gtk::ApplicationWindow,
    sidebar: Rc<RefCell<Sidebar>>,
    navigator: gtk::Stack,
    sidebar_revealer: gtk::Revealer,
    toggle_button: gtk::Button,
    history: Rc<RefCell<Vec<String>>>,
    narrow_threshold: i32,
    is_narrow: Rc<RefCell<bool>>,
}

impl PreferencesWindow {
    pub fn new(app: &gtk::Application) -> Self {
        let window = gtk::ApplicationWindow::builder()
            .application(app)
            .title("Configuración")
            .default_width(1280)
            .default_height(760)
            .build();

        window.add_css_class("preferences");
        apply_theme_class(&window);

        let w = window.clone();
        if let Some(schema_source) = gio::SettingsSchemaSource::default() {
            if let Some(schema) = schema_source.lookup("org.gnome.desktop.interface", false) {
                let settings =
                    gio::Settings::new_full(&schema, None::<&gio::SettingsBackend>, None::<&str>);
                settings.connect_changed(Some("color-scheme"), move |_, _| {
                    let w = w.clone();
                    glib::idle_add_local_once(move || refresh_theme(&w));
                });
            }
        }

        // Layout principal
        let root = gtk::Box::new(gtk::Orientation::Horizontal, 0);
        window.set_child(Some(&root));

        // Sidebar + revealer
        let sidebar = Rc::new(RefCell::new(Sidebar::new()));
        let sidebar_revealer = gtk::Revealer::new();
        sidebar_revealer.set_transition_type(gtk::RevealerTransitionType::SlideRight);
        sidebar_revealer.set_reveal_child(true);
        sidebar_revealer.set_child(Some(&sidebar.borrow().root));
        root.append(&sidebar_revealer);

        // Navegador con botón de toggle para modo estrecho
        let nav_box = gtk::Box::new(gtk::Orientation::Vertical, 0);

        let toggle_button = gtk::Button::from_icon_name("open-menu-symbolic");
        toggle_button.add_css_class("flat");
        toggle_button.set_halign(gtk::Align::End);
        toggle_button.set_margin_start(12);
        toggle_button.set_margin_end(12);
        toggle_button.set_margin_top(12);
        toggle_button.set_visible(false);

        nav_box.append(&toggle_button);

        let navigator = gtk::Stack::new();
        navigator.set_hexpand(true);
        navigator.set_vexpand(true);
        navigator.set_transition_type(gtk::StackTransitionType::SlideLeftRight);
        navigator.set_transition_duration(250);

        nav_box.append(&navigator);
        root.append(&nav_box);

        let history: Rc<RefCell<Vec<String>>> = Rc::new(RefCell::new(Vec::new()));
        let is_narrow: Rc<RefCell<bool>> = Rc::new(RefCell::new(false));

        let mut win = Self {
            window,
            sidebar,
            navigator,
            sidebar_revealer,
            toggle_button,
            history,
            narrow_threshold: 760,
            is_narrow,
        };

        win.register_pages();
        win.wire_sidebar();
        win.wire_shortcuts();
        win.wire_responsive();

        // Página inicial: última visitada o system
        let last_page = settings::get_string("preferences.last_page", "system");
        win.navigator.set_visible_child_name(&last_page);
        win.sidebar.borrow().select(&last_page);

        win
    }

    fn register_pages(&mut self) {
        // Páginas principales (se añaden al sidebar + al stack)
        self.register_main_page("system", "system.svg", "Sistema", |n| pages::system::build(n));
        self.register_main_page("about", "about.svg", "Acerca de", |n| pages::about::build(n));

        // Subpáginas registradas en el catálogo de búsqueda
        // (se añaden al stack según se porten)
        {
            let s = self.sidebar.borrow();
            s.register_subpage(
                "accent", "appearance", "Colores", "Color de acento del sistema", Some("palette.svg"));
            s.register_subpage(
                "icons", "appearance", "Iconos", "Tema de iconos", Some("icons.svg"));
            s.register_subpage(
                "cursor", "appearance", "Cursor", "Tema y tamano del cursor", Some("cursor.svg"));
            s.register_subpage(
                "fonts", "appearance", "Fuentes", "Familia y tamano de fuente", Some("font.svg"));
            s.register_subpage(
                "waybar", "appearance", "Waybar", "Barra: posicion, colores, modulos", Some("waybar.svg"));
            s.register_subpage(
                "niri", "appearance", "Niri", "Compositor: disposicion, bordes, blur", Some("niri.svg"));
            s.register_subpage(
                "foot", "appearance", "Foot", "Terminal: fuente, cursor, padding, bell", Some("terminal.svg"));
            s.register_subpage(
                "fuzzel", "appearance", "Fuzzel", "Launcher: fuente, layout, iconos", Some("applications.svg"));
            s.register_subpage(
                "mako", "appearance", "Mako", "Notificaciones: fuente, colores, posicion, DND", Some("mako.svg"));
            s.register_subpage(
                "wallpaper", "appearance", "Fondo", "Cambiar el fondo de pantalla", Some("wallpaper.svg"));
            s.register_subpage(
                "night-light", "appearance", "Luz nocturna", "Temperatura de color y filtro de luz azul", Some("night_light.svg"));
            s.register_subpage(
                "lock-screen", "appearance", "Pantalla de bloqueo", "swaylock + swayidle: estilo y bloqueo automatico", Some("lock_screen.svg"));
            s.register_subpage(
                "power-profile", "power", "Perfiles de energia", "Performance, balanced o power-saver", None);
            s.register_subpage(
                "battery", "power", "Bateria", "Estado, nivel y opciones de bateria", None);
            s.register_subpage(
                "display-timeout", "display", "Apagado de pantalla", "Tiempo antes de apagar la pantalla", None);
            s.register_subpage(
                "sleep", "power", "Suspension", "Tiempo antes de suspender el sistema", None);
            s.register_subpage(
                "backup", "system", "Copia de seguridad", "Exportar, importar o restablecer la configuracion", Some("backup.svg"));
            s.register_subpage(
                "logs", "system", "Logs de Niri", "Registros del compositor y validacion", Some("logs.svg"));
            s.register_subpage(
                "window-rules", "appearance", "Reglas de ventana", "Opacidad, flotantes, esquinas, blur", Some("window_rules.svg"));
        }
    }

    fn register_main_page(
        &mut self,
        id: &str,
        icon: &str,
        title: &str,
        builder: impl FnOnce(gtk::Stack) -> crate::widgets::page::Page,
    ) {
        let page = builder(self.navigator.clone());
        self.navigator.add_named(page.widget(), Some(id));
        self.sidebar.borrow_mut().register_page(id, icon, title);
    }

    fn wire_sidebar(&mut self) {
        // Sidebar -> navegar
        let navigator = self.navigator.clone();
        let history = Rc::clone(&self.history);
        let sidebar_revealer = self.sidebar_revealer.clone();
        let is_narrow = Rc::clone(&self.is_narrow);
        let sidebar = Rc::clone(&self.sidebar);

        sidebar.borrow().connect_page_selected(move |page| {
            settings::set("preferences.last_page", serde_json::json!(page));

            // Guardar la página actual en la historia antes de navegar
            if let Some(current) = navigator.visible_child_name() {
                if current != page {
                    history.borrow_mut().push(current.to_string());
                }
            }
            navigator.set_visible_child_name(page);

            if *is_narrow.borrow() {
                sidebar_revealer.set_reveal_child(false);
            }
        });

        // Navegación (back / stack) -> sincronizar sidebar
        let sidebar2 = Rc::clone(&self.sidebar);
        self.navigator
            .connect_visible_child_name_notify(move |stack| {
                if let Some(name) = stack.visible_child_name() {
                    sidebar2.borrow().select(&name.to_string());
                }
            });
    }

    fn wire_shortcuts(&mut self) {
        let key_ctrl = gtk::EventControllerKey::new();
        key_ctrl.set_propagation_phase(gtk::PropagationPhase::Bubble);

        let sidebar_search = self.sidebar.borrow().search.widget().clone();
        let is_narrow = Rc::clone(&self.is_narrow);
        let sidebar_revealer = self.sidebar_revealer.clone();
        key_ctrl.connect_key_pressed(move |_controller, keyval, _keycode, state| {
            let ctrl = state.contains(gtk::gdk::ModifierType::CONTROL_MASK);
            let shift = state.contains(gtk::gdk::ModifierType::SHIFT_MASK);

            if ctrl && (keyval == gtk::gdk::Key::f || keyval == gtk::gdk::Key::F) {
                sidebar_search.grab_focus();
                return glib::Propagation::Proceed;
            }

            if ctrl && (keyval == gtk::gdk::Key::b || keyval == gtk::gdk::Key::B) {
                if *is_narrow.borrow() {
                    let revealed = sidebar_revealer.reveals_child();
                    sidebar_revealer.set_reveal_child(!revealed);
                }
                return glib::Propagation::Proceed;
            }

            if ctrl && shift && (keyval == gtk::gdk::Key::n || keyval == gtk::gdk::Key::N) {
                let revealed = sidebar_revealer.reveals_child();
                sidebar_revealer.set_reveal_child(!revealed);
                return glib::Propagation::Proceed;
            }

            glib::Propagation::Proceed
        });

        self.window.add_controller(key_ctrl);
    }

    fn wire_responsive(&mut self) {
        let window = self.window.clone();
        let sidebar_revealer = self.sidebar_revealer.clone();
        let toggle_button = self.toggle_button.clone();
        let is_narrow = Rc::clone(&self.is_narrow);
        let threshold = self.narrow_threshold;

        // Check cada 250ms mientras la ventana está mapeada
        let map_window = window.clone();
        map_window.connect_map(move |_| {
            let w = window.clone();
            let is_narrow = is_narrow.clone();
            let sidebar_revealer = sidebar_revealer.clone();
            let toggle_button = toggle_button.clone();
            glib::timeout_add_local(std::time::Duration::from_millis(250), move || {
                let width = w.width();
                let new_narrow = width < threshold;

                if *is_narrow.borrow() != new_narrow {
                    *is_narrow.borrow_mut() = new_narrow;
                    if new_narrow {
                        sidebar_revealer.set_reveal_child(false);
                        toggle_button.set_visible(true);
                    } else {
                        sidebar_revealer.set_reveal_child(true);
                        toggle_button.set_visible(false);
                    }
                }
                glib::ControlFlow::Continue
            });
        });

        // Toggle del sidebar (botón hamburguesa)
        let sidebar_revealer2 = self.sidebar_revealer.clone();
        self.toggle_button.connect_clicked(move |_| {
            let revealed = sidebar_revealer2.reveals_child();
            sidebar_revealer2.set_reveal_child(!revealed);
        });
    }
}

impl PreferencesWindow {
    pub fn present(&self) {
        self.window.present();
    }
}

fn apply_theme_class(window: &gtk::ApplicationWindow) {
    let want_light = !ThemeService::is_dark();
    let has_light = window.has_css_class("light");

    if want_light && !has_light {
        window.add_css_class("light");
    } else if !want_light && has_light {
        window.remove_css_class("light");
    }
}

fn refresh_theme(window: &gtk::ApplicationWindow) {
    apply_theme_class(window);
    window.queue_draw();
    window.queue_resize();
}
