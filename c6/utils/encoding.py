#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Encoding for JSON etc"""

import json
import numpy as np


class JSONNumpyPandasEncoder(json.JSONEncoder):
    """Based on `RYMC's version
    <https://rymc.io/blog/2019/using-a-custom-jsonencoder-for-pandas-and-numpy/>`_
    """

    def default(self, obj_to_encode):
        """Pandas and Numpy have some specific types that we coerce to core
        Python types, for JSON generation purposes. This attempts to do so where
        applicable.
        """
        # Pandas dataframes have a to_json() method, so we'll check for that and
        # return it if so.
        if hasattr(obj_to_encode, "to_json"):
            return obj_to_encode.to_json()

        # Numpy objects report themselves oddly in error logs, but this generic
        # type mostly captures what we're after.
        if isinstance(obj_to_encode, np.generic):
            return obj_to_encode.item()

        # ndarray -> list, pretty straightforward.
        if isinstance(obj_to_encode, np.ndarray):
            return obj_to_encode.tolist()

        # If none of the above apply, we'll default back to the standard JSON encoding
        # routines and let it work normally.
        return super().default(obj_to_encode)


def NumpyToCore(obj_to_encode):
    """Convert numpy objects to standard python objects"""
    # Numpy objects report themselves oddly in error logs, but this generic
    # type mostly captures what we're after.
    if isinstance(obj_to_encode, np.generic):
        return obj_to_encode.item()

    # ndarray -> list, pretty straightforward.
    if isinstance(obj_to_encode, np.ndarray):
        return obj_to_encode.tolist()

    return obj_to_encode


def CoreToNumpy(obj_to_encode):
    """Convert lists back to numpy arrays"""
    if isinstance(obj_to_encode, list):
        return np.array(obj_to_encode)

    return obj_to_encode
