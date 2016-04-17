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
import threading

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

gi.require_version('Gdk', '3.0')
from gi.repository import Gdk

gi.require_version('WebKit', '3.0')
from gi.repository import WebKit

from widget.history import *
from widget.translation import *


class DictionaryWindow(Gtk.Window):
    _widget_search = None
    _history = None
    _dictionary = None
    _parent = None
    _translation = None
    _thread = None

    def __init__(self, parent, dictionary, history, template, icon):
        self._history = history
        self._dictionary = dictionary
        self._parent = parent

        self._widget_search = DictionarySuggestionAreaWidget()
        self._widget_search.listen_search("changed", self.on_translation_search)
        self._widget_search.listen_search("activate", self.on_translation_search_finished)
        self._widget_search.listen_select("row-activated", self.on_suggestion_select)

        self._widget_history = DictionaryHistoryAreaWidget(self, history)
        self._widget_translation = DictionaryTranslationAreaWidget(template)

        Gtk.Window.__init__(self, title="Translation history")
        self.connect("event", self.on_dictionary_event)
        self.connect("set-focus", self.on_dictionary_focus_changed)
        self.set_icon_from_file(icon)

        self.set_size_request(1100, 700)
        self.set_position(Gtk.WindowPosition.MOUSE)

        grid = Gtk.Grid()
        grid.attach(self._widget_search, 0, 0, 1, 1)
        grid.attach(self._widget_translation, 1, 0, 6, 1)
        grid.attach(self._widget_history, 7, 0, 6, 1)

        self.add(grid)

        self.translate(str(self._dictionary.word))

    def on_dictionary_event(self, window, event):
        if event.type in [Gdk.EventType.DELETE]:
            self.on_clipboard_scanning_activate(None)

    def on_dictionary_focus_changed(self, window, widget):
        if widget.__class__.__name__ in ['Entry']:
            self.on_clipboard_scanning_deactivate(None)
            return None
        self.on_clipboard_scanning_activate(None)
        return None

    def on_translation_search(self, widget, entry):
        self.translate(entry.get_text())

    def on_translation_search_finished(self, widget, entry):
        self.translate_suggestion(entry.get_text())

    def on_suggestion_select(self, tree, path, row):
        store = tree.get_model()
        if store is not None and len(store):
            self.translate_suggestion(store[path][0])

    def on_clipboard_scanning_activate(self, item=None):
        self._parent.on_clipboard_scanning_activate(item)

    def on_clipboard_scanning_deactivate(self, item=None):
        self._parent.on_clipboard_scanning_deactivate(item)

    def on_dictionary_history_changed(self, item=None):
        self._parent.on_dictionary_history_changed(item)

    def on_dictionary_clipboard(self, event, dispatcher):
        self._widget_history.on_dictionary_clipboard(event, dispatcher)

    def on_dictionary_translation(self, event, dispatcher):
        self._widget_history.on_dictionary_translation(event, dispatcher)

    def on_history_output(self, event, dispatcher):
        self._widget_history.on_history_output(event, dispatcher)

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
            if self._thread is not None:
                self._thread.join()

            translation = self._dictionary.get(word)
            if translation is not None and len(translation):
                self._widget_translation.label = word
                self._widget_translation.content = self._dictionary.get(word)

        def target():
            self._widget_search.suggestions = self._dictionary.matches(word)

        self._thread = threading.Thread(target=target)
        self._thread.start()
        self._thread.join(1)

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
                self._widget_translation.label = word
                self._widget_translation.content = translation
                self._parent.on_dictionary_translation(translation)


class TranslationDictionary(object):
    _history = None
    _template = None
    _dictionary = None
    _dispatcher = None
    _window = None
    _icon = None

    def __init__(self, dispatcher, dictionary, history, template, icon):
        self._history = history
        self._template = template
        self._dictionary = dictionary
        self._dispatcher = dispatcher
        self._icon = icon

        self._dispatcher.add_listener('dictionary_window', self.on_dictionary_window)

    def on_dictionary_window(self, event, dispatcher):
        self._window = DictionaryWindow(self, self._dictionary, self._history, self._template, self._icon)

        self._dispatcher.add_listener('dictionary.clipboard', self._window.on_dictionary_clipboard, 100)
        self._dispatcher.add_listener('dictionary.translation', self._window.on_dictionary_translation, 100)
        self._dispatcher.add_listener('dictionary.history_output', self._window.on_history_output, 100)

        self._window.connect("delete-event", self.on_dictionary_window_closed)
        self._window.show_all()
        Gtk.main()

    def on_dictionary_window_closed(self, window=None, widget=None):
        self._dispatcher.remove_listener('dictionary.clipboard', self._window.on_dictionary_clipboard)
        self._dispatcher.remove_listener('dictionary.translation', self._window.on_dictionary_translation)
        self._dispatcher.remove_listener('dictionary.history_output', self._window.on_history_output)

        Gtk.main_quit()

    def on_dictionary_history_changed(self, item=None):
        event = self._dispatcher.new_event(item)
        self._dispatcher.dispatch('dictionary.history_output_changed', event)

    def on_dictionary_translation(self, item=None):
        event = self._dispatcher.new_event(item)
        self._dispatcher.dispatch('dictionary.translation', event)

    def on_clipboard_scanning_activate(self, item=None):
        event = self._dispatcher.new_event()
        self._dispatcher.dispatch('dictionary.clipboard_scanning_activate', event)

    def on_clipboard_scanning_deactivate(self, item=None):
        event = self._dispatcher.new_event()
        self._dispatcher.dispatch('dictionary.clipboard_scanning_deactivate', event)
