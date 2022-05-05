#!/usr/bin/env python3

import json


class Aperture:
    def __init__(self):
        super().__init__()
        self.points_list: list = []
        self.factory: dict = {
            'elliptical': self.ell
        }

    def ell(self, ell_aper):
        self.points_list.append(ell_aper['s'])
        self.points_list.append(ell_aper['aper'])

    def load_aper_param(self, cfg):
        if 'Apertures' in cfg:
            for elem, aper_param in cfg['Apertures'].items():
                try:
                    self.factory[aper_param['type']](aper_param)
                except KeyError:
                    print(f"the key \'{aper_param['type']}\' is wrong!")

        return self.points_list


if __name__ == '__main__':
    aperture_file = 'aperture_dr.json'
    with open(aperture_file, "r") as f:
        aperture_cfg = json.load(f)

    aper = Aperture().load_aper_param(aperture_cfg)
    print(aper)

