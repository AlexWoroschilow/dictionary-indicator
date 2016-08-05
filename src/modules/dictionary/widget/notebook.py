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
import wx.html2


class DictionaryPage(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self._history = wx.ListCtrl(self, style=wx.LC_LIST | wx.LC_HRULES)
        self._history.InsertColumn(0, 'Dictionary')
        self._history.SetColumnWidth(0, 300)

        self._label = wx.StaticText(self, -1, label='loading...')

        sizer3 = wx.BoxSizer(wx.VERTICAL)
        sizer3.Add(self._history, 40, wx.EXPAND)
        sizer3.AddSpacer(1)
        sizer3.Add(self._label, 1, wx.EXPAND)

        self.SetSizer(sizer3)

    @property
    def dictionaries(self):
        pass

    @dictionaries.setter
    def dictionaries(self, collection):
        for index, dictionary in enumerate(collection):
            self._history.InsertStringItem(index, 'line', 1)
            self._history.SetStringItem(index, 0, dictionary.name)

        message = "%s dictionaries found" % self._history.GetItemCount()
        self._label.SetLabelText(message)
