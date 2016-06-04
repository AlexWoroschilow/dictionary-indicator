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
import wx.html2


class DictionaryPage(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self._browser = wx.html2.WebView.New(self)
        theme = "%s/themes/statistic.html" % os.getcwd()
        with open(theme, 'r') as template:
            self._browser.SetPage(template.read(), "text/html")

        sizer1 = wx.BoxSizer(wx.VERTICAL)
        sizer1.Add(self._browser, 1, wx.EXPAND, 1)
        self.SetSizer(sizer1)
