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
import glob
import wx
import imp
import logging
from modules import *
import modules as Modules
import inspect

class Kernel(object):
    _logger = None
    _container = None

    def __init__(self, options=None, args=None):

        logger = logging.getLogger('app')

        collection = []
        for source in glob.glob("app/config/*.yml"):
            if os.path.exists(source):
                logger.debug("config: %s" % source)
                collection.append(source)

        collection_modules = []
        for (name, module) in inspect.getmembers(Modules, inspect.ismodule):
            location = os.path.dirname(inspect.getfile(module))
            if hasattr(module, 'Loader'):
                logger.debug("module: %s" % name)
                identifier = getattr(module, 'Loader')
                with identifier(options) as plugin:
                    logger.debug("enabled: %s" % plugin.enabled)
                    if plugin.enabled is not None and plugin.enabled:
                        collection_modules.append(plugin)
                        if plugin.config is not None:
                            logger.debug("config: %s" % plugin.config)
                            collection.append("%s/%s" % (location, plugin.config))

        container = ioc.build(collection)
        for module in collection_modules:
            logger.debug("loaded: %s" % module)
            module.on_loaded(container)

        event_dispatcher = container.get('ioc.extra.event_dispatcher')
        event_dispatcher.dispatch('kernel_event.load', event_dispatcher.new_event())

        self._container = container

    @staticmethod
    def __module_loader(source):
        '''
        Load kernel modules using 
        given definitions
        
        '''
        return imp.load_source('Loader', source)

    def get(self, name):
        '''
        Get service from service container
        this is just a short notation
        from a classic event container method
        
        '''
        if self._container.has(name):
            return self._container.get(name)
        return None

