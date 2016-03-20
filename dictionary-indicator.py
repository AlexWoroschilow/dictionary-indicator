#!/usr/bin/python2
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
import gi
import sys
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

sys.path.append('/usr/lib/dictionary-indicator/vendor')
from vendor import ioc

if __name__ == "__main__":
    ioc.build(['/usr/lib/dictionary-indicator/vendor/services.yml'])
    Gtk.main()