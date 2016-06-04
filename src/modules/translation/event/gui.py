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
from src.modules.translation.widget.notebook import *
import logging


class GuiEventSubscriber(object):
    _container = None
    _page = None

    def __init__(self, container=None):
        self._container = container

    @property
    def subscribed_events(self):
        yield ('gui_event.notebook', ['on_notebook', 0])
        yield ('dict_event.clipboard', ['on_clipboard', 0])

    def on_notebook(self, event, dispatcher):

        self._page = TranslationPage(event.data, self.on_search, self.on_suggestion)
        event.data.AddPage(self._page, "Translation")

        dictionary = self._container.get('dictionary')
        self._page.translations = dictionary.translate("welcome")
        self._page.suggestions = dictionary.suggestions("welcome")

    # Search event, fired if user
    # typped a word in search box and
    # pressed enter, or without enter
    def on_search(self, word=None):

        dictionary = self._container.get('dictionary')
        event_dispatcher = self._container.get('event_dispatcher')
        if self._page is None:
            return None

        translations = dictionary.translate(word)
        self._page.translations = translations

        suggestions = dictionary.suggestions(word)
        self._page.suggestions = suggestions

        if not len(word) or not len(translations):
            return None

        event = event_dispatcher.new_event([word, translations])
        event_dispatcher.dispatch('dictionary.translation', event)

    # Suggestion event, fired of user
    # found a similar word in left side panel
    # and clicked on it
    def on_suggestion(self, word=None):
        dictionary = self._container.get('dictionary')
        event_dispatcher = self._container.get('event_dispatcher')
        if self._page is None:
            return None

        translations = dictionary.translate(word)
        self._page.translations = translations

        if translations is None or not len(translations):
            return None

        event = event_dispatcher.new_event([word, translations])
        event_dispatcher.dispatch('dictionary.translation', event)

    def on_clipboard(self, event, dispatcher):
        """
        Show translation from clipboard
        if main window presented and clipboard
        is not empty
        """
        dictionary = self._container.get('dictionary')
        if self._page is None:
            return None

        self._page.word = event.data
        self._page.translations = dictionary.translate(event.data)
