#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Manage plotting of circles in a box"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation


def plot_cells(cells, ax):
    if ax.patches == []:
        for cell in cells:
            loc, r = cell.loc, cell.radius
            color = plt.cm.hsv(np.random.random())
            cp = plt.matplotlib.patches.CirclePolygon
            pe = ax.add_patch(cp(loc, r, edgecolor=color, fill=False))
            pc = ax.add_patch(cp(loc, 0.2 * r, facecolor=color))
            cell._patches = [pe, pc]
    else:
        for cell in cells:
            pe, pc = cell._patches
            pe.radius = cell.radius
            pe.xy = cell.loc
            pc.xy = cell.loc


def animate(fig, ax, space, frames, callback=None):
    ax.axis("off")
    plt.subplots_adjust(0, 0, 1, 1)
    space.plot(ax)

    def animate_f(i):
        space.step()
        space.plot(ax)
        if callback is not None:
            callback(space)

    ani = matplotlib.animation.FuncAnimation(fig, animate_f, frames=frames)
    plt.close()  # prevent double show
    # html = ani.to_html5_video()
    return ani
