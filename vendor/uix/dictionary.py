import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

gi.require_version('WebKit', '3.0')
from gi.repository import WebKit


class TranslationHistoryFileChooser(Gtk.FileChooserDialog):
    def __init__(self, parent):
        Gtk.FileChooserDialog.__init__(self, "Please choose a file", parent,
                                       Gtk.FileChooserAction.SAVE,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_OPEN, Gtk.ResponseType.OK))


class TranslationHistoryToolbarWidget(Gtk.Toolbar):
    _window = None

    def __init__(self, window):
        Gtk.Toolbar.__init__(self)
        self._window = window

        self.set_style(Gtk.ToolbarStyle.TEXT)
        self.insert(self.widget_remove_selected, 0)
        self.insert(self.widget_remove_all, 1)
        self.insert(self.widget_export_csv, 2)
        self.insert(self.widget_save, 3)

    @property
    def widget_remove_selected(self):
        button = Gtk.ToolButton()
        button.set_label("Remove selected")
        button.connect("clicked", self.on_remove_selected)
        return button

    @property
    def widget_remove_all(self):
        button = Gtk.ToolButton()
        button.set_label("Remove all")
        button.connect("clicked", self.on_remove_all)
        return button

    @property
    def widget_export_csv(self):
        button = Gtk.ToolButton()
        button.set_label("Export as CSV")
        button.connect("clicked", self.on_export_csv)
        return button

    @property
    def widget_save(self):
        button = Gtk.ToolButton()
        button.set_label("Save changes")
        button.connect("clicked", self.on_save)
        return button

    def on_remove_selected(self, button):
        for row in self._window.store:
            if row[0] is not False:
                self._window.store.remove(row.iter)

    def on_remove_all(self, button):
        self._window.store.clear()

    def on_export_csv(self, button):
        dialog = TranslationHistoryFileChooser(self._window)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            with open(dialog.get_filename(), 'w') as stream:
                for row in self._window.store:
                    stream.write("%s;%s\n" % (row[1], row[2]))
        dialog.destroy()

    def on_save(self, button):
        with open(self._window.history, 'w') as stream:
            for row in reversed(self._window.store):
                stream.write("%s;%s\n" % (row[1], row[2]))


class TranslationHistoryTreeWidget(Gtk.ScrolledWindow):
    _tree = None
    _store = None

    def __init__(self, window=None):
        self._store = Gtk.ListStore(bool, str, str)
        Gtk.ScrolledWindow.__init__(self)
        # self.set_hexpand(True)
        # self.set_vexpand(True)
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


class DictionaryHistoryAreaWidget(Gtk.VBox):
    _history = None
    _dispatcher = None

    def __init__(self, window, dispatcher, history):
        self._history = history
        self._dispatcher = dispatcher
        self._dispatcher.add_listener('dictionary.translation', self.on_dictionary_translation, 100)
        self._dispatcher.add_listener('clipboard_text', self.on_dictionary_translation, 100)

        self._tree = TranslationHistoryTreeWidget(self)
        with open(self._history.history, 'r') as stream:
            self._tree.store = stream.readlines()

        self._toolbar = TranslationHistoryToolbarWidget(self)

        Gtk.VBox.__init__(self, homogeneous=False, spacing=0)
        self.pack_start(self.widget_label, False, False, 0)
        self.pack_start(self._tree, True, True, 0)
        self.pack_start(self._toolbar, False, True, 0)

    def on_dictionary_translation(self, event, dispatcher):
        self._tree.store.clear()
        with open(self._history.history, 'r') as stream:
            self._tree.store = stream.readlines()
        self._label.set_markup('<big>%s records in history</big>' % len(self._tree.store))

    @property
    def widget_label(self):
        self._label = Gtk.Label()
        self._label.set_markup('<big>%s records in history</big>' % len(self._tree.store))
        self._label.set_margin_top(8)
        self._label.set_margin_bottom(8)
        self._label.set_justify(Gtk.Justification.LEFT)
        return self._label

    @property
    def store(self):
        return self._tree.store

    @property
    def history(self):
        return self._history.history


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

        entity.add(self.widget_webview)
        return entity

    @property
    def widget_webview(self):
        self._webview = WebKit.WebView()
        return self._webview

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
        with open(self._template) as template:
            self._webview.load_html_string(template.read() % value, 'text/html')


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


class DictionaryWindow(Gtk.Window):
    _search = None
    _history = None
    _dictionary = None
    _dispatcher = None
    _translation = None

    def __init__(self, dispatcher, dictionary, history, template):
        self._search = DictionarySuggestionAreaWidget()
        self._search.listen_search("changed", self.on_search)
        self._search.listen_search("activate", self.on_search_finished)
        self._search.listen_select("row-activated", self.on_select)

        self._tree = DictionaryHistoryAreaWidget(self, dispatcher, history)
        self._translation = DictionaryTranslationAreaWidget(template)

        self._history = history
        self._dictionary = dictionary
        self._dispatcher = dispatcher
        Gtk.Window.__init__(self, title="Translation history")
        self.set_size_request(1100, 700)
        self.set_position(Gtk.WindowPosition.MOUSE)



        grid = Gtk.Grid()
        grid.attach(self._search, 0, 0, 1, 1)
        grid.attach(self._translation, 1, 0, 6, 1)
        grid.attach(self._tree, 7, 0, 6, 1)

        self.add(grid)

        self.translate(str(self._dictionary.word))

    def on_search(self, widget, entry):
        self.translate(entry.get_text())

    def on_search_finished(self, widget, entry):
        self.translate_suggestion(entry.get_text())

    def on_select(self, tree, path, row):
        store = tree.get_model()
        if store is not None and len(store):
            self.translate_suggestion(store[path][0])

    def translate(self, word):
        """
        Fetch character sequence from text field
        try to translate it and try to find
        suggestions - a similar words with
        a partial match of search string.
        There could be a lot of different words,
        i can not be sure if we need to store
        all this things to history
        :param word:
        """
        if word is not None and len(word):
            translation = self._dictionary.get(word)
            if translation is not None and len(translation):
                self._translation.label = word
                self._translation.content = self._dictionary.get(word)
        self._search.suggestions = self._dictionary.matches(word)

    def translate_suggestion(self, word):
        """
        Normally we should have a complete
        word here, from suggestions list
        or if user has pressed Enter,
        in this case user is sure to store
        this word in history
        :param word:
        """
        if word is not None and len(word):
            translation = self._dictionary.get(word)
            if translation is not None and len(translation):
                self._translation.label = word
                self._translation.content = translation
                event = self._dispatcher.new_event(translation)
                self._dispatcher.dispatch('dictionary.translation', event)


class TranslationDictionary(object):
    _history = None
    _template = None
    _dictionary = None
    _dispatcher = None

    def __init__(self, dispatcher, dictionary, history, template):
        self._history = history
        self._template = template
        self._dictionary = dictionary
        self._dispatcher = dispatcher

        self._dispatcher.add_listener('dictionary_window', self.on_dictionary_window)

    def on_dictionary_window(self, event, dispatcher):
        self._window = DictionaryWindow(self._dispatcher, self._dictionary, self._history, self._template)
        self._window.connect("delete-event", Gtk.main_quit)
        self._window.show_all()
        Gtk.main()
