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
import glob
import copy
from pystardict import Dictionary
from pystardict import _StarDictIfo
from os.path import expanduser


class DictionarySources(object):
    def __init__(self, sources):
        self._sources = copy.copy(sources)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def __iter__(self):
        while len(self._sources):
            source = self._sources.pop()
            if source.find('~') is not -1:
                source = source.replace('~', expanduser('~'))

            for path in glob.glob(source):
                if os.path.isdir(path):
                    self._sources.append("%s/*" % path)
                    continue
                if path.find('.ifo') is not -1:
                    yield path.replace('.ifo', '')


class DictionaryManager(object):
    _word = None
    _dictionaries = []

    def __init__(self, sources):
        with DictionarySources(sources) as collection:
            for source in collection:
                with _StarDictIfo(source, self) as info:
                    with Dictionary(source) as dictionary:
                        self._dictionaries.append(dictionary)

    @property
    def dictionaries(self):
        for dictionary in self._dictionaries:
            yield dictionary

    def translate(self, word):
        translations = []
        for dictionary in self.dictionaries:
            if dictionary.has_key(word):
                translation = dictionary.get(word)
                if translation is not None:
                    translations.append(translation)
        return translations
