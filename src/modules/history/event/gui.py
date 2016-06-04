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
from src.modules.history.widget.notebook import *
import logging
import threading
import wx


class GuiEventSubscriber(object):
    _container = None
    _logger = None

    def __init__(self, container=None):
        self._logger = logging.getLogger('window_gtk')
        self._container = container

    @property
    def subscribed_events(self):
        yield ('gui_event.notebook', ['on_notebook', 1])
        yield ('gui_event.notebook_changed', ['on_notebook_changed', 1])

    # Append custom page to common notebook
    def on_notebook(self, event, dispatcher):
        event.data.AddPage(HistoryPage(event.data), "History")

    # Perform some actions if notebook
    # have been changed somehow
    def on_notebook_changed(self, event, dispatcher):
        service_history = self._container.get('history')

        (previous, current) = event.data
        if current.__class__.__name__.find('HistoryPage') != -1:
            current.history = service_history.history
            return None

        if previous.__class__.__name__.find('HistoryPage') != -1:
            service_history.history = previous.history
            return None
