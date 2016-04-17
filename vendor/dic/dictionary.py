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
import string
import copy
import re
import gc as garbage
from pystardict import Dictionary
from pystardict import _StarDictIfo
from os.path import expanduser


class DictionarySource(object):
    def __init__(self, name, path):
        self._name = name
        self._path = path

    @property
    def name(self):
        return self._name

    @property
    def path(self):
        return self._path


class DictionarySourceCollection(object):
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


class DictionaryWord(object):
    def __init__(self, word):
        self._word = word

    @property
    def word(self):
        return [
            self._word,
            self._word.capitalize(),
        ]

    @property
    def variants(self):
        collection = []
        if len(self._word) >= 2:
            word_slice = self._word[:-1]
            collection.append(word_slice)
            collection.append(word_slice.capitalize())

        if len(self._word) >= 3:
            word_slice = self._word[:-2]
            collection.append(word_slice)
            collection.append(word_slice.capitalize())

        if len(self._word) >= 4:
            word_slice = self._word[:-3]
            collection.append(word_slice)
            collection.append(word_slice.capitalize())

        return collection

    def __str__(self):
        return self._word


class DictionaryWordTranslation(object):
    _word = None
    _translation = None

    @property
    def word(self):
        return self._word

    @property
    def translation(self):
        return self._translation

    def __init__(self, word, translation):
        self._word = word
        self._translation = translation

    def __len__(self):
        return len(self._translation)

    def __str__(self):
        return self._translation


class DictionaryManager(object):
    _word = None
    _config = None
    _sources = None
    _disabled = []
    _dictionaries = []

    def __init__(self, config, dispatcher, sources):
        self._config = config
        self._sources = sources

        dispatcher.add_listener('dictionary.clipboard', self.on_clipboard_text, 0)
        dispatcher.add_listener('dictionary_found', self.on_dictionary_found, 10)
        dispatcher.add_listener('dictionary_enabled', self.on_dictionary_enabled, 10)
        dispatcher.add_listener('dictionary_disabled', self.on_dictionary_disabled, 10)

        with DictionarySourceCollection(sources) as source_collection:
            for source in source_collection:
                with _StarDictIfo(source, self) as dictionary_info:
                    dictionary_name = dictionary_info.bookname
                    event = dispatcher.new_event(DictionarySource(dictionary_name, source))
                    dispatcher.dispatch('dictionary_found', event)

    @property
    def word(self):
        return self._word

    @property
    def dictionaries(self):
        for dictionary in self._dictionaries:
            yield dictionary

    @property
    def available(self):
        if self._config is not None:
            return self._config.available
        return []

    @property
    def enabled(self):
        for dictionary in self.dictionaries:
            if dictionary.name not in self.disabled:
                yield dictionary

    @property
    def disabled(self):
        if self._config is not None:
            return self._config.disabled
        return []

    def on_dictionary_found(self, event, dispatcher):
        dictionary_source = event.data
        if dictionary_source.name not in self.disabled:
            with Dictionary(dictionary_source.path) as dictionary:
                self._dictionaries.append(dictionary)
                garbage.collect()

    def on_clipboard_text(self, event, dispatcher):
        word = event.data
        if word is not None and len(word):
            translation = self.get(event.data)
            if translation is not None and len(translation):
                event = dispatcher.new_event(translation)
                dispatcher.dispatch('dictionary.translation_clipboard', event)

    def on_dictionary_enabled(self, event, dispatcher):
        with DictionarySourceCollection(self._sources) as source_collection:
            for source in source_collection:
                with _StarDictIfo(source, self) as dictionary_info:
                    dictionary_name = dictionary_info.bookname
                    if dictionary_name is event.data:
                        event = dispatcher.new_event(DictionarySource(dictionary_name, source))
                        dispatcher.dispatch('dictionary_found', event)
                        garbage.collect()
                        break

    def on_dictionary_disabled(self, event, dispatcher):
        for dictionary in self._dictionaries:
            if dictionary.name is event.data:
                index = self._dictionaries.index(dictionary)
                self._dictionaries.pop(index)
                garbage.collect()
                break

    def matches(self, match):
        for dictionary in self._dictionaries:
            for word in dictionary.matches(match):
                yield word

    def get(self, text):
        self._word = DictionaryWord(text)
        translations = []
        for dictionary in self.enabled:
            for variant in self._word.word:
                if dictionary.has_key(variant):
                    translations.append(dictionary.get(variant))
                    break

        if not len(translations):
            for dictionary in self.enabled:
                for variant in self._word.variants:
                    if dictionary.has_key(variant):
                        translations.append(dictionary.get(variant))
                        break

        if not len(translations):
            return None

        return DictionaryWordTranslation(text, string.join(translations, ''))
