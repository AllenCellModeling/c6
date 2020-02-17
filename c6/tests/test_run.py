#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test a run, the simplest of tests"""


def test_run(small_space):
    """Test loading a run and run it for a single step"""
    small_space.step()
