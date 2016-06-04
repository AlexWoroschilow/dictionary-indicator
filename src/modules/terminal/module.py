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
from src.modules.terminal.event.app import *


class Loader(object):
    _options = None
    _container = None

    def __init__(self, options=None):
        self._options = options

    @property
    def config(self):
        return None

    @property
    def enabled(self):
        return True

    def on_loaded(self, container):
        if container.has('event_dispatcher'):
            event_dispatcher = container.get('event_dispatcher')
            event_dispatcher.add_subscriber(TerminalEventSubscriber(container))
        self._container = container

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass