#!/usr/bin/env python3

import json
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from plot_beamline_old import plot_beamline


def plot_response(resp_name, resp_data, beamline_cfg, ax, plane='X'):
    s_values=[]
    slope_values=[]
    slope_error_values=[]
    units = ""
    for name, itm in resp_data.items():
        observed, varied = name.split(" / ")
        if varied == resp_name and observed in beamline_cfg["Beamline elements"]:
            element = beamline_cfg["Beamline elements"][observed]
            if "plane" in element and element["plane"] == plane:
                s_values.append(element["s"])
                units = itm["units"]
                slope_values.append(itm["slope"])
                slope_error_values.append(itm["slope error"])
    ax.plot(s_values, slope_values, "--", marker="o", lw=3)
    return s_values, slope_values, units

if __name__ == '__main__':

    resp_name = None
    if len(sys.argv) > 1:
        resp_name = sys.argv[1]

    resp_file='responses.json'
    if len(sys.argv) > 2:
        resp_file = sys.argv[2]

    beamline_file='beamline.json'
    if len(sys.argv) > 3:
        beamline_file = sys.argv[3]

    if os.path.exists(resp_file) and os.path.exists(beamline_file):
        with open(resp_file, "r") as f:
            cfg = json.load(f)
            if not resp_name:
                resp_name = list(cfg["response data"].keys())[0]
                observed, resp_name = resp_name.split(" / ")
            print(f'Plot response to "{resp_name}"')
        with open(beamline_file, "r") as f:
            beamline_cfg = json.load(f)
            print(f"Beamline file: {beamline_file}")

        fig, (axx, axy) = plt.subplots(2, 1, sharex=True, sharey=True, figsize=(11,6))

        title = f'Response to "{resp_name}" ({resp_file})'

        axx.set_title(title)

        # plot beamline
        s, x_slopes, units = \
            plot_response(resp_name, cfg["response data"], beamline_cfg, axx, plane="X")
        axx.set_ylabel(f'x-response ({units})')

        s, y_slopes, units = \
            plot_response(resp_name, cfg["response data"], beamline_cfg, axy, plane="Y")
        axy.set_ylabel(f'y-response ({units})')

        axy.set_xlabel("$s$ (m)")

        slopes = np.concatenate([x_slopes,y_slopes])
        slope_range = slopes.max()-slopes.min()

        box_h = 0.1
        if slope_range > 0:
            box_h = slope_range*0.1

        plot_beamline(beamline_cfg, axx, show_names=False, box_h=box_h)
        plot_beamline(beamline_cfg, axy, show_names=False, box_h=box_h)

        fig.tight_layout()
        plt.show()

    else:
        print(f"No files to plot!")
