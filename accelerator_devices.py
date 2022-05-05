#!/usr/bin/env python3

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QObject
import numpy as np


class BPM(QObject):
    valueChanged = pyqtSignal(float, int, str)

    def __init__(self, name, order, **prop):
        super().__init__()
        self.name = name
        self.plane = prop.get('plane', 'NO KEY')
        self.pos = prop.get('s', 'NO KEY')
        self.length = prop.get('L', 'NO KEY')
        self.val = prop.get('kick', 'NO KEY')

        self.or_num: int = order
        self.val: float = -1.0

    def val_changed(self, chan):
        self.val = chan.val
        self.valueChanged.emit(self.val, self.or_num, self.plane)


class Corrector(QObject):
    valueChanged = pyqtSignal(float, int, str)

    def __init__(self, name, order, **prop):
        super().__init__()
        self.name = name
        self.plane = prop.get('plane', 'NO KEY')
        self.pos = prop.get('s', 'NO KEY')
        self.length = prop.get('L', 'NO KEY')
        self.val = prop.get('kick', 'NO KEY')
        self.upper_limit = prop.get('max_kick', 'NO KEY')
        self.lower_limit = prop.get('min_kick', 'NO KEY')

        self.or_num: int = order
        self.val: float = -1.0

    def val_changed(self, chan):
        self.val = chan.val
        self.valueChanged(self.val, self.or_num, self.plane)
