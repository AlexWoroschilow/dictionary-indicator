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
import string


class DictionaryHistory(object):
    _logger = None
    _logger_handler = None
    _logfile = None
    _dispatcher = None

    def __init__(self, logfile=None):
        self._logfile = logfile.replace('~', os.path.expanduser('~'))
        location = os.path.dirname(self._logfile)
        if not os.path.exists(location):
            os.makedirs(location, 0744)

        self._logger = Logger("history")
        self._logger.setLevel(INFO)
        self._logger.addHandler(self.handler)

    @property
    def handler(self):
        self._logger_handler = FileHandler(filename=self._logfile)
        self._logger_handler.setFormatter(Formatter('%(asctime)s;%(message)s', "%Y.%m.%d %H:%M:%S"))
        return self._logger_handler

    def add_history(self, value):
        self._logger.info(value)

    @property
    def history(self):
        with open(self._logfile, 'r') as stream:
            for line in reversed(stream.readlines()):
                fields = line.split(';')
                if len(fields) >= 2:
                    yield fields
        stream.close()

    @history.setter
    def history(self, collection):
        history = []
        for record in collection:
            history.append(string.join(record, ';'))
        with open(self._logfile, 'w+') as stream:
            stream.writelines(reversed(history))
            stream.close()
