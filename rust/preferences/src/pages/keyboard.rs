// ==========================================
// KeyboardPage — atajos de teclado de Niri
// (equivalente a pages/keyboard.py)
// ==========================================

use gtk::prelude::*;

use std::cell::RefCell;
use std::rc::Rc;

use crate::services::keyboard::{Bind, KeyboardService};
use crate::widgets::group::Group;
use crate::widgets::page::Page;
use crate::widgets::row::Row;

const ACTION_TYPES: [(&str, &str); 3] = [
    ("spawn", "Ejecutar programa"),
    ("spawn-sh", "Ejecutar shell"),
    ("builtin", "Accion de Niri"),
];

fn categorize(cmd: &str, bind_type: &str) -> &'static str {
    let c = cmd.to_lowercase();
    let c = c.as_str();

    if bind_type == "spawn" || bind_type == "spawn-sh" {
        if ["churros", "thunar", "fuzzel", "foot", "store"]
            .iter()
            .any(|w| c.contains(w))
        {
            return "Aplicaciones";
        }
        return "Aplicaciones";
    }

    let wm = [
        "close-window",
        "quit",
        "maximize-column",
        "fullscreen-window",
        "switch-preset-column-width",
        "toggle-window-floating",
        "switch-focus-between-floating-and-tiling",
    ];
    if wm.contains(&cmd) {
        return "Ventanas";
    }

    let move_keys = [
        "focus-column-left",
        "focus-column-right",
        "focus-window-up",
        "focus-window-down",
        "move-column-left",
        "move-column-right",
        "move-window-up",
        "move-window-down",
    ];
    if move_keys.contains(&cmd) {
        return "Movimiento";
    }

    if cmd.contains("focus-workspace") || cmd.contains("move-window-to-workspace") {
        return "Workspaces";
    }

    if cmd.contains("screenshot") {
        return "Capturas";
    }

    if cmd.contains("hotkey-overlay") || cmd.contains("toggle-overview") {
        return "Overlays";
    }

    if cmd.contains("battery") || cmd.contains("XFBattery") || cmd.contains("playerctl") {
        return "Multimedia";
    }

    if ["wpctl", "pamixer", "audio", "mute", "volume"]
        .iter()
        .any(|w| cmd.contains(w))
    {
        return "Audio";
    }

    if cmd.to_lowercase().contains("brightness") {
        return "Multimedia";
    }

    "Niri"
}

fn bind_summary(bind: &Bind) -> String {
    let type_label = ACTION_TYPES
        .iter()
        .find(|(t, _)| t == &bind.kind)
        .map(|(_, l)| *l)
        .unwrap_or(bind.kind.as_str());

    let summary = if bind.kind == "spawn" && !bind.command.is_empty() {
        if bind.args.is_empty() {
            bind.command.clone()
        } else {
            format!("{} {}", bind.command, bind.args)
        }
    } else if bind.kind == "spawn-sh" && !bind.command.is_empty() {
        format!("shell: {}", bind.command)
    } else if bind.kind == "builtin" && !bind.command.is_empty() {
        if bind.args.is_empty() {
            bind.command.clone()
        } else {
            format!("{} {}", bind.command, bind.args)
        }
    } else {
        if bind.command.is_empty() {
            "(vacio)".to_string()
        } else {
            bind.command.clone()
        }
    };

    let _ = type_label;
    summary
}

pub fn build(navigator: gtk::Stack) -> Page {
    let page = Page::new(
        Some(navigator),
        "Atajos de teclado",
        Some("Modifica los atajos de teclado de Niri"),
        None,
    );

    build_content(&page);

    page
}

fn build_content(page: &Page) {
    let binds = KeyboardService::get_keybinds();

    let mut hint = Group::new("Info");
    hint.add(&Row::new(
        "Haz clic en un atajo para editarlo",
        Some("Los cambios se guardan en config.kdl al instante"),
        Some("system.svg"),
        None,
        None,
        None,
    ));
    page.add(hint.widget());

    let mut add_group = Group::new("Agregar");
    add_group.add(&Row::new(
        "Agregar nuevo atajo",
        Some("Define una nueva combinacion de teclas"),
        Some("system.svg"),
        None,
        None,
        Some(Box::new(|_btn| {
            // TODO: diálogo de nuevo atajo (equivalente a _add_new_bind)
            eprintln!("[keyboard] add new bind dialog pendiente de portar");
        })),
    ));
    page.add(add_group.widget());

    let mut categories: Vec<(&str, Vec<Bind>)> = [
        "Aplicaciones",
        "Ventanas",
        "Workspaces",
        "Movimiento",
        "Capturas",
        "Overlays",
        "Multimedia",
        "Audio",
        "Niri",
    ]
    .iter()
    .map(|c| (*c, Vec::new()))
    .collect();

    for bind in &binds {
        let cat = categorize(&bind.command, &bind.kind);
        if let Some((_, list)) = categories.iter_mut().find(|(name, _)| name == &cat) {
            list.push(bind.clone());
        }
    }

    for (cat_name, cat_binds) in categories {
        if cat_binds.is_empty() {
            continue;
        }

        let mut group = Group::new(cat_name);
        for bind in &cat_binds {
            let summary = bind_summary(bind);
            let type_label = ACTION_TYPES
                .iter()
                .find(|(t, _)| t == &bind.kind)
                .map(|(_, l)| *l)
                .unwrap_or(bind.kind.as_str())
                .to_string();

            group.add(&Row::new(
                &summary,
                Some(&type_label),
                Some("system.svg"),
                None,
                None,
                Some(Box::new(move |_btn| {
                    // TODO: diálogo de edición (equivalente a _edit_bind)
                    eprintln!("[keyboard] edit bind dialog pendiente de portar");
                })),
            ));
        }
        page.add(group.widget());
    }
}
