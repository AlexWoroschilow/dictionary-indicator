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


class HistoryEventSubscriber(object):
    _container = None

    def __init__(self, container=None):
        self._container = container

    @property
    def subscribed_events(self):
        yield ('dictionary.translation', ('on_dictionary_translation'))

    def on_dictionary_translation(self, event, dispatcher):
        word, translation = event.data
        history = self._container.get('history')
        history.add_history(word)
