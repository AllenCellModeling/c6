#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Manage plotting of circles in a box"""

import functools
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation


def plot_cells(cells, ax=None):
    if ax is None:
        fig, ax = plt.subplots(1, 1)
        x, y = [c.loc[0] for c in cells], [c.loc[1] for c in cells]
        xlim = np.min(x) - 10, np.max(x) + 10
        ylim = np.min(y) - 10, np.max(y) + 10
        ax.set(xlim=xlim, ylim=ylim, aspect=1)
    for cell in cells:
        if hasattr(cell, "_patches") and cell._patches[0] in ax.patches:
            pe, pc = cell._patches
            pe.radius = cell.radius
            pe.xy = cell.loc
            pc.xy = cell.loc
        else:
            loc, r = cell.loc, cell.radius
            color = plt.cm.tab10(np.random.random())
            cp = plt.matplotlib.patches.CirclePolygon
            pe = ax.add_patch(cp(loc, r, edgecolor=color, fill=False))
            pc = ax.add_patch(cp(loc, 0.2 * r, facecolor=color))
            cell._patches = [pe, pc]
            cell.remove = pop_patch_dec(cell, ax.patches)
    return ax


def pop_patch_dec(cell, patches):
    """Decorate remove method so it kills that cell's patches"""
    remove_func = cell.remove

    @functools.wraps(remove_func)
    def pop_and_remove(*args, **kwargs):
        for patch in cell._patches:
            if patch in patches:
                patches.remove(patch)
        return remove_func(*args, **kwargs)

    return pop_and_remove


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
