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


class TranslationPage(wx.Panel):
    _callback_on_select = None
    _callback_on_search = None

    def __init__(self, parent=None, on_search=None, on_select=None, on_scan=None):
        self._callback_on_scan = on_scan
        self._callback_on_search = on_search
        self._callback_on_select = on_select
        wx.Panel.__init__(self, parent)

        self._search = wx.TextCtrl(self, wx.ID_ANY, "")
        self.Bind(wx.EVT_TEXT, self.on_search_selected, self._search)

        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer1.Add(self._search, 1, wx.ALL)

        self._browser = wx.html2.WebView.New(self)

        self._suggestions = wx.ListCtrl(self, style=wx.LC_LIST | wx.LC_NO_HEADER)
        self._suggestions.InsertColumn(0, 'Similar words')
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_suggestion_selected, self._suggestions)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_suggestion_selected, self._suggestions)

        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer2.Add(self._suggestions, 1, wx.EXPAND)
        sizer2.AddSpacer(1)
        sizer2.Add(self._browser, 3, wx.EXPAND)

        self._checkbox = wx.CheckBox(self, label='Scan and translate clipboard')
        self.Bind(wx.EVT_CHECKBOX, self.on_scan_checked, self._checkbox)

        sizer4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer4.Add(self._checkbox, 1, wx.ALL)

        sizer3 = wx.BoxSizer(wx.VERTICAL)
        sizer3.Add(sizer1, 1, wx.EXPAND)
        sizer3.AddSpacer(1)
        sizer3.Add(sizer2, 30, wx.EXPAND)
        sizer3.AddSpacer(1)
        sizer3.Add(sizer4, 1, wx.EXPAND)
        self.SetSizer(sizer3)

    @property
    def suggestions(self):
        pass

    @suggestions.setter
    def suggestions(self, value):
        self._suggestions.ClearAll()
        for index, word in enumerate(value):
            self._suggestions.InsertStringItem(index, word)
            if index > 30:
                break

    @property
    def word(self):
        self._search.GetValue()

    @word.setter
    def word(self, value):
        self._search.SetValue(value)

    @property
    def translations(self):
        pass

    @translations.setter
    def translations(self, translations):
        theme = "%s/themes/translation.html" % os.getcwd()
        with open(theme, 'r') as template:
            for translation in translations:
                if translation is not None:
                    self._browser.SetPage(template.read() % translation, "text/html")
                    return None


    def on_scan_checked(self, event):
        if self._callback_on_scan is not None:
            checkbox = event.GetEventObject()
            self._callback_on_scan(checkbox.GetValue())

    def on_search_selected(self, event):
        if self._callback_on_search is not None:
            word = self._search.GetValue()
            self._callback_on_search(word.encode('utf-8'))

    def on_suggestion_selected(self, event):
        if self._callback_on_select is not None:
            index = self._suggestions.GetFocusedItem()
            word = self._suggestions.GetItemText(index)
            self._callback_on_select(word.encode('utf-8'))
