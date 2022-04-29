#!/usr/bin/env python3

from PyQt5.QtWidgets import QApplication
import json
import os
import sys
import numpy as np
from threading import Timer

from aperture import Aperture
from plot_orbit_correction import OrbitCorMatPlot

PROTOCOL = 'cx'
if PROTOCOL == 'cx':
    from cx_connection import DataExchange


class OrbitCorrection:
    def __init__(self):
        super().__init__()
        beamline_file = 'beamline.json'
        responses_file = 'responses.json'
        aperture_file = 'aperture_dr.json'

        # think about opening files and action if true/false
        try:
            f = open(beamline_file, "r")
            beamline_cfg = json.load(f)
        finally:
            print(f"Beamline file: {beamline_file}")
            f.close()

        with open(responses_file, 'r') as f:
            responses_cfg = json.load(f)
            print(f"Response matrix file: {responses_file}")

        with open(aperture_file, "r") as f:
            aperture_cfg = json.load(f)
            aper = Aperture().load_aper_param(aperture_cfg)

        self.plot_view = OrbitCorMatPlot(self.check_con, self.check_con, aper=aper, bline=beamline_cfg)

    def check_con(self, event):
        print('cucuepta')


if __name__ == '__main__':
    # app = QApplication(['resp_orbittt'])
    # # data_exchange = DataExchange('/home/vbalakin/PycharmProjects/TuneBeamParameters/cx_data_config.json',
    # #                                'bpm', 'cor')

    o_r = OrbitCorrection()
    # sys.exit(app.exec_())
