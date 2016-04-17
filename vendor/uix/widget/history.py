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

gi.require_version('Gdk', '3.0')
from gi.repository import Gdk

gi.require_version('WebKit', '3.0')
from gi.repository import WebKit


class TranslationHistoryFileChooser(Gtk.FileChooserDialog):
    def __init__(self, parent):
        Gtk.FileChooserDialog.__init__(self, "Please choose a file", parent,
                                       Gtk.FileChooserAction.SAVE,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_OPEN, Gtk.ResponseType.OK))


class TranslationHistoryToolbarWidget(Gtk.Toolbar):
    _parent = None

    def __init__(self, parent):
        self._parent = parent

        Gtk.Toolbar.__init__(self)

        self.set_style(Gtk.ToolbarStyle.TEXT)
        self.insert(self.widget_remove_selected, 0)
        self.insert(self.widget_remove_all, 1)
        self.insert(self.widget_export_csv, 2)
        self.insert(self.widget_save, 3)

    @property
    def widget_remove_selected(self):
        button = Gtk.ToolButton()
        button.set_label("Remove selected")
        button.connect("clicked", self._parent.on_button_remove_selected)
        return button

    @property
    def widget_remove_all(self):
        button = Gtk.ToolButton()
        button.set_label("Remove all")
        button.connect("clicked", self._parent.on_button_remove_all)
        return button

    @property
    def widget_export_csv(self):
        button = Gtk.ToolButton()
        button.set_label("Export as CSV")
        button.connect("clicked", self._parent.on_button_export_csv)
        return button

    @property
    def widget_save(self):
        button = Gtk.ToolButton()
        button.set_label("Save changes")
        button.connect("clicked", self._parent.on_button_save)
        return button


class TranslationHistoryTreeWidget(Gtk.ScrolledWindow):
    _tree = None
    _store = None
    _dispatcher = None

    def __init__(self, window=None, dispatcher=None):
        self._store = Gtk.ListStore(bool, str, str)
        Gtk.ScrolledWindow.__init__(self)
        self.add(self.widget_tree)

    @property
    def store(self):
        return self._store

    @store.setter
    def store(self, value):
        for line in reversed(value):
            fields = line.strip("\n").split(';')
            if len(fields) >= 2:
                self._store.append([0, fields[0].strip(), fields[1]])
        self._tree.set_model(self._store)

    @property
    def widget_tree(self):
        self._tree = Gtk.TreeView()
        self._tree.append_column(self.widget_tree_checkbox)
        self._tree.append_column(self.widget_tree_date)
        self._tree.append_column(self.widget_tree_word)
        return self._tree

    @property
    def widget_tree_checkbox(self):
        checkbox = Gtk.CellRendererToggle()
        checkbox.connect("toggled", self.on_cell_toggled)
        checkbox.set_padding(5, 5)
        return Gtk.TreeViewColumn("", checkbox, active=0)

    @property
    def widget_tree_date(self):
        data = Gtk.CellRendererText()
        data.set_property("editable", True)
        data.set_padding(5, 5)
        data.connect("edited", self.on_data_edited)
        return Gtk.TreeViewColumn("Data", data, text=1)

    @property
    def widget_tree_word(self):
        word = Gtk.CellRendererText()
        word.set_property("editable", True)
        word.connect("edited", self.on_word_edited)
        word.set_padding(5, 5)
        return Gtk.TreeViewColumn("Word", word, text=2)

    def on_cell_toggled(self, widget, path):
        self._store[path][0] = not self._store[path][0]

    def on_data_edited(self, widget, path, text):
        self._store[path][1] = text

    def on_word_edited(self, widget, path, text):
        self._store[path][2] = text


class HistoryLabelWidget(Gtk.Label):
    def __init__(self):
        Gtk.Label.__init__(self)
        self.set_margin_top(8)
        self.set_margin_bottom(8)
        self.set_justify(Gtk.Justification.RIGHT)


class HistoryToolbarTopWidget(Gtk.Grid):
    _label = None
    _parent = None

    def __init__(self, parent):
        self._parent = parent
        self._label = HistoryLabelWidget()

        Gtk.Grid.__init__(self)
        self.attach(self._button, 0, 0, 1, 1)
        self.attach(self._label, 1, 0, 4, 1)

    @property
    def label(self):
        self._label.get_label()

    @label.setter
    def label(self, value):
        self._label.set_label(value)

    @property
    def _button(self):
        button = Gtk.ToolButton()
        button.set_label("History file")
        button.connect("clicked", self._parent.on_history_file_choose)
        return button


class DictionaryHistoryAreaWidget(Gtk.VBox):
    _history = None
    _window = None
    _toolbar_top = None
    _toolbar_bottom = None

    def __init__(self, window, history):
        self._window = window
        self._history = history

        self._toolbar_top = HistoryToolbarTopWidget(self)
        self._toolbar_top.label = ": %s " % self.history

        self._content = TranslationHistoryTreeWidget(self)
        with open(self.history, 'r') as stream:
            self._content.store = stream.readlines()

        self._toolbar_bottom = TranslationHistoryToolbarWidget(self)

        Gtk.VBox.__init__(self, homogeneous=False, spacing=0)
        self.pack_start(self._toolbar_top, False, False, 0)
        self.pack_start(self._content, True, True, 0)
        self.pack_start(self._toolbar_bottom, False, True, 0)

    @property
    def history(self):
        return self._history.history

    def on_history_output(self, event, dispatcher):
        self._content.store.clear()
        with open(self.history, 'r') as stream:
            self._content.store = stream.readlines()
        self._toolbar_top.label = ": %s " % self.history

    def on_dictionary_clipboard(self, event, dispatcher):
        self._content.store.clear()
        with open(self.history, 'r') as stream:
            self._content.store = stream.readlines()

    def on_dictionary_translation(self, event, dispatcher):
        self._content.store.clear()
        with open(self.history, 'r') as stream:
            self._content.store = stream.readlines()

    def on_button_remove_selected(self, button):
        for row in self._content.store:
            if row[0] is not False:
                self._content.store.remove(row.iter)

    def on_button_remove_all(self, button):
        self._content.store.clear()

    def on_button_export_csv(self, button):
        dialog = TranslationHistoryFileChooser(self._window)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            with open(dialog.get_filename(), 'w') as stream:
                for row in self._content.store:
                    stream.write("%s;%s\n" % (row[1], row[2]))
        dialog.destroy()

    def on_button_save(self, button):
        with open(self.history, 'w') as stream:
            for row in reversed(self._content.store):
                stream.write("%s;%s\n" % (row[1], row[2]))

    def on_history_file_choose(self, button):
        dialog = TranslationHistoryFileChooser(self._window)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self._window.on_dictionary_history_changed(dialog.get_filename())
        dialog.destroy()
