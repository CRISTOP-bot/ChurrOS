// ==========================================
// Page — base de todas las páginas de configuración
// (equivalente a widgets/page.py)
// ==========================================

use gtk::prelude::*;

pub struct Page {
    pub scrolled: gtk::ScrolledWindow,
    pub content: gtk::Box,
    pub navigator: Option<gtk::Stack>,
    pub parent_page: Option<String>,
}

impl Page {
    pub fn new(
        navigator: Option<gtk::Stack>,
        title: &str,
        subtitle: Option<&str>,
        parent_page: Option<String>,
    ) -> Self {
        let scrolled = gtk::ScrolledWindow::new();
        scrolled.set_hexpand(true);
        scrolled.set_vexpand(true);
        scrolled.set_policy(gtk::PolicyType::Never, gtk::PolicyType::Automatic);

        let root = gtk::Box::new(gtk::Orientation::Vertical, 18);
        root.set_margin_top(24);
        root.set_margin_bottom(24);
        root.set_margin_start(24);
        root.set_margin_end(24);

        scrolled.set_child(Some(&root));

        // Botón de retroceso (subpáginas)
        if let Some(parent) = parent_page.clone() {
            let back_btn = gtk::Button::builder()
                .label(" Atras")
                .halign(gtk::Align::Start)
                .has_frame(false)
                .build();
            back_btn.add_css_class("back-button");
            back_btn.set_icon_name("go-previous-symbolic");

            let navigator = navigator.clone();
            back_btn.connect_clicked(move |_| {
                if let Some(stack) = &navigator {
                    stack.set_visible_child_name(&parent);
                }
            });

            root.append(&back_btn);
        }

        // Cabecera
        let header = gtk::Box::new(gtk::Orientation::Vertical, 4);

        let title_label = gtk::Label::builder()
            .label(title)
            .xalign(0.0)
            .build();
        title_label.add_css_class("page-title");
        header.append(&title_label);

        if let Some(sub) = subtitle {
            let subtitle_label = gtk::Label::builder()
                .label(sub)
                .xalign(0.0)
                .build();
            subtitle_label.add_css_class("page-subtitle");
            header.append(&subtitle_label);
        }

        root.append(&header);

        // Contenido
        let content = gtk::Box::new(gtk::Orientation::Vertical, 18);
        root.append(&content);

        Self {
            scrolled,
            content,
            navigator,
            parent_page,
        }
    }

    pub fn widget(&self) -> &gtk::ScrolledWindow {
        &self.scrolled
    }

    pub fn add(&self, widget: &impl IsA<gtk::Widget>) {
        self.content.append(widget);
    }
}
