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
import sys
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

gi.require_version('AppIndicator3', '0.1')
from gi.repository.AppIndicator3 import Indicator
from gi.repository.AppIndicator3 import IndicatorCategory
from gi.repository.AppIndicator3 import IndicatorStatus


class TranslationIndicator(object):
    def __init__(self, config, dispatcher):
        self._history = []
        self._config = config
        self._dispatcher = dispatcher

        self._dispatcher.add_listener('dictionary_found', self.on_dictionary_found)
        self._dispatcher.add_listener('dictionary_enabled', self.on_dictionary_enabled)
        self._dispatcher.add_listener('dictionary_disabled', self.on_dictionary_disabled)

        self.__indicator = Indicator.new(
                "Indicator Popup Dictionary",
                "/usr/share/power-manager/share/icons/1x50px.png",
                IndicatorCategory.SYSTEM_SERVICES
        )
        self.__indicator.set_status(IndicatorStatus.ACTIVE)
        self.__indicator.set_label(u"\U0001F4CE", "Indicator Popup Dictionary")
        self.__indicator.set_menu(self.menu)

    @property
    def disabled(self):
        if self._config is not None:
            return self._config.disabled
        return []

    @property
    def available(self):
        if self._config is not None:
            return self._config.available
        return []

    @property
    def menu(self):
        menu = Gtk.Menu()
        menu.append(self._menu_dictionary_window)
        menu.append(self._menu_scaning)
        menu.append(self._menu_separator)
        for name in self.available:
            menu.append(self._menu_dictionary(name))
        menu.append(self._menu_separator)
        menu.append(self._menu_shutdown)
        return menu

    @property
    def _menu_scaning(self):
        entity = Gtk.CheckMenuItem('Scan clipboard')
        entity.connect("activate", self.on_clipboard_scan)
        entity.set_active(True)
        entity.show()
        return entity

    @property
    def _menu_dictionary_window(self):
        history = Gtk.MenuItem('Show main window')
        history.connect("activate", self.on_dictionary_window)
        history.show()
        return history

    @property
    def _menu_shutdown(self):
        element = Gtk.MenuItem('Exit')
        element.connect("activate", self.on_shutdown)
        element.show()
        return element

    @property
    def _menu_separator(self):
        element = Gtk.SeparatorMenuItem()
        element.show()
        return element

    def _menu_dictionary(self, name):
        element = Gtk.CheckMenuItem(name)
        element.set_active(False if self.is_disabled(name) else True)
        element.connect("activate", self.on_dictionary_toggle)
        element.show()
        return element

    def on_clipboard_scan(self, item=None):
        if item.get_active():
            event = self._dispatcher.new_event()
            self._dispatcher.dispatch('dictionary.clipboard_scanning_enable', event)
            return True
        event = self._dispatcher.new_event()
        self._dispatcher.dispatch('dictionary.clipboard_scanning_disable', event)
        return True

    def on_dictionary_found(self, event, dispatcher):
        self.__indicator.set_menu(self.menu)

    def on_dictionary_enabled(self, event, dispatcher):
        self.__indicator.set_menu(self.menu)

    def on_dictionary_disabled(self, event, dispatcher):
        self.__indicator.set_menu(self.menu)

    def is_disabled(self, name=None):
        return name in self.disabled

    def on_dictionary_toggle(self, item=None):
        name = item.get_label()
        if self.is_disabled(name):
            event = self._dispatcher.new_event(name)
            self._dispatcher.dispatch('dictionary_enabled', event)
            return None

        event = self._dispatcher.new_event(name)
        self._dispatcher.dispatch('dictionary_disabled', event)
        return None

    def on_history(self, item=None):
        event = self._dispatcher.new_event()
        self._dispatcher.dispatch('dictionary_history', event)

    def on_dictionary_window(self, item=None):
        event = self._dispatcher.new_event()
        self._dispatcher.dispatch('dictionary_window', event)

    def on_shutdown(self, item=None):
        sys.exit(0)
