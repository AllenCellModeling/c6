#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Configuration for tests"""

from c6.utils.serialize import load_starting_conditions
from pathlib import Path

import pytest


# Set up immutable or globally needed parameters
DATADIR = Path(__file__).parent.parent / "data"
INITPATH = DATADIR / "small.initial.json"
SPACE = load_starting_conditions(INITPATH)


@pytest.fixture
def data_dir() -> Path:
    return DATADIR


@pytest.fixture
def small_initial_condition_path() -> Path:
    return INITPATH


@pytest.fixture
def small_space(small_initial_condition_path):
    return load_starting_conditions(small_initial_condition_path)


@pytest.fixture(params=SPACE.cells)
def cell(request):
    """Tests accepting `cell` will be called with all cells in `SPACE`"""
    return request.param
