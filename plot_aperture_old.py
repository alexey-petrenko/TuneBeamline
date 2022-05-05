#!/usr/bin/env python3

import json
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from plot_beamline_old import plot_beamline


def plot_aperture(cfg, ax, plane='X'):

    for name, itm in cfg['Apertures'].items():
        visible = True # visible by default
        if "visible" in itm:
            if not itm["visible"]: visible = False

        if visible:
            s_shift = 0
            if "s_shift" in itm:
                s_shift = itm['s_shift']
            if 'definition' in itm:
                itm = cfg['Apertures'][itm['definition']]

            s = np.array(itm["s"]) + s_shift

            if plane == 'X':
                if "Xmax" in itm:
                    Xmax = np.array(itm["Xmax"])*1e3 # mm
                    ax.plot(s, Xmax, lw=2, c='black', alpha=0.4)
                    if "Xmin" in itm:
                        Xmin = np.array(itm["Xmin"])*1e3 # mm
                    else: Xmin = -Xmax
                    ax.plot(s, Xmin, lw=2, c='black', alpha=0.4)

            if plane == 'Y':
                if "Ymax" in itm:
                    Ymax = np.array(itm["Ymax"])*1e3 # mm
                    ax.plot(s, Ymax, lw=2, c='black', alpha=0.4)
                    if "Ymin" in itm:
                        Ymin = np.array(itm["Ymin"])*1e3 # mm
                    else: Ymin = -Ymax
                    ax.plot(s, Ymin, lw=2, c='black', alpha=0.4)


if __name__ == '__main__':

    aperture_file='aperture.json'
    if len(sys.argv) > 1:
        aperture_file = sys.argv[1]

    beamline_file='beamline.json'
    if len(sys.argv) > 2:
        beamline_file = sys.argv[2]

    if os.path.exists(aperture_file):
        with open(aperture_file, "r") as f:
            cfg = json.load(f)

            fig, (axx, axy) = plt.subplots(2, 1, sharex=True, sharey=True, figsize=(11,6))

            title = aperture_file
            if "Name" in cfg:
                title = f'{cfg["Name"]} ({aperture_file})'

            axx.set_title(title)

            if os.path.exists(beamline_file):
                with open(beamline_file, "r") as f:
                    beamline_cfg = json.load(f)
                    print(f"Beamline file: {beamline_file}")

                    plot_beamline(beamline_cfg, axx, show_names=False, box_h=5.0)
                    plot_beamline(beamline_cfg, axy, show_names=False, box_h=5.0)

            plot_aperture(cfg, axx, plane="X")
            plot_aperture(cfg, axy, plane="Y")

            axx.set_ylabel("$x$ (mm)")

            axy.set_xlabel("$s$ (m)")
            axy.set_ylabel("$y$ (mm)")

            fig.tight_layout()
            plt.show()

    else:
        print(f"No {aperture_file} file to plot!")
