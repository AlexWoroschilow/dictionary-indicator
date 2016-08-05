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
from modules.popup.widget.popup import *


class PopupEventSubscriber(object):
    _container = None
    _dictionary = None
    _window = None

    def __init__(self, container=None):

        self._window = TranslationPopup()
        self._window.Hide()

    @property
    def container(self):
        return self._container

    def set_container(self, container):
        self._container = container

    @property
    def subscribed_events(self):
        yield ('clipboard_event.changed', ['on_clipboard', 128])

    # Catch clipboard event (clipboard text has been changed)
    # and display popup with a translation, if it has been found
    def on_clipboard(self, event, dispatcher):

        clipboard = self._text_clean(event.data)
        if clipboard is None or not len(clipboard):
            return None

        self._dictionary = self.container.get('dictionary')
        translation = self._dictionary.translate_one(clipboard)
        if translation is None:
            return None

        self._window.Hide()
        self._window.SetPosition(wx.GetMousePosition())
        self._window.translations = translation
        self._window.Show()

    # Remove special characters, empty spaces
    # and check for maximal word Limit to translate Tree
    @staticmethod
    def _text_clean(text):
        if len(text) > 32:
            return None
        return ''.join(e for e in text if e.isalnum())
