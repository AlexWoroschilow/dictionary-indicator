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
from src.modules.statistic.widget.notebook import *
import logging


class GuiEventSubscriber(object):
    _container = None
    _logger = None

    def __init__(self, container=None):
        self._logger = logging.getLogger('statistic')
        self._container = container

    @property
    def subscribed_events(self):
        yield ('gui_event.notebook', ['on_notebook', 2])

    def on_notebook(self, event, dispatcher):
        statistic = StatisticPage(event.data)
        event.data.AddPage(statistic, "Statistic")
