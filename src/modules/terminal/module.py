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
from event.subscribers import *


class Loader(object):
    _options = None
    _location = None
    _container = None

    def __init__(self, source, options=None):
        self._options = options
        self._location = source

    @property
    def config(self):
        return '%s/config/services.xml' \
               % self._location

    @property
    def enabled(self):
        if self._options is not None:
            return not self._options.gui
        return False

    def on_loaded(self, container):
        self._container = container
        if not self._container.has('event_dispatcher'):
            return None

        event_dispatcher = self._container.get('event_dispatcher')
        event_dispatcher.add_subscriber(AppEventSubscriber(self._container))

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass