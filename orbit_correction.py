#!/usr/bin/env python3

from PyQt5.QtWidgets import QApplication
import json
import os
import sys
import numpy as np
from threading import Timer

from aperture import Aperture
from plot_orbit_correction import OrbitCorMatPlot
from accelerator_devices import BPM, Corrector

PROTOCOL = 'cx'
if PROTOCOL == 'cx':
    from cx_connection import DataExchange


class OrbitCorrection:
    def __init__(self):
        super().__init__()
        self.orbit: dict = {}
        self.cur: dict = {}
        self.bpm_x: list = []
        self.bpm_z: list = []
        self.cor_x: list = []
        self.cor_z: list = []

        beamline_file = 'beamline.json'
        responses_file = 'responses.json'
        aperture_file = 'aperture_dr.json'

        # think about opening files and action if true/false
        try:
            f = open(beamline_file, "r")
            self.beamline_cfg = json.load(f)
        finally:
            print(f"Beamline file: {beamline_file}")
            f.close()

        with open(responses_file, 'r') as f:
            responses_cfg = json.load(f)
            print(f"Response matrix file: {responses_file}")

        with open(aperture_file, "r") as f:
            aperture_cfg = json.load(f)
            aper = Aperture().load_aper_param(aperture_cfg)

        bpm, s, col = self.get_order('BPM', 'X')
        self.orbit['X'] = np.zeros(len(bpm))
        self.bpm_x = [BPM(bpm[i], i, **col[bpm[i]]) for i in range(len(bpm))]
        for bpm in self.bpm_x:
            bpm.valueChanged.connect(self.bpm_val_changed)

        bpm, s, col = self.get_order('BPM', 'Y')
        self.orbit['Y'] = np.zeros(len(bpm))
        self.bpm_y = [BPM(bpm[i], i, **col[bpm[i]]) for i in range(len(bpm))]
        for bpm in self.bpm_y:
            bpm.valueChanged.connect(self.bpm_val_changed)

        cor, s, col = self.get_order('corrector', 'X')
        self.cur['X'] = np.zeros(len(cor))
        self.cor_x = [Corrector(cor[i], i, **col[cor[i]]) for i in range(len(cor))]
        for cor in self.cor_x:
            cor.valueChanged.connect(self.cur_val_changed)

        cor, s, col = self.get_order('corrector', 'Y')
        self.cur['Y'] = np.zeros(len(cor))
        self.cor_y = [Corrector(cor[i], i, **col[cor[i]]) for i in range(len(cor))]
        for cor in self.cor_y:
            cor.valueChanged.connect(self.cur_val_changed)

    def bpm_val_changed(self, val: float, i: int, plane: str) -> None:
        self.orbit[plane][i] = val

    def cur_val_changed(self, val: float, i: int, plane: str) -> None:
        self.cur[plane][i] = val

    def get_order(self, typo: str, plane: str) -> (list, list, dict):
        coll = {}
        for elem_name, elem_par in self.beamline_cfg['Beamline elements'].items():
            if elem_par['type'] == typo and elem_par['plane'] == plane:
                coll[elem_name] = elem_par

        names = np.array([name for name, elem in coll.items() if elem['plane'] == plane])
        s = np.array([elem['s'] for name, elem in coll.items() if elem['plane'] == plane])
        ind = np.argsort(s)
        return names[ind], s[ind], coll

    def check_con(self, event):
        print('cucuepta')


if __name__ == '__main__':
    # app = QApplication(['resp_orbittt'])
    o_r = OrbitCorrection()
    # sys.exit(app.exec_())
