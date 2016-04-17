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


class DictionaryLogger(object):
    def __init__(self, logfile=None, dispatcher=None, files=3):

        logfile = logfile.replace('~', os.path.expanduser('~'))
        logfile_dir = os.path.dirname(logfile)
        if not os.path.exists(logfile_dir):
            os.makedirs(logfile_dir, 0744)


        dispatcher.add_listener('dictionary.clipboard', self.on_clipboard_text)
        dispatcher.add_listener('dictionary_found', self.on_dictionary_found)
        dispatcher.add_listener('dictionary_enabled', self.on_dictionary_enabled)
        dispatcher.add_listener('dictionary_disabled', self.on_dictionary_disabled)
        dispatcher.add_listener('translation_found', self.on_translation_found)

        handler = RotatingFileHandler(filename=logfile, maxBytes=(1024 * 100), backupCount=int(files))
        handler.setFormatter(Formatter('%(levelname)s;%(asctime)s;%(message)s'))

        self.__logger = Logger("dictionary")
        self.__logger.setLevel(DEBUG)
        self.__logger.addHandler(handler)

    def on_clipboard_text(self, event, dispatcher):
        pass

    def on_dictionary_found(self, event, dispatcher):
        pass

    def on_dictionary_enabled(self, event, dispatcher):
        pass

    def on_dictionary_disabled(self, event, dispatcher):
        pass

    def on_translation_found(self, event, dispatcher):
        pass
