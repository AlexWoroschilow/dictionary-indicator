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
import logging
from collections import OrderedDict


class Event(object):
    def __init__(self, data=None):
        self.__name = None
        self.__data = data

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = value

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, value):
        self.__data = value


class EventSubscriberInterface(object):
    @property
    def subscribed(self):
        raise NotImplementedError()


class EventListenerItem(object):
    def __init__(self, listener, priority=0):
        self.__listener = listener
        self.__priority = priority

    @property
    def listener(self):
        return self.__listener

    @property
    def priority(self):
        return self.__priority

    def __eq__(self, other):
        return self.__listener == other.__listener


class EventDispatcher(object):
    _logger = []

    def __init__(self):
        self._logger = logging.getLogger('event_dispatcher')
        self._listeners = {}


    @staticmethod
    def new_event(data=None):
        return Event(data)

    def dispatch(self, event_name, event=None):
        if event is None:
            event = Event()
        elif not isinstance(event, Event):
            raise ValueError('Unexpected event type given')
        event.name = event_name

        if event_name not in self._listeners:
            return event

        for listener_item in self._listeners[event_name]:
            listener_item.listener(event, self)

        return event

    def add_listener(self, event_name, listener, priority=0):
        if event_name not in self._listeners:
            self._listeners[event_name] = []

        self._listeners[event_name].append(EventListenerItem(listener, priority))
        self._listeners[event_name].sort(key=lambda item: item.priority)

    def remove_listener(self, name, removed=None):
        if name not in self._listeners:
            return None

        if not removed:
            del self._listeners[name]
            return None

        listener_removed = EventListenerItem(removed)
        index = self._listeners[name].index(listener_removed)
        if index is not None:
            self._listeners[name].pop(index)
            return None

    def add_subscriber(self, subscriber):
        self._logger.debug("subscriber:  %s" %  subscriber.__class__.__name__)
        for name, params in subscriber.subscribed_events:
            if isinstance(params, str):
                self.add_listener(name, getattr(subscriber, params))
                continue

            if not isinstance(params, list):
                raise ValueError('Invalid params for event "%s"' % name)

            if not params:
                raise ValueError('Invalid params "%r" for event "%s"' % (params, name))

            if len(params) <= 2 and isinstance(params[0], str):
                priority = params[1] if len(params) > 1 else 0
                self.add_listener(name, getattr(subscriber, params[0]), priority)
                continue

            for listener in params:
                priority = listener[1] if len(listener) > 1 else 0
                self.add_listener(name, getattr(subscriber, listener[0]), priority)

# if __name__ == "__main__":
#     dispatcher = EventDispatcher()
#     dispatcher.add_listener('app.on_shutdown', lambda e, d: print("func_2"), 1)
#     dispatcher.add_listener('app.on_shutdown', lambda e, d: print("func_1"), 0)
#     dispatcher.add_listener('app.on_shutdown', lambda e, d: print("func_3"), 2)
#     dispatcher.add_listener('app.on_shutdown', lambda e, d: print("func_4"), 3)
#
#     dispatcher.dispatch('app.on_shutdown', Event())
