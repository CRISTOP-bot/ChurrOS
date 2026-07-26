from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
PREFERENCES = Path(__file__).resolve().parents[5] / "preferences"

sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(PREFERENCES))

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GLib

from i18n import _

from services.wifi import WifiService

from widgets.network_item import NetworkItem
from widgets.password_dialog import PasswordDialog


class WifiWidget(Gtk.Box):

    def __init__(self):

        super().__init__(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=12
        )

        self.add_css_class("wifi-widget")

        self.last_state = None
        self.password_page = None

        self.stack = Gtk.Stack()
        self.stack.set_hexpand(True)
        self.stack.set_vexpand(True)
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(250)

        self.network_page = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=10
        )

        title = Gtk.Label(label=_("Wi-Fi"))
        title.set_xalign(0)
        title.add_css_class("section-title")
        self.network_page.append(title)

        self.toggle_widget = self._build_toggle()
        self.network_page.append(self.toggle_widget)

        self.network_list = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=10
        )

        self.network_scroller = Gtk.ScrolledWindow()
        self.network_scroller.set_policy(
            Gtk.PolicyType.NEVER,
            Gtk.PolicyType.AUTOMATIC
        )
        self.network_scroller.set_min_content_height(180)
        self.network_scroller.set_max_content_height(220)
        self.network_scroller.set_propagate_natural_height(False)
        self.network_scroller.set_child(self.network_list)
        self.network_scroller.set_vexpand(True)

        self.network_page.append(self.network_scroller)

        self.stack.add_named(self.network_page, "list")
        self.stack.set_visible_child_name("list")

        self.append(self.stack)

        self.reload()

        GLib.timeout_add_seconds(3, self.auto_refresh)

    def _build_toggle(self):

        box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=12
        )
        box.add_css_class("network-toggle")

        label = Gtk.Label(label=_("Wi-Fi"))
        label.add_css_class("network-label")
        label.set_hexpand(True)
        label.set_xalign(0)

        self.switch = Gtk.Switch()
        wifi = WifiService.get()
        if wifi["available"]:
            self.switch.set_active(wifi["enabled"])
        else:
            self.switch.set_sensitive(False)

        self.switch.connect("state-set", self.on_toggle)

        box.append(label)
        box.append(self.switch)

        return box

    def auto_refresh(self):

        if self.stack.get_visible_child_name() != "list":
            return True

        state = WifiService.get()

        if state != self.last_state:
            self.reload()

        return True

    def clear_network_page(self):

        child = self.network_list.get_first_child()

        while child is not None:

            self.network_list.remove(child)
            child = self.network_list.get_first_child()

    def show_message(self, text):

        label = Gtk.Label(label=text)
        label.set_xalign(0)
        label.add_css_class("network-info")
        self.network_list.append(label)

    def reload(self):

        self.last_state = WifiService.get()

        WifiService.scan()

        self.clear_network_page()

        if not self.last_state["available"]:

            self.show_message(_("No Wi-Fi adapter detected."))
            return

        if not self.last_state["enabled"]:

            self.show_message(_("Wi-Fi is disabled."))
            return

        if not self.last_state["networks"]:

            spinner = Gtk.Spinner()
            spinner.start()
            self.network_list.append(spinner)
            self.show_message(_("Searching for networks..."))
            return

        self.show_networks()

    def show_networks(self):

        actions_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=8
        )

        refresh = Gtk.Button(label=_("Refresh"))
        refresh.add_css_class("network-button")
        refresh.connect("clicked", lambda *_: self.reload())
        actions_box.append(refresh)

        hidden_btn = Gtk.Button(label=_("Connect to hidden network"))
        hidden_btn.add_css_class("network-button")
        hidden_btn.connect("clicked", lambda *_: self._show_hidden())
        actions_box.append(hidden_btn)

        self.network_list.append(actions_box)

        for network in self.last_state["networks"]:
            item = NetworkItem(
                network,
                self.select_network,
                self.forget_network
            )
            self.network_list.append(item)

    def forget_network(self, network):

        WifiService.forget(network["ssid"])
        self.reload()

    def select_network(self, network):

        if network["connected"]:

            WifiService.disconnect()
            self.reload()
            return

        if network["ssid"] == "Hidden Network":

            self._show_hidden()
            return

        secured = network["security"] not in ("", "--")

        if secured and not network["saved"]:
            self._show_password(network)
            return

        success, message = WifiService.connect(network["ssid"])
        self.reload()

        if not success:
            self.show_message(message)

    def _show_password(self, network):

        if self.password_page is not None:
            self.stack.remove(self.password_page)

        self.password_page = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=12
        )

        back = Gtk.Button(label=_("Back"))
        back.add_css_class("network-button")
        back.connect("clicked", lambda *_: self.back())

        dialog = PasswordDialog(network, self.back)

        self.password_page.append(back)
        self.password_page.append(dialog)

        self.stack.add_named(self.password_page, "password")
        self.stack.set_visible_child_name("password")

    def _show_hidden(self):

        if self.password_page is not None:
            self.stack.remove(self.password_page)

        self.password_page = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=12
        )
        self.password_page.add_css_class("hidden-dialog")

        back = Gtk.Button(label=_("Back"))
        back.add_css_class("network-button")
        back.connect("clicked", lambda *_: self.back())

        title = Gtk.Label(label=_("Connect to hidden network"))
        title.set_xalign(0)
        title.add_css_class("section-title")

        ssid_entry = Gtk.Entry()
        ssid_entry.set_placeholder_text("SSID")

        password_entry = Gtk.Entry()
        password_entry.set_visibility(False)
        password_entry.set_placeholder_text(_("Password"))

        error_label = Gtk.Label()
        error_label.set_xalign(0)
        error_label.add_css_class("network-error")

        connect_btn = Gtk.Button(label=_("Connect"))
        connect_btn.add_css_class("suggested-action")

        def do_connect(*_):

            ssid = ssid_entry.get_text().strip()

            if not ssid:
                error_label.set_label(_("SSID required."))
                return

            pwd = password_entry.get_text()
            success, message = WifiService.connect_hidden(ssid, pwd or None)

            if success:
                self.back()
            else:
                error_label.set_label(message)

        connect_btn.connect("clicked", do_connect)

        self.password_page.append(back)
        self.password_page.append(title)
        self.password_page.append(ssid_entry)
        self.password_page.append(password_entry)
        self.password_page.append(connect_btn)
        self.password_page.append(error_label)

        self.stack.add_named(self.password_page, "hidden")
        self.stack.set_visible_child_name("hidden")

    def back(self):

        self.stack.set_visible_child_name("list")
        if self.password_page is not None:
            self.stack.remove(self.password_page)
            self.password_page = None

        self.reload()

    def on_toggle(self, switch, state):

        if state:
            WifiService.enable()
        else:
            WifiService.disable()

        return False
