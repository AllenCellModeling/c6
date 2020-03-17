#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import sklearn.neighbors

from .plot import plot_cells
from .utils.math import clip


class Space:
    """Space tracks the locations of cells within a space"""

    def __init__(self):
        self.cells = []
        self.timestep = 0

    def plot(self, ax=None):
        """Quick plot cells onto a provided matplotlib axis"""
        return plot_cells(self.cells, ax)

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
        for cell in np.random.permutation(self.cells):
            cell.step()
        self.timestep += 1

    def within(self, cell, rad):
        """Find all cells within a radius of a given cell.
        Must call `step` first to generate search tree.
        """
        near = self.tree.query_radius(cell.loc.reshape(1, -1), rad)
        return self._not_original_cell(near, cell)

    def nearest(self, cell, n=1):
        """The n nearest cells to a given cell
        Must call `step` first to generate search tree.
        """
        n = clip(n, 0, len(self.cells) - 1)
        near = self.tree.query(cell.loc.reshape(1, -1), n + 1, False)
        return self._not_original_cell(near, cell)

    def _not_original_cell(self, tree_results, cell):
        """Return the tree results that aren't the passed cell"""
        if tree_results is None:
            return []
        else:
            cells = [self.cells[i] for i in tree_results[0]]
            cells = [c for c in cells if c is not cell]
            return cells
