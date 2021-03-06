# window.py
#
# Copyright 2019 Phie
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import gi
from gi.repository import Gtk, Gdk
gi.require_version('WebKit2', '4.0')
from gi.repository import WebKit2
from .gi_composites import GtkTemplate
from .settings_manager import *

@GtkTemplate(ui='/org/gnome/Carnetgtk/window.ui')
class CarnetgtkWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'CarnetgtkWindow'

    webview = GtkTemplate.Child()
    header_bar = GtkTemplate.Child()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        WebKit2.WebView()
        self.init_template()
        settingsManager.setHeaderBarBG(self.convert_to_hex(self.header_bar.get_style_context().get_background_color(Gtk.StateFlags.ACTIVE)))
        #self.webview.load_uri("file:///home/phieelementary/Dev/GitBis/QuickDoc/CarnetNextcloud/templates/CarnetElectron/index.html")
        self.webview.connect("notify::title", self.window_title_change) #only way to receive messages...
        self.webview.load_uri("http://google.fr")
        self.switch_to_browser()

        #self.webview.get_inspector().detach()

    def convert_to_hex(self, rgba_color) :
        red = int(rgba_color.red*255)
        green = int(rgba_color.green*255)
        blue = int(rgba_color.blue*255)
        return '{r:02x}{g:02x}{b:02x}'.format(r=red,g=green,b=blue)

    def on_format_clicked(self, view):
        print("on format clicked")
        self.toggle_toolbar("format-toolbar")

    def on_edit_clicked(self, view):
        print("on format clicked")
        self.toggle_toolbar("edit-toolbar")

    def on_media_clicked(self, view):
        print("on format clicked")
        self.toggle_toolbar("media-toolbar")

    def on_tools_clicked(self, view):
        print("on format clicked")
        self.toggle_toolbar("tools-toolbar")

    def toggle_toolbar(self, toolbar):
        self.webview.run_javascript("writerFrame.contentWindow.writer.toolbarManager.toggleToolbar(writerFrame.contentWindow.document.getElementById('"+toolbar+"'))")

    def window_title_change(self, v, param):
        print("on title changed")
        if not v.get_title():
            return
        if v.get_title().startswith("msgtopython:::"):
            message = v.get_title().split(":::",1)[1]
            # Now, send a message back to JavaScript
            if(message == "noteloaded"):
                self.switch_to_editor()
            elif(message == "exit"):
                self.switch_to_browser()

    def switch_to_editor(self):
        for child in self.header_bar.get_children():
            if(child.get_name() == "new-note"):
                child.hide()
            elif(child.get_name() == "new-folder"):
                child.hide()
        for child in self.header_bar.get_custom_title().get_children():
            if(child.get_name() == "title-label"):
                child.hide()
            elif(child.get_name() == "editor-box"):
                child.show()
    def switch_to_browser(self):
        for child in self.header_bar.get_children():
            if(child.get_name() == "new-note"):
                child.show()
            elif(child.get_name() == "new-folder"):
                child.show()
        for child in self.header_bar.get_custom_title().get_children():
            if(child.get_name() == "title-label"):
                child.show()
            elif(child.get_name() == "editor-box"):
                child.hide()

