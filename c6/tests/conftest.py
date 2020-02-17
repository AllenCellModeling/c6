#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Configuration for tests"""

from c6.utils.serialize import load_starting_conditions
from pathlib import Path

import pytest


@pytest.fixture
def data_dir() -> Path:
    return Path(__file__).parent / "data"


@pytest.fixture
def small_space(data_dir):
    return load_starting_conditions(data_dir / "small.initial.json")
