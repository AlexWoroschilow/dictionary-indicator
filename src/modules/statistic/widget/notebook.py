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
from dateutil.parser import parse
import matplotlib

matplotlib.use('WXAgg')

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure


class StatisticPage(wx.Panel):
    _template = None

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.figure = Figure(facecolor='white')
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self, -1, self.figure)

        self._label = wx.StaticText(self, -1, label='loading...')

        sizer1 = wx.BoxSizer(wx.VERTICAL)
        sizer1.Add(self.canvas, 40, wx.EXPAND, 1)
        sizer1.AddSpacer(1)
        sizer1.Add(self._label, 1, wx.EXPAND)

        self.SetSizer(sizer1)

    @property
    def history(self):
        pass

    @history.setter
    def history(self, history):
        collection = {}
        for fields in history:

            if len(fields) == 3:
                datetime, word, translation = fields
            else:
                datetime, word = fields
                
            date = parse(datetime, fuzzy=True).date()
            date_string = date.strftime("%d %b %y")

            if not collection.has_key(date_string):
                collection[date_string] = 1
                continue

            collection[date_string] += 1

        labels = collection.keys()
        labels.reverse()

        values = collection.values()
        values.reverse()

        positions = [i for i in range(0, len(labels))]

        self.axes.clear()
        if len(labels) > 1 and len(values) > 1:
            self.axes.plot(positions, values, linewidth=3.0)

        self.axes.set_xticks(positions)
        self.axes.set_xticklabels(labels, rotation=23, fontdict={'size': 9})
        self.axes.set_ylabel('Amount of words')

        message = "%s days history statistic" % len(labels)
        self._label.SetLabelText(message)

        self.canvas.draw()
