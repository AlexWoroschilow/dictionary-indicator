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
import gi
import re

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk


class TranslationClipboard(object):
    _active = True
    _enabled = True

    def __init__(self, config, dispatcher):
        self._dispatcher = dispatcher
        self._dispatcher.add_listener('dictionary.clipboard_scanning_enable', self.on_scanning_enable)
        self._dispatcher.add_listener('dictionary.clipboard_scanning_disable', self.on_scanning_disable)
        self._dispatcher.add_listener('dictionary.clipboard_scanning_activate', self.on_scanning_activate)
        self._dispatcher.add_listener('dictionary.clipboard_scanning_deactivate', self.on_scanning_deactivate)

        self._clipboard = Gtk.Clipboard.get(Gdk.SELECTION_PRIMARY)
        self._clipboard.connect("owner-change", self.on_clipboard_change)

    def _normalize(self, word):
        return word.strip(" \n\t-_;:,.")

    def on_scanning_enable(self, event, dispatcher):
        self._enabled = True

    def on_scanning_disable(self, event, dispatcher):
        self._enabled = False

    def on_scanning_activate(self, event, dispatcher):
        self._active = True

    def on_scanning_deactivate(self, event, dispatcher):
        self._active = False

    def on_clipboard_change(self, clipboard, event):
        if not self._enabled:
            return True

        if not self._active:
            return True

        text = clipboard.wait_for_text()
        if text is None or len(text) > 32:
            return None
        event = self._dispatcher.new_event(self._normalize(text.lower()))
        self._dispatcher.dispatch('dictionary.clipboard', event)
        return True
