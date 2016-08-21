# -*- coding: utf-8 -*-
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
from modules.translation.widget.notebook import *
import logging


class KernelEventSubscriber(object):
    _container = None
    _page = None

    @property
    def container(self):
        return self._container

    def set_container(self, container):
        self._container = container

    @property
    def subscribed_events(self):
        yield ('kernel_event.window_tab', ['on_window_tab', 0])
        yield ('clipboard_event.changed', ['on_clipboard_changed', 0])

    def on_window_tab(self, event, dispatcher):

        self._page = TranslationPage(event.data, self.on_search, self.on_suggestion, self.on_toggle_scaning)
        event.data.AddPage(self._page, "Translation")

        dictionary = self._container.get('dictionary')
        self._page.translations = dictionary.translate("welcome")
        self._page.suggestions = dictionary.suggestions("welcome")

    # Search event, fired if user
    # typped a word in search box and
    # pressed enter, or without enter
    def on_search(self, word=None):

        dictionary = self._container.get('dictionary')
        event_dispatcher = self._container.get('ioc.extra.event_dispatcher')
        if self._page is None:
            return None

        if len(word) and len(word) >= 3:
            suggestions = dictionary.suggestions(word)
            self._page.suggestions = suggestions

        if not len(word):
            return None

        translations = dictionary.translate(word)
        if translations is None:
            return None

        self._page.translations = translations

        event = event_dispatcher.new_event([word, translations])
        event_dispatcher.dispatch('dictionary.translation', event)

    # Suggestion event, fired of user
    # found a similar word in left side panel
    # and clicked on it
    def on_suggestion(self, word=None):
        dictionary = self._container.get('dictionary')
        event_dispatcher = self._container.get('ioc.extra.event_dispatcher')
        if self._page is None:
            return None

        translations = dictionary.translate(word)
        if translations is None:
            return None

        self._page.translations = translations

        event = event_dispatcher.new_event([word, translations])
        event_dispatcher.dispatch('dictionary.translation', event)

    # Enable or disable clipboard scanning
    def on_toggle_scaning(self, scan=False):
        event_dispatcher = self._container.get('ioc.extra.event_dispatcher')
        event = event_dispatcher.new_event(scan)
        event_dispatcher.dispatch('kernel_event.toggle_scanning', event)


    # Catch clipboard event (clipboard text has been changed)
    # and display popup with a translation, if it has been found
    def on_clipboard_changed(self, event, dispatcher):
        self._page.word = event.data
