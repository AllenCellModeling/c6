#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Provide (de)serialization for the space and its cells"""

import json
import numpy as np

from .. import cell
from .. import space
from .encoding import JSONNumpyPandasEncoder


class CSVLog:
    def __init__(self, fn=None, header=None):
        """Log the output of a run as we go in a tidy CSV

        Parameters
        ----------
        fn: str
            filename to log output to, will have '.c6log' appended if not
            present
        header: list
            list of cell properties to log, will also log timestep from space
            default ["id", "x", "y", "dir_x", "dir_y", "speed", "radius", "age",
            "parent"]
        """
        # Create file
        if fn is None:
            fn = "./temp.c6log"
        fn = str(fn)  # convert if path
        if not fn.endswith(".c6log"):
            fn += ".c6log"
        self.fn = fn
        self.file = open(fn, "w")
        # Add t to header and save to file
        if header is None:
            header = [
                "id",
                "x",
                "y",
                "dir_x",
                "dir_y",
                "speed",
                "radius",
                "age",
                "parent",
            ]
        header = ["t"] + header
        self.file.write(",".join(header) + "\n")
        self.header = header

    @staticmethod
    def _cell_prop(cell, prop):
        """Deal with ``loc`` and ``dir`` being vectors"""
        if prop not in ("x", "y", "dir_x", "dir_y"):
            return cell.__dict__[prop]
        elif prop == "x":
            return cell.loc[0]
        elif prop == "y":
            return cell.loc[1]
        elif prop == "dir_x":
            return cell.dir[0]
        elif prop == "dir_y":
            return cell.dir[1]

    @staticmethod
    def _format(value):
        if type(value) is str:
            return value
        elif value is None:
            return "nan"
        else:
            return "{:12.6g}".format(value)

    def log_space(self, space):
        """Log cells in a space at a single timestep"""
        for c in space.cells:
            vals = [self._cell_prop(c, h) for h in self.header[1:]]
            vals.insert(0, space.timestep)
            self.file.write(",".join(self._format(v) for v in vals) + "\n")

    def close(self):
        if not self.file.closed:
            self.file.close()

    def __del__(self):
        self.close()


class SimulariumLog:
    def __init__(self, fn=None):
        """Log the output of the run to a Simularium compatible JSON format

        Parameters
        ----------
        fn: str
            filename to log output to, will have '.simularium' appended if not
            present
        """
        if fn is None:
            fn = "./temp.simularium"
        fn = str(fn)  # convert if path
        if not fn.endswith(".simularium"):
            fn += ".simularium"
        self.fn = fn
        self.file = open(fn, "w")
        self.file.writelines(["{", '"bundleData": ['])
        self._uuids = {}
        self._length = 1

    def _to_id(self, uuid):
        """Add the UUID if it is new, return ID uuid maps to"""
        if uuid not in self._uuids:
            self._uuids[uuid] = len(self._uuids) + 1
        return self._uuids[uuid]

    def _cell_to_vec(self, cell):
        "Transform a cell to a vector for inclusion in the data array"
        cell_id = self._to_id(cell.id)
        x, y, r = cell.loc[0], cell.loc[1], cell.radius
        return f"1000,{cell_id},{x:.4f},{y:.4f},0,0,0,0,{r:.4f},0"

    def log_space(self, space):
        """Log space at a timepoint"""
        assert not self.file.closed, "Log closed"
        cell_vecs = ",".join([self._cell_to_vec(cell) for cell in space.cells])
        if self._length != 1:
            self.file.write(",")
        self.file.writelines(
            [
                "{",
                f'"data": [{cell_vecs}],'
                f'"frameNumber": {self._length},'
                f'"msgType":1,'
                f'"time": {self._length}'
                "}",
            ]
        )
        self._length += 1

    def close(self):
        """Terminate the JSON and close the file"""
        if self.file.closed:
            return
        self.file.writelines(
            ["],", f'"bundleSize":{self._length-1},', '"bundleStart":0', "}"]
        )
        self.file.close()

    def __del__(self):
        """Close log before releasing memory"""
        self.close()


def load_starting_conditions(conditions_filename):
    """Load starting conditions into memory"""
    with open(conditions_filename, "r") as conditions_file:
        cond = json.load(conditions_file)
    # Seed RNG
    if "seed" in cond:
        np.random.seed(cond["seed"])
    # Create space
    new_space = space.Space()
    # Convert cell arrays to numpy
    for cell_d in cond["cells"]:
        for array_prop in ("loc", "dir"):
            if array_prop in cell_d:
                cell_d.update({array_prop: np.array(cell_d[array_prop])})
    # Read and load all cells
    cell_dicts = [{**cond["universal"], **cell_dict} for cell_dict in cond["cells"]]
    _ = [cell.Cell(new_space, **cd) for cd in cell_dicts]
    return new_space


def write_starting_conditions(
    conditions_filename,
    space,
    extra_top_level=dict(),
    universal_keys=None,
    cell_keys=None,
):
    """Write the current state of a space as a set of starting conditions"""
    # Create default universal and per-cell keys
    if universal_keys is None:
        universal_keys = (
            "growth_rate",
            "growth_var",
            "min_growth",
            "min_radius",
            "max_radius",
            "mitosis_50",
            "mitosis_steepness",
            "sensing",
            "influence_max",
            "influence_decay",
            "adhesion",
            "max_speed",
            "speed_dispersion",
            "repel_limit",
        )
    if cell_keys is None:
        cell_keys = ("loc", "dir", "speed", "radius", "age", "id")
    # Create dictionary serialized from space
    start_dict = extra_top_level
    start_dict["universal"] = {
        key: space.cells[0].__dict__[key] for key in universal_keys
    }
    start_dict["cells"] = [
        {key: cell.__dict__[key] for key in cell_keys} for cell in space.cells
    ]
    # Write out json
    conditions_filename = str(conditions_filename)  # convert if path
    if not conditions_filename.endswith(".initial.json"):
        conditions_filename += ".initial.json"
    with open(conditions_filename, "w") as conditions_file:
        json.dump(start_dict, conditions_file, cls=JSONNumpyPandasEncoder)
    return conditions_filename
