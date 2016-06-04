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
from src.modules import *
import src.modules as Modules
import inspect


class WxGuiKernel(wx.App):
    _logger = None
    _container = None

    def __init__(self, options=None, args=None):
        wx.App.__init__(self)

        self._logger = logging.getLogger('app')

        collection = []
        for source in glob.glob("app/config/*.yml"):
            if os.path.exists(source):
                self._logger.debug("config: %s" % source)
                collection.append(source)

        collection_modules = []
        for (name, module) in inspect.getmembers(Modules, inspect.ismodule):
            location = os.path.dirname(inspect.getfile(module))
            if hasattr(module, 'Loader'):
                self._logger.debug("module: %s" % name)
                identifier = getattr(module, 'Loader')
                with identifier(options) as plugin:
                    self._logger.debug("enabled: %s" % plugin.enabled)
                    if plugin.enabled is not None and plugin.enabled:
                        collection_modules.append(plugin)
                        if plugin.config is not None:
                            self._logger.debug("config: %s" % plugin.config)
                            collection.append("%s/%s" % (location, plugin.config))

        container = ioc.build(collection)
        for module in collection_modules:
            self._logger.debug("loaded: %s" % module)
            module.on_loaded(container)

        event_dispatcher = container.get('event_dispatcher')
        event_dispatcher.dispatch('kernel_event.load', event_dispatcher.new_event())

        self._container = container

    # Get service from service container
    # this is just a short notation
    # from a classic event container method
    def get(self, name):
        if self._container.has(name):
            return self._container.get(name)
        return None

    @staticmethod
    def __module_loader(source):
        return imp.load_source('Loader', source)

    def run(self, options=None, args=None):
        dispatcher = self.get('event_dispatcher')

        event = dispatcher.new_event(options)
        dispatcher.dispatch('kernel_event.start', event)
        self.MainLoop()


class WxWindowKernel(WxGuiKernel):
    _notebook = None

    def __init__(self, options=None, args=None):
        WxGuiKernel.__init__(self, options, args)

    def run(self, options=None, args=None):
        dispatcher = self.get('event_dispatcher')

        event = dispatcher.new_event(options)
        dispatcher.dispatch('kernel_event.start', event)

        window = wx.Frame(None)
        window.SetSize((600, 600))
        window.SetMinSize((600, 600))

        panel = wx.Panel(window)
        self._notebook = wx.Notebook(panel)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.on_page_changed, self._notebook)

        event = dispatcher.new_event(self._notebook)
        dispatcher.dispatch('gui_event.notebook', event)

        sizer = wx.BoxSizer()
        panel.SetSizer(sizer)
        sizer.Add(self._notebook, 1, wx.EXPAND)
        window.Show()

        self.MainLoop()

    def on_page_changed(self, event):
        dispatcher = self.get('event_dispatcher')

        previous = self._notebook.GetPage(event.GetOldSelection())
        current = self._notebook.GetPage(event.GetSelection())

        event = dispatcher.new_event((previous, current))
        dispatcher.dispatch('gui_event.notebook_changed', event)

