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
from threading import Thread

from modules.dbus_service.server.dictionary import DictionaryServer

class KernelEventSubscriber(object):
    _thread = None
    _container = None

    @property
    def container(self):
        return self._container

    def set_container(self, container):
        self._container = container

    @property
    def subscribed_events(self):
        '''
        Get a list with all subscribed 
        events and theirs callbacks

        '''
        yield ('kernel_event.start', ['on_start', -128])

    def on_start(self, event, dispatcher):
        '''
        Application is ready here
        to accept notebok pages from modules
        all servicea are initialized

        '''
        dispatcher = self._container.get('ioc.extra.event_dispatcher')
        DictionaryServer(dispatcher).start()

