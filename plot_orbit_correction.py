#!/usr/bin/env python3

import json, os, sys
import numpy as np
import matplotlib.pyplot as plt
from plot_beamline import plot_beamline
from plot_aperture import plot_aperture
from threading import Timer

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
    min_kicks = []
    max_kicks = []

    for name, itm in beamline_cfg["Beamline elements"].items():
        if "type" in itm and itm["type"] == "corrector":
            if "plane" in itm and itm["plane"] == plane:
                if "s" in itm and "kick" in itm:
                    corrector_names.append(name)
                    s = itm["s"]
                    s_values.append(s)
                    kick_values.append(itm["kick"])

                    if "min_kick" in itm:
                        min_kick = itm["min_kick"]
                        ax.plot([s,s], [0,min_kick], color="blue", alpha=0.3, lw=3)
                    else: min_kick = -1e10

                    if "max_kick" in itm:
                        max_kick = itm["max_kick"]
                        ax.plot([s,s], [0,max_kick], color="blue", alpha=0.3, lw=3)
                    else: max_kick = 1e10

                    max_kicks.append(max_kick)
                    min_kicks.append(min_kick)

    line, = ax.plot(s_values, kick_values, " ", marker="o",
                    markersize=8, markeredgewidth=1, markeredgecolor="black",
                    color="white", alpha=0.5)
    return line, corrector_names, min_kicks, max_kicks

def responses_to_corrector(element_names, corrector_name, responses_cfg):
    slopes = []
    for name in element_names:
        slope = 0
        response_id = f"{name} / {corrector_name}"
        if response_id in responses_cfg["response data"]:
            slope = responses_cfg["response data"][response_id]["slope"]
        slopes.append(slope)
    return np.array(slopes)

scroll_in_progress = False
N_scrolls_done = 0
def on_scroll(event):
    global scroll_in_progress
    global N_scrolls_done

    x = event.xdata
    if not x: return

    if event.button == "up":
        N_scrolls_done+=1
    else:
        N_scrolls_done-=1

    if not scroll_in_progress:
        scroll_in_progress = True
        t = Timer(0.2, move_dot, args=[event])
        t.start()

def move_dot(event):
    global scroll_in_progress, N_scrolls_done
    scroll_in_progress = False
    
    global x_orbit_values, y_orbit_values
    global x_cor_values, y_cor_values
    
    res = line_and_element_from_mouse_event(event)
    if not res: return
    line, i, element_name = res

    v_min, v_max =event.inaxes.get_ylim()
    step = N_scrolls_done*(v_max-v_min)/30.0
    N_scrolls_done = 0
    
    element = beamline_cfg["Beamline elements"][element_name]
    if element["type"] == "corrector":
        if element["plane"] == "X":
            kick_values = x_cor_values
        else:
            kick_values = y_cor_values
        
        kick = kick_values[i]

        if "max_kick" in element:
            if kick + step > element["max_kick"]:
                step = element["max_kick"] - kick
        if "min_kick" in element:
            if kick + step < element["min_kick"]:
                step = element["min_kick"] - kick
        
        x_resp = responses_to_corrector(x_BPMs, element_name, responses_cfg)
        y_resp = responses_to_corrector(y_BPMs, element_name, responses_cfg)
        
        x_orbit_values = x_orbit_values + x_resp*step
        y_orbit_values = y_orbit_values + y_resp*step

        kick_values[i]+= step
        
    elif element["type"] == "BPM":
        dX = x_orbit_values*0.0
        dY = y_orbit_values*0.0
        if element["plane"] == "X":
            dX[i] = step
        else:
            dY[i] = step
        
        dV_wish = np.concatenate( (dX,dY) )
                
        dkicks = ORM_inv*np.matrix(dV_wish).T
        
        kicks = np.concatenate((x_cor_values,y_cor_values))
        
        min_kicks = np.concatenate((x_min_kicks,y_min_kicks))
        max_kicks = np.concatenate((x_max_kicks,y_max_kicks))
        
        new_kicks = kicks + dkicks.A1
        
        new_kicks = [min((kick, max_kick)) for kick, max_kick in zip(new_kicks, max_kicks)]
        new_kicks = [max((kick, min_kick)) for kick, min_kick in zip(new_kicks, min_kicks)]
        new_kicks = np.array(new_kicks)

        dkicks = np.matrix(new_kicks-kicks).T
        
        dV = ORM*dkicks
        dV = dV.A1

        dkicks = dkicks.A1
        
        x_cor_values = x_cor_values + dkicks[:len(x_cor_values)]
        y_cor_values = y_cor_values + dkicks[len(x_cor_values):]
        
        x_orbit_values = x_orbit_values + dV[:len(x_orbit_values)]
        y_orbit_values = y_orbit_values + dV[len(x_orbit_values):]

    update_plot()


def get_ORM(BPMs, correctors):
    M = []
    for BPM in BPMs:
        line = []    
        for cor in correctors:
            key = f"{BPM} / {cor}"
            if key in responses_cfg["response data"]:
                line.append(responses_cfg["response data"][key]["slope"])
            else:
                line.append(0.0)
        M.append(line)
    
    return np.matrix(M)

def line_and_element_from_mouse_event(event):
    x = event.xdata
    if not x: return
    
    mouse_x = event.xdata
    if not mouse_x or not event.inaxes: return
    
    if event.inaxes is axcx:
        line = cx_dots
        names = x_correctors
    if event.inaxes is axcy:
        line = cy_dots
        names = y_correctors
    if event.inaxes is axx:
        line = x_line
        names = x_BPMs
    if event.inaxes is axy:
        line = y_line
        names = y_BPMs
    
    s_data, value_data = line.get_data()

    i = np.argmin(np.abs(s_data-mouse_x)) # nearest element index
    element_name = names[i]
    
    return line, i, element_name

def onmove(event):
    res = line_and_element_from_mouse_event(event)
    if not res: return
    line, i, element_name = res
    
    select_element(element_name, event.inaxes)

selected_element_name = ""
selected_element_txt = None
def select_element(name, ax):
    global selected_element_name, selected_element_txt
    if name == selected_element_name : return
    selected_element_name = name
    
    if selected_element_txt:
        selected_element_txt.set_text("")

    element = beamline_cfg["Beamline elements"][name]
    s = 0
    if "s" in element: s = element["s"]
    
    if ax is axcx:
        txt = txt_cx
    if ax is axcy:
        txt = txt_cy
    if ax is axx:
        txt = txt_x
    if ax is axy:
        txt = txt_y
    
    txt.set_text(name)
    txt.set_x(s)
    selected_element_txt = txt
    
    ax.figure.canvas.draw()


def update_plot():

    for line, values in zip([x_line, y_line, cx_dots, cy_dots],
                            [x_orbit_values, y_orbit_values,
                             x_cor_values, y_cor_values]):
        
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

    plot_beamline(beamline_cfg, axx,  show_names=False, box_h=10.0, alpha=0.2)
    plot_beamline(beamline_cfg, axy,  show_names=False, box_h=10.0, alpha=0.2)
    plot_beamline(beamline_cfg, axcx, show_names=False, box_h=1.0, alpha=0.2)
    plot_beamline(beamline_cfg, axcy, show_names=False, box_h=1.0, alpha=0.2)

    x_line, x_BPMs = plot_orbit(beamline_cfg, axx, plane='X')
    y_line, y_BPMs = plot_orbit(beamline_cfg, axy, plane='Y')

    txt_x = axx.text(0, 0, "", verticalalignment='center',
                     horizontalalignment='right', color='black',
                     fontsize=9, rotation='vertical', alpha=0.7)
    txt_y = axy.text(0, 0, "", verticalalignment='center',
                     horizontalalignment='right', color='black',
                     fontsize=9, rotation='vertical', alpha=0.7)
    txt_cx = axcx.text(0, 0, "", verticalalignment='center',
                     horizontalalignment='right', color='black',
                     fontsize=9, rotation='vertical', alpha=0.7)
    txt_cy = axcy.text(0, 0, "", verticalalignment='center',
                     horizontalalignment='right', color='black',
                     fontsize=9, rotation='vertical', alpha=0.7)

    x_orbit_values = x_line.get_data()[1] # mm
    y_orbit_values = y_line.get_data()[1] # mm

    cx_dots, x_correctors, x_min_kicks, x_max_kicks = \
        plot_correctors(beamline_cfg, axcx, plane='X')
    cy_dots, y_correctors, y_min_kicks, y_max_kicks = \
        plot_correctors(beamline_cfg, axcy, plane='Y')
    
    x_cor_values = cx_dots.get_data()[1] # mrad
    y_cor_values = cy_dots.get_data()[1] # mrad
    
    #print(x_line.get_data())

    if len(x_correctors) > 0:
        cor = x_correctors[0]
    elif len(y_correctors) > 0:
        cor = y_correctors[0]
    kick_units = beamline_cfg["Beamline elements"][cor]["kick_units"]

    axx.set_ylabel("$x$ (mm)")

    axy.set_ylabel("$y$ (mm)")

    axcx.set_ylabel(f"x-corr. ({kick_units})")
    axcy.set_ylabel(f"y-corr. ({kick_units})")
    axcy.set_xlabel("$s$ (m)")

    fig.subplots_adjust(left=0.06, bottom=0.08, right=0.99, top=0.96, hspace=0)
    #cid = fig.canvas.mpl_connect('scroll_event', on_scroll)
    cid = fig.canvas.mpl_connect('scroll_event', on_scroll)
    cid = fig.canvas.mpl_connect('motion_notify_event', onmove)

    # ORM/SVD calculations:
    
    ORM_BPMs = np.concatenate( (x_BPMs,y_BPMs) ) # all BPMs
    ORM_cors = np.concatenate( (x_correctors,y_correctors) ) # all correctors
    ORM = get_ORM(ORM_BPMs,ORM_cors) # ORM matrix
    
    print("ORM:")
    print(np.round(ORM, 1))
    
    U, s, Vh = np.linalg.svd(ORM, full_matrices=False)
    print("Non-zero singular values:")
    s_limit = 1e-5
    print(s[s>s_limit])
   
    N_singular_values_to_keep = int( 0.85 * len(s[s>s_limit]) )
    #N_singular_values_to_keep = 7
    print(f"N_singular_values_to_keep = {N_singular_values_to_keep} ({100*N_singular_values_to_keep/len(s):.0f}%)")
    s1 = s.copy()
    s1 = s1**-1
    s1[N_singular_values_to_keep:] = 0
    ORM_reduced = np.matrix(U)*np.matrix(np.diag(s1))*np.matrix(Vh)  
    #print("ORM_reduced:")
    #print(np.round(ORM_reduced))

    ORM_inv=Vh.T*np.diag(s1)*U.T
    
    print("Inverted ORM:")
    print(np.round(ORM_inv))

    plt.show()
