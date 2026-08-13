// ==========================================
// NavigationRow — fila que navega a otra página
// (equivalente a widgets/navigation_row.py)
// ==========================================

use gtk::prelude::*;

use crate::widgets::row::Row;

pub fn new(
    navigator: gtk::Stack,
    title: &str,
    icon: &str,
    page_name: &str,
    subtitle: Option<&str>,
) -> Row {
    let arrow = gtk::Image::from_icon_name("go-next-symbolic");
    arrow.add_css_class("row-arrow");

    let arrow_widget: &gtk::Widget = arrow.upcast_ref();
    let stack = navigator.clone();
    let target = page_name.to_string();

    Row::new(
        title,
        subtitle,
        Some(icon),
        None,
        Some(arrow_widget),
        Some(Box::new(move |_| {
            stack.set_visible_child_name(&target);
        })),
    )
}
