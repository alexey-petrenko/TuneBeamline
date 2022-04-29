#!/usr/bin/env python3

import numpy as np


class BPM:
    def __init__(self, name, **kwargs):
        super().__init__()
        self.name = name
        self.typo = kwargs.get('plane', 'NO KEY')
        self.pos = kwargs.get('s', 'NO KEY')
        self.lenght = kwargs.get('L', 'NO KEY')
        self.val = kwargs.get('kick', 'NO KEY')


class Corrector:
    def __init__(self, name, **kwargs):
        super().__init__()
        self.name = name
        self.typo = kwargs.get('plane', 'NO KEY')
        self.pos = kwargs.get('s', 'NO KEY')
        self.lenght = kwargs.get('L', 'NO KEY')
        self.val = kwargs.get('kick', 'NO KEY')
        self.upper_limit = kwargs.get('max_kick', 'NO KEY')
        self.lower_limit = kwargs.get('min_kick', 'NO KEY')


class AccElemCollection:
    def __init__(self, name, typo, config):
        super().__init__()
        self.name = name
        self.elem_coll = {'BPM': BPM, 'corrector': Corrector}
        self.coll: dict = {}

        for elem_name, elem_par in config['Beamline elements'].items():
            if elem_par['type'] == typo:
                self.coll[elem_name] = self.elem_coll[typo](elem_name, **elem_par)

        self.names_x = np.array([name for name, elem in self.coll.items() if elem.typo == "X"])
        self.s_x = np.array([elem.pos for name, elem in self.coll.items() if elem.typo == "X"])
        self.ind_x = np.argsort(self.s_x)
        self.names_y = np.array([name for name, elem in self.coll.items() if elem.typo == "Y"])
        self.s_y = np.array([elem.pos for name, elem in self.coll.items() if elem.typo == "Y"])
        self.ind_y = np.argsort(self.s_y)
