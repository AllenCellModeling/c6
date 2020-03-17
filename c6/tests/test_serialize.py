#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test encoding"""

import os
import json
import filecmp

import c6


def log_and_return(log_class, ext, dir, space):
    """Run a step, log it, return the filename"""
    # Find filenames and initialize log
    log = log_class(dir / "test_log")
    fn_test = log.fn
    assert fn_test.endswith(ext)
    # Create new log in way the test log was written
    log.log_space(space)
    space.step()
    log.log_space(space)
    log.close()
    return fn_test


def test_csvlog(tmp_path, small_space, data_dir):
    """Run a few steps and compare to a stored CSVLog"""
    # Find filenames and initialize log
    fn_orig = data_dir / "small.onestep.c6log"
    fn_test = log_and_return(c6.utils.serialize.CSVLog, "c6log", tmp_path, small_space)
    # Compare the two
    files_match = filecmp.cmp(fn_orig, fn_test, shallow=False)
    assert files_match, "c6logs don't match"


def test_simulariumlog(tmp_path, small_space, data_dir):
    """Run a few steps and compare to a stored SimulariumLog"""
    # Find filenames and initialize log
    fn_orig = data_dir / "small.onestep.simularium"
    fn_test = log_and_return(
        c6.utils.serialize.SimulariumLog, "simularium", tmp_path, small_space
    )
    # Compare the two
    with open(fn_orig, "r") as file_orig, open(fn_test, "r") as file_test:
        orig = json.load(file_orig)
        test = json.load(file_test)
    files_match = orig == test
    assert files_match, "simularium logs don't match"


def test_temp_names():
    """Temporary filenames should be a thing"""
    log_fn = (
        (c6.utils.serialize.CSVLog, "./temp.c6log"),
        (c6.utils.serialize.SimulariumLog, "./temp.simularium"),
    )
    for logclass, fn in log_fn:
        log = logclass()
        assert log.fn == fn, "Changed the temp fn?"
        log.close()
        os.remove(fn)


def test_write_starting_conditions(small_initial_condition_path, tmpdir):
    """Does re-writing a loaded space give the same starting conditions?"""
    fn_orig = small_initial_condition_path
    space = c6.utils.serialize.load_starting_conditions(fn_orig)
    # Rewrite these conditions
    fn_new = tmpdir / "smalltest"
    top_dict = dict(seed=1)
    fn_test = c6.utils.serialize.write_starting_conditions(fn_new, space, top_dict)
    # Load both with json, compare
    with open(fn_orig, "r") as file:
        raw_orig = json.load(file)
    with open(fn_test, "r") as file:
        raw_test = json.load(file)
    assert raw_orig == raw_test, "Rewritten small.intial.json not the same"
