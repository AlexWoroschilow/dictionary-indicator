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
    def __init__(self, logfile=None, dispatcher=None):

        self._logfile = logfile.replace('~', os.path.expanduser('~'))
        logfile_dir = os.path.dirname(self._logfile)
        if not os.path.exists(logfile_dir):
            os.makedirs(logfile_dir, 0744)

        dispatcher.add_listener('clipboard_text', self.on_clipboard_text, 1)
        dispatcher.add_listener('dictionary.translation', self.on_dictionary_translation, 1)

        handler = FileHandler(filename=self._logfile)
        handler.setFormatter(Formatter('%(asctime)s;%(message)s'))

        self.__logger = Logger("history")
        self.__logger.setLevel(INFO)
        self.__logger.addHandler(handler)

    @property
    def history(self):
        return self._logfile

    def on_clipboard_text(self, event, dispatcher):
        word = event.data
        if word is None:
            return None
        if not len(word):
            return None
        self.__logger.info(event.data)

    def on_dictionary_translation(self, event, dispatcher):
        translation = event.data
        if translation is not None and len(translation):
            event.data = translation.word
            self.on_clipboard_text(event, dispatcher)
