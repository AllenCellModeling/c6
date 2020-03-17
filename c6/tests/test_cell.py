#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test the cell"""


import numpy as np
import copy

import c6


def test_solo_cell():
    """Create and let a cell, without a space, walk through some steps"""
    cell = c6.Cell(loc=[1, 1])
    for i in range(10):
        cell.step()


def test_two_cell_repel():
    """Create and let a cell, without a space, walk through some steps"""
    space = c6.Space()
    c6.Cell(space, [0, 0], 1)
    c6.Cell(space, [0, 1.9], 1)
    for i in range(2):
        space.step()


def test_encoding_round_trip(cell):
    """Does everything come through a round trip?"""
    orig = copy.copy(cell.__dict__)
    cell._from_serializeable_dict(cell._to_serializeable_dict())
    round_trip = cell.__dict__
    for key in cell._allowed:
        if type(orig[key]) == np.ndarray or type(orig[key]) == list:
            assert all(orig[key] == round_trip[key])
        else:
            assert orig[key] == round_trip[key]
