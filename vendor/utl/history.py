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
from logging import *
from logging.handlers import RotatingFileHandler


class DictionaryHistory(object):
    _logger = None
    _logger_handler = None
    _logfile = None
    _dispatcher = None

    def __init__(self, logfile=None, dispatcher=None):

        self.logfile = logfile
        logfile_dir = os.path.dirname(self.logfile)
        if not os.path.exists(logfile_dir):
            os.makedirs(logfile_dir, 0744)

        self._dispatcher = dispatcher
        self._dispatcher.add_listener('dictionary.clipboard', self.on_clipboard_text, 1)
        self._dispatcher.add_listener('dictionary.translation', self.on_dictionary_translation, 1)
        self._dispatcher.add_listener('dictionary.history_output_changed', self.on_history_output_changed, 1)

        self._logger = Logger("history")
        self._logger.setLevel(INFO)
        self._logger.addHandler(self.handler)

    @property
    def logfile(self):
        return self._logfile

    @logfile.setter
    def logfile(self, value):
        self._logfile = value.replace('~', os.path.expanduser('~'))

    @property
    def handler(self):
        self._logger_handler = FileHandler(filename=self.logfile)
        self._logger_handler.setFormatter(Formatter('%(asctime)s;%(message)s'))
        return self._logger_handler

    @property
    def history(self):
        return self._logfile

    def on_history_output_changed(self, event, dispatcher):
        if event.data is None:
            return None
        self.logfile = event.data
        if self._logger_handler is not None:
            self._logger.removeHandler(self._logger_handler)

        self._logger.addHandler(self.handler)

        event = self._dispatcher.new_event(self.logfile)
        self._dispatcher.dispatch('dictionary.history_output', event)

    def on_clipboard_text(self, event, dispatcher):
        word = event.data
        if word is None:
            return None
        if not len(word):
            return None
        self._logger.info(event.data)

    def on_dictionary_translation(self, event, dispatcher):
        translation = event.data
        if translation is not None and len(translation):
            event.data = translation.word
            self.on_clipboard_text(event, dispatcher)
