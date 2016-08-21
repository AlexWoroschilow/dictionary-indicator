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
from modules.clipboard.widget.clipboard import *


class KernelEventSubscriber(object):
    _container = None
    _clipboard = None
    _application = None

    @property
    def container(self):
        return self._container

    def set_container(self, container):
        self._container = container

    @property
    def subscribed_events(self):
        yield ('kernel_event.stop', ['on_stop', 0])
        yield ('kernel_event.toggle_scanning', ['on_toggle_scanning', 0])
        yield ('kernel_event.window_tab', ['on_notebook', 10])

    def on_notebook(self, event, dispatcher):
        if event.data is None:
            return None

        self._application = event.data
        self._clipboard = Clipboard(self._application, self.on_clipboard)

    def on_toggle_scanning(self, event, dispatcher):
        if self._clipboard is None:
            return None

        if event.data is not None and event.data:
            self._clipboard.start_scan(self.on_clipboard)
            return None

        self._clipboard.stop_scan()
        return None

    def on_clipboard(self, event):
        text = event.data
        if text is None or not len(text):
            return None

        dispatcher = self.container.get('ioc.extra.event_dispatcher')
        dispatcher.dispatch('clipboard_event.changed', dispatcher.new_event(text.strip()))

    def on_stop(self, event, dispatcher):
        if self._clipboard is None:
            return None

        self._clipboard.stop_scan()
