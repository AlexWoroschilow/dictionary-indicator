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
from modules.dictionary.widget.notebook import *


class KernelEventSubscriber(object):
    _container = None

    @property
    def container(self):
        return self._container

    def set_container(self, container):
        self._container = container

    @property
    def subscribed_events(self):
        yield ('kernel_event.window_tab', ['on_window_tab', 4])

    def on_window_tab(self, event, dispatcher):
        dictionary = self.container.get('dictionary')

        page = DictionaryPage(event.data)
        page.dictionaries = dictionary.dictionaries

        event.data.AddPage(page, "Dictionaries")
