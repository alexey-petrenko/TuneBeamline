#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle
from matplotlib.widgets import Button
from threading import Timer


class OrbitCorMatPlot:
    def __init__(self, get_vals_from_consys, send_vals_to_consys, **kwargs):
        super().__init__()
        # to be done
        aper = kwargs.get('aper')
        bline = kwargs.get('bline')
        self.s = self.get_pos(bline)

        # matplotlib binding
        ################################################################################################################
        self.txt: dict = {}
        self.fig, self.axides = plt.subplots(6, 1, sharex='col', sharey='col')

        for axis in range(len(self.axides) - 2):
            self.plot_aper(aper, self.axides[axis])
            self.plot_beamline(bline, self.axides[axis], 10)
            self.txt[id(self.axides[axis])] = self.axides[axis].text(0, 0, "", verticalalignment='center',
                                                                     horizontalalignment='right', color='black',
                                                                     fontsize=9, rotation='vertical', alpha=0.7)

        btn_get = Button(self.axides[4], 'Get Values')
        btn_get.on_clicked(get_vals_from_consys)
        btn_set = Button(self.axides[5], 'Set Values')
        btn_set.on_clicked(send_vals_to_consys)

        # self.names_id = {id(self.axides[0]): self.bpm_col.names_x, id(self.axides[1]): self.bpm_col.names_y,
        #                  id(self.axides[2]): self.cor_col.names_x, id(self.axides[3]): self.cor_col.names_y}
        # self.s_id = {id(self.axides[0]): self.bpm_col.s_x, id(self.axides[1]): self.bpm_col.s_y,
        #              id(self.axides[2]): self.cor_col.s_x, id(self.axides[3]): self.cor_col.s_y}

        # self.plot_orbit()
        # self.plot_correctors()

        self.scroll_in_progress = False
        self.N_scrolls_done = 0
        self.selected_name: str = ' '
        self.selected_txt = self.txt[id(self.axides[0])]

        self.fig.canvas.mpl_connect('scroll_event', self.on_scroll)
        self.fig.canvas.mpl_connect('motion_notify_event', self.onmove)

        self.fig.subplots_adjust(left=0.06, bottom=0.08, right=0.99, top=0.96, hspace=0)
        plt.show()
        ################################################################################################################

    def get_pos(self, bline: dict) -> dict:
        s_s = {}
        coll = {}
        i = 0
        for elem in ['BPM', 'corrector']:
            for plane in ['X', 'Y']:
                for elem_name, elem_par in bline['Beamline elements'].items():
                    if elem_par['type'] == elem and elem_par['plane'] == plane:
                        coll[elem_name] = elem_par

                s = np.array([elem['s'] for name, elem in coll.items() if elem['plane'] == plane])
                coll = {}
                ind = np.argsort(s)
                s_s[i] = s[ind]
                i += 1
        return s_s

    def plot_aper(self, aper, axis):
        axis.plot(aper[0], aper[1], lw=2, c='black', alpha=0.4)

    def plot_beamline(self, bline, axis, h):
        color = {'BEND': 'green', 'QUAD': 'red', 'BPM': 'black', 'corrector': 'orange'}
        for elem_name, elem_par in bline['Beamline elements'].items():
            s = elem_par['s']
            l = elem_par['L']
            axis.add_patch(Rectangle((s - l/2, 0-h/2), l, h, facecolor=color[elem_par['type']], alpha=0.5))

    def plot_orbit(self, orbit_x=np.zeros(16,), orbit_y=np.zeros(16,)):
        self.axides[0].plot(self.s[0], orbit_x, "--", marker="o", lw=3)
        self.axides[1].plot(self.s[1], orbit_y, "--", marker="o", lw=3)

    def plot_correctors(self, x_kick=np.zeros(19,), y_kick=np.zeros(17,)):
        self.axides[2].plot(self.s[2], x_kick, " ", marker="o",
                            markersize=8, markeredgewidth=1, markeredgecolor="black", color="white", alpha=0.5)
        self.axides[3].plot(self.s[3], y_kick, " ", marker="o",
                            markersize=8, markeredgewidth=1, markeredgecolor="black", color="white", alpha=0.5)

    def on_scroll(self, event):
        x = event.xdata
        if not x:
            return
        if event.button == "up":
            self.N_scrolls_done += 1
        else:
            self.N_scrolls_done -= 1

        if not self.scroll_in_progress:
            self.scroll_in_progress = True
            t = Timer(0.2, self.move_dot, args=[event])
            t.start()

    # def move_dot(self, event):
    #     self.scroll_in_progress = False
    #
    #     name, s = self.element_from_mouse_event(event)
    #     if not name:
    #         return
    #
    #     v_min, v_max = event.inaxes.get_ylim()
    #     step = self.N_scrolls_done * (v_max - v_min) / 30.0
    #     self.N_scrolls_done = 0
    #
    #     element = beamline_cfg["Beamline elements"][element_name]
    #     if element["type"] == "corrector":
    #         if element["plane"] == "X":
    #             kick_values = x_cor_values
    #         else:
    #             kick_values = y_cor_values
    #
    #         kick = kick_values[i]
    #
    #         if "max_kick" in element:
    #             if kick + step > element["max_kick"]:
    #                 step = element["max_kick"] - kick
    #         if "min_kick" in element:
    #             if kick + step < element["min_kick"]:
    #                 step = element["min_kick"] - kick
    #
    #         x_resp = responses_to_corrector(x_BPMs, element_name, responses_cfg)
    #         y_resp = responses_to_corrector(y_BPMs, element_name, responses_cfg)
    #
    #         x_orbit_values = x_orbit_values + x_resp * step
    #         y_orbit_values = y_orbit_values + y_resp * step
    #
    #         kick_values[i] += step
    #
    #     elif element["type"] == "BPM":
    #         dX = x_orbit_values * 0.0
    #         dY = y_orbit_values * 0.0
    #         if element["plane"] == "X":
    #             dX[i] = step
    #         else:
    #             dY[i] = step
    #
    #         dV_wish = np.concatenate((dX, dY))
    #
    #         dkicks = ORM_inv * np.matrix(dV_wish).T
    #
    #         kicks = np.concatenate((x_cor_values, y_cor_values))
    #
    #         min_kicks = np.concatenate((x_min_kicks, y_min_kicks))
    #         max_kicks = np.concatenate((x_max_kicks, y_max_kicks))
    #
    #         new_kicks = kicks + dkicks.A1
    #
    #         new_kicks = [min((kick, max_kick)) for kick, max_kick in zip(new_kicks, max_kicks)]
    #         new_kicks = [max((kick, min_kick)) for kick, min_kick in zip(new_kicks, min_kicks)]
    #         new_kicks = np.array(new_kicks)
    #
    #         dkicks = np.matrix(new_kicks - kicks).T
    #
    #         dV = ORM * dkicks
    #         dV = dV.A1
    #
    #         dkicks = dkicks.A1
    #
    #         x_cor_values = x_cor_values + dkicks[:len(x_cor_values)]
    #         y_cor_values = y_cor_values + dkicks[len(x_cor_values):]
    #
    #         x_orbit_values = x_orbit_values + dV[:len(x_orbit_values)]
    #         y_orbit_values = y_orbit_values + dV[len(x_orbit_values):]
    #
    #     update_plot()

    def onmove(self, event):
        name, s = self.element_from_mouse_event(event)
        if not name:
            return
        self.select_element(name, s, event.inaxes)

    def element_from_mouse_event(self, event):
        x = event.xdata
        if not x:
            return False, False
        mouse_x = event.xdata
        if not mouse_x or not event.inaxes:
            return False, False
        try:
            i = np.argmin(np.abs(self.s_id[id(event.inaxes)] - mouse_x))  # nearest element index
        except KeyError:
            return False, False

        return self.names_id[id(event.inaxes)][i], self.s_id[id(event.inaxes)][i]

    def select_element(self, name, s, ax):
        if name == self.selected_name:
            return
        self.selected_name = name

        if self.selected_txt:
            self.selected_txt.set_text("")

        txt = self.txt[id(ax)]
        txt.set_text(name)
        txt.set_x(s)
        self.selected_txt = txt

        ax.figure.canvas.draw()
