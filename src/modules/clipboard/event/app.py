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
import wx
import time
import threading


class ClipboardEventSubscriber(object):
    _container = None

    def __init__(self, container=None):
        self._container = container

    @property
    def subscribed_events(self):
        yield ('kernel_event.start', ('on_started'))

    def on_started(self, event, dispatcher):

        def worker():
            previous = None
            event_dispatcher = self._container.get('event_dispatcher')
            while True:
                do = wx.TextDataObject()
                wx.TheClipboard.Open()
                success = wx.TheClipboard.GetData(do)
                wx.TheClipboard.Close()
                if success:
                    current = do.GetText()
                    if current != previous:
                        event = event_dispatcher.new_event(current)
                        event_dispatcher.dispatch('dict_event.clipboard', event)
                        previous=current
                time.sleep(0.4)

        if not wx.TheClipboard.IsOpened():  # may crash, otherwise
            t = threading.Thread(target=worker)
            t.start()

