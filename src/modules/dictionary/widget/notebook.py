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
import  wx.lib.mixins.listctrl  as  listmix

class ListCtrlAutoWidth(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    def __init__(self, parent, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, wx.ID_ANY, pos, size, style)
        listmix.ListCtrlAutoWidthMixin.__init__(self)
        self.setResizeColumn(0)

class DictionaryPage(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        style = wx.LC_REPORT | wx.BORDER_NONE | wx.LC_EDIT_LABELS | wx.LC_SORT_ASCENDING
        self._history = ListCtrlAutoWidth(self, style=style)
        self._history.InsertColumn(0, 'Dictionary')

        self._label = wx.StaticText(self, -1, label='loading...')

        sizer3 = wx.BoxSizer(wx.VERTICAL)
        sizer3.Add(self._history, proportion=20, flag=wx.ALL | wx.EXPAND)
        sizer3.Add(self._label, proportion=1, flag=wx.ALL | wx.EXPAND, border=15)

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
