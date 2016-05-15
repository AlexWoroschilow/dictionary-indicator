# Copyright 2015 Alex Woroschilow (alex.woroschilow@gmail.com)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

#gi.require_version('Gdk', '3.0')
#from gi.repository import Gdk

#gi.require_version('WebKit', '3.0')
#from gi.repository import WebKit


class DictionaryTranslationAreaWidget(Gtk.VBox):
    _label = None
    _webview = None
    _template = None

    def __init__(self, template):
        self._template = template
        Gtk.VBox.__init__(self, spacing=0)
        self.pack_start(self.widget_label, False, True, 0)
        self.pack_start(self.widget_translation, True, True, 0)

    @property
    def widget_label(self):
        self._label = Gtk.Label()
        self._label.set_margin_top(8)
        self._label.set_margin_bottom(8)
        return self._label

    @property
    def widget_translation(self):
        entity = Gtk.ScrolledWindow()
        entity.set_hexpand(True)
        entity.set_vexpand(True)
        entity.set_margin_left(5)
        entity.set_margin_right(5)
        entity.set_margin_bottom(5)
        entity.set_size_request(280, 400)

#        entity.add(self.widget_webview)
        return entity

    @property
    def widget_webview(self):
#        self._webview = WebKit.WebView()
#        return self._webview
        return None

    @property
    def label(self):
        pass

    @label.setter
    def label(self, value):
        self._label.set_markup("<big>%s</big>" % value)

    @property
    def content(self):
        pass

    @content.setter
    def content(self, value):
        print(value)
#        with open(self._template) as template:
#            self._webview.load_html_string(template.read() % value, 'text/html')
        pass

class DictionarySuggestionAreaWidget(Gtk.VBox):
    _tree = None
    _store = None
    _search = None

    def __init__(self):
        self._store = Gtk.ListStore(str)

        Gtk.VBox.__init__(self, homogeneous=False, spacing=0)

        self.pack_start(self.widget_search, False, False, 0)
        self.pack_start(self.widget_tree, True, True, 0)

    @property
    def text(self):
        return self._search.get_text()

    @text.setter
    def text(self, value):
        self._search.set_text(value)

    @property
    def suggestions(self):
        pass

    @suggestions.setter
    def suggestions(self, value):
        if self._store is not None:
            self._store.clear()
            for index, word in enumerate(value):
                self._store.append([word])
                if index is 30:
                    break

    @property
    def widget_search(self):
        self._search = Gtk.Entry()
        self._search.set_margin_left(5)
        self._search.set_margin_right(0)
        self._search.set_margin_top(5)
        self._search.set_margin_bottom(3)
        self._search.set_property("editable", True)
        return self._search

    @property
    def widget_tree(self):
        word = Gtk.CellRendererText()
        word.set_padding(5, 5)

        self._tree = Gtk.TreeView(model=self._store)
        self._tree.append_column(Gtk.TreeViewColumn("Similar words", word, text=0))

        entity = Gtk.ScrolledWindow()
        entity.set_hexpand(True)
        entity.set_vexpand(True)
        entity.set_margin_left(5)
        entity.set_margin_right(0)
        entity.set_margin_bottom(5)

        entity.add(self._tree)

        return entity

    def listen_select(self, name, callback):
        self._tree.connect(name, callback)

    def listen_search(self, name, callback):
        self._search.connect(name, callback, self._search)
