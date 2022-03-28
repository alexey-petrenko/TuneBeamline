#!/usr/bin/env python3

import json, os, sys
import numpy as np
import matplotlib.pyplot as plt

from plot_beamline import plot_beamline
from plot_aperture import plot_aperture

def plot_orbit(beamline_cfg, ax, plane='X'):
    s_values = []
    orbit_values = []
    BPM_names = []

    for name, itm in beamline_cfg["Beamline elements"].items():
        if "type" in itm and itm["type"] == "BPM":
            if "plane" in itm and itm["plane"] == plane:
                if "s" in itm and "value" in itm:
                    s_values.append(itm["s"])
                    orbit_values.append(itm["value"])
                    BPM_names.append(name)
    
    s_values = np.array(s_values)
    orbit_values = np.array(orbit_values)
    BPM_names = np.array(BPM_names)
    
    ids = np.argsort(s_values) # indicies sorted by s
    
    line, = ax.plot(s_values[ids], orbit_values[ids], "--", marker="o", lw=3)
    return line, BPM_names[ids]

def plot_correctors(beamline_cfg, ax, plane='X'):
    s_values=[]
    kick_values=[]
    corrector_names = []

    for name, itm in beamline_cfg["Beamline elements"].items():
        if "type" in itm and itm["type"] == "corrector":
            if "plane" in itm and itm["plane"] == plane:
                if "s" in itm and "kick" in itm:
                    corrector_names.append(name)
                    s = itm["s"]
                    s_values.append(s)
                    kick_values.append(itm["kick"])
                    if "max_kick" in itm:
                        ax.plot([s,s], [0,itm["max_kick"]], color="blue", alpha=0.4, lw=3)
                    if "min_kick" in itm:
                        ax.plot([s,s], [0,itm["min_kick"]], color="blue", alpha=0.4, lw=3)

    line, = ax.plot(s_values, kick_values, " ", marker="o",
                    markersize=8, markeredgewidth=1, markeredgecolor="black",
                    color="white", alpha=0.5)
    return line, corrector_names

def responses_to_corrector(element_names, corrector_name, responses_cfg):
    slopes = []
    for name in element_names:
        slope = 0
        response_id = f"{name} / {corrector_name}"
        if response_id in responses_cfg["response data"]:
            slope = responses_cfg["response data"][response_id]["slope"]
        slopes.append(slope)
    return np.array(slopes)

def on_scroll(event):
    global x_orbit_values, y_orbit_values, y_orbit_values
    global x_cor_values, y_cor_values
    
    mouse_x = event.xdata
    
    if not mouse_x or not event.inaxes: return
    
    if event.inaxes is axcx:
        line = cx_dots
        names_data = x_correctors
        cor_values = x_cor_values
    if event.inaxes is axcy:
        line = cy_dots
        names_data = y_correctors
        cor_values = y_cor_values
    if event.inaxes is axx:
        line = x_line
        names_data = x_BPMs
    if event.inaxes is axy:
        line = y_line
        names_data = y_BPMs
    
    s_data, value_data = line.get_data()

    i = np.argmin(np.abs(s_data-mouse_x))

    #print('you pressed', event.button, event.xdata, event.ydata)
    direction = -1.0
    if event.button == "up": direction = 1.0
  
    v_min, v_max =event.inaxes.get_ylim()
    step = direction*(v_max-v_min)/30.0
    
    element_name = names_data[i]
    element = beamline_cfg["Beamline elements"][element_name]
    if element["type"] == "corrector":
        #print(f"Apply correction: '{element_name}' change = {step:+.3f}")
        x_resp = responses_to_corrector(x_BPMs, element_name, responses_cfg)
        y_resp = responses_to_corrector(y_BPMs, element_name, responses_cfg)
        
        x_orbit_values = x_orbit_values + x_resp*step
        y_orbit_values = y_orbit_values + y_resp*step

        cor_values[i]+= step
        #value_data[i]+=step
        #line.set_data(s_data, value_data)
    
        update_plot()

    #fig.canvas.draw()
    #event.canvas.draw()
    
def update_plot():

    for line, values in zip([x_line, y_line, cx_dots, cy_dots],
                            [x_orbit_values, y_orbit_values, x_cor_values, y_cor_values]):
        
        s_data, _ = line.get_data()
        line.set_data(s_data, values)

    fig.canvas.draw()

if __name__ == '__main__':

    beamline_file='beamline.json'
    if len(sys.argv) > 1:
        beamline_file = sys.argv[1]
    if not os.path.exists(beamline_file):
        print(f"No {beamline_file} file to plot!")
        exit()
    
    responses_file='responses.json'
    if len(sys.argv) > 2:
        responses_file = sys.argv[2]
    if not os.path.exists(responses_file):
        print(f"No {responses_file} file to use!")
        exit()

    aperture_file='aperture.json'
    if len(sys.argv) > 3:
        aperture_file = sys.argv[3]

    with open(beamline_file, "r") as f:
        beamline_cfg = json.load(f)
        print(f"Beamline file: {beamline_file}")

    with open(responses_file, 'r') as f:
        responses_cfg = json.load(f)
        print(f"Response matrix file: {responses_file}")
        
    fig = plt.figure(figsize=(11,6))
    
    axx  = fig.add_subplot(411)
    axy  = fig.add_subplot(412, sharex=axx, sharey=axx)
    axcx = fig.add_subplot(413, sharex=axx)
    axcy = fig.add_subplot(414, sharex=axx, sharey=axcx)

    title = beamline_file

    axx.set_title(title)

    if os.path.exists(aperture_file):
        with open(aperture_file, "r") as f:
            aperture_cfg = json.load(f)

            plot_aperture(aperture_cfg, axx, plane="X")
            plot_aperture(aperture_cfg, axy, plane="Y")

    plot_beamline(beamline_cfg, axx,  show_names=False, box_h=5.0, alpha=0.2)
    plot_beamline(beamline_cfg, axy,  show_names=False, box_h=5.0, alpha=0.2)
    plot_beamline(beamline_cfg, axcx, show_names=False, box_h=2.0, alpha=0.2)
    plot_beamline(beamline_cfg, axcy, show_names=False, box_h=2.0, alpha=0.2)

    x_line, x_BPMs = plot_orbit(beamline_cfg, axx, plane='X')
    y_line, y_BPMs = plot_orbit(beamline_cfg, axy, plane='Y')
    
    #print(x_BPMs,y_BPMs)
    
    x_orbit_values = x_line.get_data()[1] # mm
    y_orbit_values = y_line.get_data()[1] # mm

    cx_dots, x_correctors = plot_correctors(beamline_cfg, axcx, plane='X')
    cy_dots, y_correctors = plot_correctors(beamline_cfg, axcy, plane='Y')
    
    x_cor_values = cx_dots.get_data()[1] # mrad
    y_cor_values = cy_dots.get_data()[1] # mrad
    
    #print(x_line.get_data())

    axx.set_ylabel("$x$ (mm)")

    axy.set_ylabel("$y$ (mm)")

    axcx.set_ylabel("x-corr. (mrad)")
    axcy.set_ylabel("y-corr. (mrad)")
    axcy.set_xlabel("$s$ (m)")

    fig.subplots_adjust(left=0.06, bottom=0.08, right=0.99, top=0.96, hspace=0)
    #cid = fig.canvas.mpl_connect('scroll_event', on_scroll)
    cid = axcx.figure.canvas.mpl_connect('scroll_event', on_scroll)

    plt.show()

