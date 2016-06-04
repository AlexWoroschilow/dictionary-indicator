import os
import wx
import wx.html2
import string


class TranslationPopup(wx.PopupWindow):
    def __init__(self, parent, style):
        wx.PopupWindow.__init__(self, None, style)

        self._browser = wx.html2.WebView.New(self)
        self._browser.SetPage("This is a special kind of top level\n", "")

        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer2.Add(self._browser, 3, wx.EXPAND)
        self.SetSizer(sizer2)

        wx.CallAfter(self.Refresh)

    def setTranslations(self, translations):
        theme = "%s/themes/popup.html" % os.getcwd()
        with open(theme, 'r') as template:
            translation = string.join(translations, '')
            self._browser.SetPage(template.read() % translation, "text/html")


class ChildFrame(wx.Frame):
    def __init__(self, parent=None, text=None):
        wx.Frame.__init__(self, None, size=(150,100), title='ChildFrame')
        self.SetSize((400, 200))
        self.SetMinSize((400, 100))

        self._browser = wx.TextCtrl(self, -1, pos=(0,0), size=(100,20), style=wx.DEFAULT)
        self._browser.write(text)

        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer2.Add(self._browser, 3, wx.EXPAND)
        self.SetSizer(sizer2)

    def SetTranslations(self, translations):
        theme = "%s/themes/popup.html" % os.getcwd()
        with open(theme, 'r') as template:
            translation = string.join(translations, '')
            self._browser.write(translation)
            # self._browser.SetPage(template.read() % translation, "text/html")

            # def onbutton(self, evt):
    #     text = self.txt.GetValue()
    #     self.parent.txt.write('Child says: %s' %text)


class TranslationPopupFrame(wx.Frame):

    def __init__(self, parent, translations):
        wx.Frame.__init__(self, parent, title="Test Popup")

        win = TranslationPopup(self, wx.SIMPLE_BORDER)
        win.SetPosition(wx.GetMousePosition())
        win.setTranslations(string.join(translations, ''))

    def on_test(self, event):
        print ("asdf")
