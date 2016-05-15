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
import sys
sys.path.append('app')
sys.path.append('src')
sys.path.append('vendor')

import app
import optparse
import logging

if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option("-g", "--gui", action="store_true", default=False, dest="gui", help="enable grafic user interface")
    parser.add_option("-w", "--word", default="baum", dest="word", help="word to translate")

    (options, args) = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG)

    app = app.App(options, args)
    app.run(options, args)
