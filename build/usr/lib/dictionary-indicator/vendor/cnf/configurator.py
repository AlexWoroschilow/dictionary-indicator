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
import string
from configparser import ConfigParser
from os.path import expanduser
from os.path import dirname



class DictionaryConfigParser(ConfigParser):
    @staticmethod
    def __normalize(string):
        return string.strip('\'')

    @staticmethod
    def __denormalize(string):
        return "'%s'" % string

    @property
    def available(self):
        collection_raw = self.get('general', 'available')
        collection = collection_raw.strip(' \t\n\r,')
        if collection.find(',') is not -1:
            return map(self.__normalize, collection.split(','))
        return [self.__normalize(collection)] if len(collection) else []

    @available.setter
    def available(self, value):
        collection = map(self.__denormalize, value)
        available_string = string.join(collection, ',')
        self.set('general', 'available', available_string.strip(' \t\n\r,'))

    @property
    def disabled(self):
        collection_raw = self.get('general', 'disabled')
        collection = collection_raw.strip(' \t\n\r,')
        if collection.find(',') is not -1:
            return map(self.__normalize, collection.split(','))
        return [self.__normalize(collection)] if len(collection) else []

    @disabled.setter
    def disabled(self, value):
        collection = map(self.__denormalize, value)
        blacklist_string = string.join(collection, ',')
        self.set('general', 'disabled', blacklist_string.strip(' \t\n\r,'))

    def flush(self, path):
        with open(path, 'w') as stream:
            self.write(stream)


class DictionaryConfig(object):
    def __init__(self, config=None, dispatcher=None):
        self._config = config.replace('~', expanduser('~'))

        config_dir = dirname(self._config)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir, 0744)

        if not os.path.exists(self._config):
            with open(self._config, 'w') as stream:
                stream.write("[general]\n")
                stream.write("available=\n")
                stream.write("disabled=\n")

        self._parser = DictionaryConfigParser()
        self._parser.read(self._config)

        dispatcher.add_listener('dictionary_found', self.on_dictionary_found, 0)
        dispatcher.add_listener('dictionary_enabled', self.on_dictionary_enabled, 0)
        dispatcher.add_listener('dictionary_disabled', self.on_dictionary_disabled, 0)

        self._disabled = self._parser.disabled
        self._available = self._parser.available

    @property
    def disabled(self):
        return self._disabled

    @property
    def available(self):
        return self._available

    def on_dictionary_found(self, event, dispatcher):
        dictionary = event.data
        if dictionary.name not in self._available:
            self._available.append(dictionary.name)
            self._parser.available = self._available
            self._parser.flush(self._config)

    def on_dictionary_enabled(self, event, dispatcher):
        dictionary_name = event.data
        if dictionary_name in self._disabled:

            self._disabled.pop(
                self._disabled.index(
                    dictionary_name
                )
            )

            self._parser.disabled = self._disabled
            self._parser.flush(self._config)

    def on_dictionary_disabled(self, event, dispatcher):
        dictionary_name = event.data
        if dictionary_name not in self._disabled:
            self._disabled.append(dictionary_name)
            self._parser.disabled = self._disabled
            self._parser.flush(self._config)
