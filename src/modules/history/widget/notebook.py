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
import wx
import string
import wx.html2
import wx.lib.mixins.listctrl as listmix


class EditableListCtrl(wx.ListCtrl, listmix.TextEditMixin):
    def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        listmix.TextEditMixin.__init__(self)


class HistoryPage(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self._history = EditableListCtrl(self, style=wx.LC_REPORT)
        self._history.InsertColumn(0, 'Date')
        self._history.SetColumnWidth(0, 200)
        self._history.InsertColumn(1, 'Word')
        self._history.SetColumnWidth(1, 200)
        self.Bind(wx.EVT_LIST_KEY_DOWN, self.on_key_pressed, self._history)

        sizer3 = wx.BoxSizer(wx.VERTICAL)
        sizer3.Add(self._history, 1, wx.EXPAND)

        self.SetSizer(sizer3)

    @property
    def history(self):
        item = -1
        while True:
            item = self._history.GetNextItem(item, wx.LIST_NEXT_BELOW, wx.LIST_STATE_DONTCARE)
            date = self._history.GetItemText(item, 0)
            word = self._history.GetItemText(item, 1)
            if len(date) and len(word):
                yield [date.encode('utf-8'), word.encode('utf-8')]
            if item == -1:
                break

    @history.setter
    def history(self, value):
        self._history.DeleteAllItems()
        for index, line in enumerate(value):
            self._history.InsertStringItem(index, 'line', 1)
            self._history.SetStringItem(index, 0, line[0])
            self._history.SetStringItem(index, 1, line[1])

    def on_key_pressed(self, event):
        if event.GetKeyCode() == wx.WXK_DELETE:
            item = self._history.GetFocusedItem()
            self._history.Select(self._history.GetNextItem(item))
            self._history.DeleteItem(item)
            return event.Skip()

        if event.GetKeyCode() in (wx.WXK_DOWN, wx.WXK_UP):
            item = self._history.GetFocusedItem()
            next = self._history.GetNextItem(item, wx.LIST_NEXT_ABOVE)
            self._history.Select(item, False)
            self._history.Select(next, True)
            return event.Skip()
