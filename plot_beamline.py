#!/usr/bin/env python3

import json
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


def plot_beamline(cfg, ax, show_names=True, box_h=0.1, alpha=0.5):

    s_names = {}

    for name, itm in cfg['Beamline elements'].items():
       if "s" in itm:
           s = itm['s']

           if s in s_names:
               s_names[s].append(name)
           else:
               s_names[s] = [name]

           if show_names:
               ax.plot([s,s], [0,-1], lw=1, color='blue', alpha=alpha)

           color = 'blue'
           h = box_h
           if 'type' in itm:
               itm_type = itm['type'].upper()
               if itm_type == "BEND":
                   color = 'green'
               elif itm_type == "QUAD":
                   h = box_h*2
                   color = 'red'
               elif itm_type == "BPM":
                   color = 'black'

           if 'L' in itm:
               L = itm['L']
               ax.add_patch(Rectangle((s-L/2, 0-h/2), L, h, facecolor=color, alpha=alpha))
           else:
               ax.scatter(s, 0.0, c=color, alpha=alpha, s=20, marker='s')

    if show_names:
        for s, itm in s_names.items():
            ax.text(s, -1, ", ".join(itm), verticalalignment='bottom', horizontalalignment='right',
                        color='blue', fontsize=9, rotation='vertical', alpha=alpha)

    s_values = np.array( list(s_names) )
    s_min = s_values.min()
    s_max = s_values.max()

    ax.plot([s_min,s_max], [0,0], color='gray', alpha=alpha, lw=1)

    #plt.grid()

    #plt.ylim(-0.35,+0.35)

    #plt.ylabel("$U$ (V)")

    #plt.title("BPM" + BPM)
    #plt.legend()

if __name__ == '__main__':
    json_file='beamline.json'
    if len(sys.argv) > 1:
        json_file = sys.argv[1]

    if os.path.exists(json_file):
        with open(json_file, "r") as f:
            cfg = json.load(f)

            fig, ax = plt.subplots(figsize=(11,4))

            title = json_file
            if "Name" in cfg:
                title = f"{cfg['Name']} ({json_file})"

            ax.set_title(title)

            plot_beamline(cfg, ax)
            ax.set_xlabel("$s$ (m)")

            fig.tight_layout()
            plt.show()

    else:
        print(f"No {json_file} file to plot!")
