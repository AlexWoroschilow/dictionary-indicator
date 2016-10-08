'''
Created on Oct 6, 2016

@author: sensey
'''
import platform


class Layout(object):

    def __init__(self):
        pass

    @property
    def icon(self):
        return "img/dictionary.svg"

    @property
    def border(self):
        if platform.system() in ["Darwin"]:
            return 0
        return 15

    @property
    def width(self):
        if platform.system() in ["Darwin"]:
            return 500
        return 900

    @property
    def height(self):
        if platform.system() in ["Darwin"]:
            return 600
        return 1000
