#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import sklearn.neighbors

from .plot import plot_cells, animate


class Space:
    """Space tracks the locations of cells within a space"""

    def __init__(self):
        self.cells = []
        self.timestep = 0

    def plot(self, ax):
        """Quick plot cells onto a provided matplotlib axis"""
        plot_cells(self.cells, ax)

    def add_cell(self, cell):
        """Add cell and regenerate distance tree"""
        self.cells.append(cell)
        self._generate_distance_map()

    def remove_cell(self, cell):
        """Remove cell and regenerate distance tree"""
        self.cells.remove(cell)
        self._generate_distance_map()

    def _generate_distance_map(self):
        locs = np.array([cell.loc for cell in self.cells])
        self.tree = sklearn.neighbors.KDTree(locs)

    def step(self):
        """Tell every cell to go through one time step"""
        self._generate_distance_map()
        for cell in self.cells:
            cell.step()
        self.timestep += 1

    def within(self, cell, rad):
        """Find all cells within a radius of a given cell.
        Must call `step` first to generate search tree.
        """
        near = self.tree.query_radius(cell.loc.reshape(1, -1), rad)
        if near is None:
            return []
        else:
            cells = [self.cells[i] for i in near[0]]
            cells = [c for c in cells if c is not cell]
            return cells
