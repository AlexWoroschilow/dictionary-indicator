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
import wx.grid


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
    _export_as = 1012
    _on_update = None
    _on_delete = None

    def __init__(self, layout, parent, on_update=None, on_delete=None):
        self._on_update = on_update
        self._on_delete = on_delete

        wx.Panel.__init__(self, parent, style=wx.TEXT_ALIGNMENT_LEFT)
        # Create a wxGrid object
        self._history = wx.grid.Grid(self, -1)

        # Then we call CreateGrid to set the dimensions of the grid
        # (100 rows and 10 columns in this example)
        self._history.CreateGrid(1, 4)
        self._history.SetColLabelSize(20)
        self._history.SetRowLabelSize(20)
        self._history.HideCol(0)

        self._history.Bind(wx.grid.EVT_GRID_CELL_CHANGED, self.on_changed)
        self._history.Bind(wx.EVT_SIZE, self.on_resize)

        sizer3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer3.Add(self._button_panel, proportion=1, flag=wx.EXPAND, border=layout.empty)
        sizer3.Add(self._history, proportion=30, flag=wx.EXPAND | wx.ALL, border=layout.empty)
        self.SetSizer(sizer3)

    @property
    def history(self):
        for row in range(0, self._history.GetNumberRows()):
            collection = []
            for column in range(0, self._history.GetNumberCols()):
                collection.append(self._history.GetCellValue(row, column))
            yield collection

    @history.setter
    def history(self, value=None):
        self._history.DeleteRows(numRows=self._history.GetNumberRows())
        for row, line in enumerate(value):
            if self._history.GetNumberRows() == row:
                self._history.AppendRows(1)
            for column, field in enumerate(line):
                if self._history.GetNumberCols() == column:
                    self._history.AppendCols(1)
                self._history.SetColSize(column, 130)
                self._history.SetCellValue(row, column, field)
        self._history.HideCol(0)

    @property
    def _button_panel(self):
        self._toolbar = wx.ToolBar(self, style=wx.TB_FLAT | wx.TB_VERTICAL | wx.TB_NODIVIDER)
        self._toolbar.Bind(wx.EVT_TOOL, self.on_export)
 
        self._toolbar.AddRadioTool(1012, self.scale(wx.Bitmap("./img/excel.png")))
        self._toolbar.AddRadioTool(1013, self.scale(wx.Bitmap("./img/csv.png")))
        self._toolbar.AddRadioTool(1014, self.scale(wx.Bitmap("./img/text.png")))
        self._toolbar.AddLabelTool(2012, 'Export to disk', self.scale(wx.Bitmap("./img/save.png")))
        self._toolbar.AddSeparator()
        self._toolbar.AddLabelTool(3012, 'Clean table', self.scale(wx.Bitmap("./img/clean.png")))
 
        self._toolbar.Realize()
 
        return self._toolbar

    @staticmethod
    def scale(bitmap, width=32, height=32):
        image = wx.ImageFromBitmap(bitmap)
        image = image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
        result = wx.BitmapFromImage(image)
        return result

    def on_export(self, event):
        if event.GetId() in [1012, 1013, 1014]:
            self._export_as = event.GetId()
            return None

        if event.GetId() in [2012]:
            if self._export_as in [1012]:
                return self.on_export_excel(event)
            if self._export_as in [1013]:
                return self.on_export_csv(event)
            if self._export_as in [1014]:
                return self.on_export_text(event)

        if event.GetId() in [3012]:
            return self.on_history_clean(event)

    def on_resize(self, event):
        width, height = self.GetClientSizeTuple()
        for col in range(1, 4):
            self._history.SetColSize(col, width/3)

    def on_changed(self, event):
        collection = []
        row = event.GetRow()
        for column in range(0, self._history.GetNumberCols()):
            collection.append(self._history.GetCellValue(row, column))
        if self._on_update is not None:
            self._on_update(collection)

    def on_history_clean(self, event):
        for row in range(0, self._history.GetNumberRows()):
            if self._on_delete is not None:
                index = self._history.GetCellValue(row, 0)
                self._on_delete([index, None, None, None])
        self._history.DeleteRows(numRows=self._history.GetNumberRows())

    def on_export_csv(self, event):
        dialog = wx.FileDialog(self, "Save As", "", "", "", wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if dialog.ShowModal() == wx.ID_OK:
            with open(dialog.GetPath(), 'w+') as stream:
                for fields in self.history:
                    stream.write("%s\n" % string.join(fields, ';'))
                stream.close()
        dialog.Destroy()

    def on_export_excel(self, event):
        dialog = wx.FileDialog(self, "Save As", "", "", "", wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if dialog.ShowModal() == wx.ID_OK:
            column0 = []
            column1 = []
            column2 = []
            for fields in self.history:
                index, date, word, description = fields
                column0.append(date)
                column1.append(word)
                column2.append(description)
            frame = DataFrame({'Date': column0, 'Words': column1, 'Translations': column2 })
            frame.to_excel(dialog.GetPath(), sheet_name='sheet1', index=False)
        dialog.Destroy()

    def on_export_text(self, event):
        dialog = wx.FileDialog(self, "Save As", "", "", "", wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if dialog.ShowModal() == wx.ID_OK:
            with open(dialog.GetPath(), 'w+') as stream:
                for fields in self.history:
                    stream.write("%s\n" % string.join(fields, "\t"))
                stream.close()
        dialog.Destroy()
