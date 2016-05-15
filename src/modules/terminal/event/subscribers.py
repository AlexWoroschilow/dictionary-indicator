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


class AppEventSubscriber(object):
    _container = None

    def __init__(self, container=None):
        self._container = container

    @property
    def subscribed_events(self):
        yield ('app.started', ('on_started'))

    def on_started(self, event, dispatcher):
        dictionary = self._container.get('dictionary')

        options = event.data['options']
        if options is None:
            return None

        word = options.word
        if word is not None:
            for translation in dictionary.translate(word):
                print(translation)