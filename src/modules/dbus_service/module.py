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
import platform

class Loader(object):
    _options = None

    def __init__(self, options=None):
        self._options = options

    def __enter__(self):
        return self

    @property
    def config(self):
        return 'config/services.yml'

    @property
    def enabled(self):
        if platform.system() in ["Linux"]:
            return True
        return False

    def on_loaded(self, container):
        pass

    def __exit__(self, type, value, traceback):
        pass
