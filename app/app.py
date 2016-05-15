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
import os
import ioc
import sys
import glob
import imp
import logging


class App(object):
    _logger = None
    _container = None

    def __init__(self, options=None, args=None):
        self._logger = logging.getLogger('app')

        collection = []
        for source in glob.glob("app/config/*.yml"):
            if os.path.exists(source):
                self._logger.debug("config: %s" % source)
                collection.append(source)

        collection_modules = []
        for source in glob.glob("src/modules/*"):
            if os.path.exists(source):
                sys.path.append(source)

                loader = self.__module_loader(source)

                if loader is not None:
                    self._logger.debug("module: %s" % source)
                    with loader.Loader(source, options) as module:
                        self._logger.debug("enabled: %s" % module.enabled)
                        if module.enabled is not None and module.enabled:
                            self._logger.debug("config: %s" % module.config)
                            collection.append(module.config)
                            collection_modules.append(module)

        container = ioc.build(collection)
        for module in collection_modules:
            self._logger.debug("loaded: %s" % module)
            module.on_loaded(container)

        if container.has('event_dispatcher'):
            event_dispatcher = container.get('event_dispatcher')
            event_dispatcher.dispatch('app.loaded', event_dispatcher.new_event())

        self._container = container

    def run(self, options=None, args=None):
        if self._container.has('event_dispatcher'):
            event_dispatcher = self._container.get('event_dispatcher')
            data = {'options':options, 'args':args}
            event_dispatcher.dispatch('app.started', event_dispatcher.new_event(data))

    @staticmethod
    def __module_loader(source):
        (file, filename, data) = imp.find_module('module', [source])
        return imp.load_module('Loader', file, filename, data)
