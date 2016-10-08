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
import string

from pandas import DataFrame
from dateutil.parser import parse

import wx
import wx.lib.mixins.listctrl as listmix
import wx.lib.buttons as buttons


class ListCtrlAutoWidth(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    def __init__(self, parent, ID, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        listmix.ListCtrlAutoWidthMixin.__init__(self)
        self.setResizeColumn(2)


class EditableListCtrl(ListCtrlAutoWidth, listmix.TextEditMixin):
    def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0):
        ListCtrlAutoWidth.__init__(self, parent, ID, pos, size, style)
        listmix.TextEditMixin.__init__(self)


class HistoryPage(wx.Panel):
    def __init__(self, layout, parent):
        wx.Panel.__init__(self, parent, style=wx.TEXT_ALIGNMENT_LEFT)
        style = wx.LC_REPORT | wx.BORDER_NONE | wx.LC_EDIT_LABELS | wx.LC_SORT_ASCENDING
        self._history = EditableListCtrl(self, style=style)
        self._history.InsertColumn(0, 'Date', width=300)
        self._history.InsertColumn(1, 'Word')
        self._history.InsertColumn(2, 'Translation', width=300)
        self._history.Bind(wx.EVT_LIST_KEY_DOWN, self.on_key_pressed)

        sizer3 = wx.BoxSizer(wx.VERTICAL)
        sizer3.Add(self._history, proportion=30, flag=wx.ALL | wx.EXPAND, border=layout.empty)
        sizer3.Add(self._button_panel, proportion=1, flag=wx.ALL | wx.EXPAND, border=layout.empty)
        self.SetSizer(sizer3)

    @property
    def _button_panel(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        self._export_excel = buttons.GenButton(self, wx.ID_ANY, "Export as Excel", style=wx.BORDER_NONE)
        self._export_excel.Bind(wx.EVT_BUTTON, self.on_export_excel)
        sizer.Add(self._export_excel, proportion=1, flag=wx.ALL | wx.EXPAND)

        self._export_csv = buttons.GenButton(self, wx.ID_ANY, "Export as CSV", style=wx.BORDER_NONE)
        self._export_csv.Bind(wx.EVT_BUTTON, self.on_export_csv)
        sizer.Add(self._export_csv, proportion=1, flag=wx.ALL | wx.EXPAND)

        self._export_text = buttons.GenButton(self, wx.ID_ANY, "Export as Text", style=wx.BORDER_NONE)
        self._export_text.Bind(wx.EVT_BUTTON, self.on_export_text)
        sizer.Add(self._export_text, proportion=1, flag=wx.ALL | wx.EXPAND)

        self._clean = buttons.GenButton(self, wx.ID_ANY, "Clean history", style=wx.BORDER_NONE)
        self._clean.Bind(wx.EVT_BUTTON, self.on_history_clean)
        sizer.Add(self._clean, proportion=1, flag=wx.ALL | wx.EXPAND)

        return sizer

    @property
    def history(self):
        for index in range(-1, self._history.GetItemCount()):
            item = self._history.GetNextItem(index, wx.LIST_NEXT_BELOW, wx.LIST_STATE_DONTCARE)
            if item == -1:
                break

            date = self._history.GetItemText(item, 0)
            word = self._history.GetItemText(item, 1)
            trans = self._history.GetItemText(item, 2)
            if not len(date) or not len(word):
                continue

            datetime = parse(date, fuzzy=True)
            if not datetime:
                continue

            yield [datetime.strftime("%Y.%m.%d %H:%M:%S"), word.encode('utf-8'), trans.encode('utf-8')]

    @history.setter
    def history(self, value):
        self._history.DeleteAllItems()
        for index, line in enumerate(value):
            self._history.InsertStringItem(index, 'line', 1)

            self._history.SetStringItem(index, 0, line[0])
            self._history.SetStringItem(index, 1, line[1])
            if len(line) < 3:
                continue

            self._history.SetStringItem(index, 2, line[2])

    def on_export_excel(self, event):
        dialog = wx.FileDialog(self, "Save As", "", "", "", wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if dialog.ShowModal() == wx.ID_OK:

            column0 = []
            column1 = []
            column2 = []
            for fields in self.history:
                column0.append(fields[0])
                column1.append(fields[1])
                column2.append(fields[2])

            frame = DataFrame({
                'Date': column0,
                'Words': column1,
                'Translations': column2
            })

            frame.to_excel(dialog.GetPath(), sheet_name='sheet1', index=False)

        dialog.Destroy()

    def on_export_csv(self, event):
        dialog = wx.FileDialog(self, "Save As", "", "", "", wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if dialog.ShowModal() == wx.ID_OK:
            with open(dialog.GetPath(), 'w+') as stream:
                for fields in self.history:
                    stream.write("%s\n" % string.join(fields, ';'))
                stream.close()
        dialog.Destroy()

    def on_export_text(self, event):
        dialog = wx.FileDialog(self, "Save As", "", "", "", wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if dialog.ShowModal() == wx.ID_OK:
            with open(dialog.GetPath(), 'w+') as stream:
                for fields in self.history:
                    stream.write("%s\n" % string.join(fields, "\t"))
                stream.close()
        dialog.Destroy()

    def on_history_clean(self, event):
        self._history.DeleteAllItems()

    def on_key_pressed(self, event):
        if event.GetKeyCode() in [wx.WXK_DELETE]:
            return self.on_delete_pressed(event)

        if event.GetKeyCode() in [wx.WXK_RETURN]:
            return self.on_enter_pressed(event)

        if event.GetKeyCode() in [wx.WXK_UP, wx.WXK_PAGEUP]:
            return self.on_up_pressed(event)

        if event.GetKeyCode() in [wx.WXK_DOWN, wx.WXK_PAGEDOWN]:
            return self.on_down_pressed(event)

    def on_delete_pressed(self, event):
        item = self._history.GetFocusedItem()
        self._history.DeleteItem(item)

    def on_enter_pressed(self, event):
        pass

    def on_up_pressed(self, event):
        item = self._history.GetFocusedItem()
        below = self._history.GetNextItem(item, wx.LIST_NEXT_BELOW)

        if below in [1]:
            return None

        self._history.Select(item, False)
        self._history.Select(below, True)
        return event.Skip()

    def on_down_pressed(self, event):
        item = self._history.GetFocusedItem()
        above = self._history.GetNextItem(item, wx.LIST_NEXT_ABOVE)

        if above in [-1]:
            return None

        self._history.Select(item, False)
        self._history.Select(above, True)
        return event.Skip()
