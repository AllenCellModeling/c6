#!/usr/bin/env python
# -*- coding: utf-8 -*-

import uuid
import numpy as np

from .utils.encoding import NumpyToCore


class Cell:
    """A circular cell that meanders about"""

    def __init__(self, space=None, loc=[0, 0], **kwargs):
        """Create our circular cell.

        Parameters
        ==========
        space: c6.space
            a parent space, default is None
        loc: 2 tuple
            starting xy location of this cell, (default 0,0)
        dir: 2 tuple
            initial direction of movement
        speed: float
            initial migratory speed
        radius: float
            cell size
        age: int
            how many timesteps old this cell is
        sensing: float
            distance across which we sense other cells
        influence_max: float
            level of influence max value
        influence_decay: float
            level of influence `exponential decay`_ constant
        adhesion: float
            well depth for LJP
        direction_dispersion: float
            how strong our directional memory is
        repel_limit: float
            how far a cell can move to avoid overlap, tuned along with adhesion to
            avoid oscillation
        id: int or str
            unique name of this cell, defaults to first 6 of a UUID
        parent: int or str or None
            id of parent of this cell, if any

        .. _exponential decay: http://mathworld.wolfram.com/ExponentialDecay.html
        """
        if space is not None:
            space.cells.append(self)
        self.space = space
        # Set default values
        defaults = dict(
            loc=loc,
            dir=np.random.normal(size=2),  # will get normed on first steer
            speed=np.abs(np.random.normal(0.1, 0.01)),
            radius=2,
            age=0,
            sensing=5,
            influence_max=10,
            influence_decay=2,
            adhesion=0.001,
            max_speed=1.0,
            speed_dispersion=0.03,
            direction_dispersion=0.1,
            repel_limit=0.1,
            id=uuid.uuid4().hex[:6],
            parent=None,
        )
        defaults["dir"] /= np.linalg.norm(defaults["dir"])
        # Update the dictionary
        self._allowed = list(defaults.keys())
        defaults.update(kwargs)
        self.__dict__.update((k, v) for k, v in defaults.items() if k in self._allowed)

    def _to_serializeable_dict(self):
        """State of the cell, anything we can set"""
        return {key: NumpyToCore(self.__dict__[key]) for key in self._allowed}

    def _from_serializeable_dict(self, props):
        """Set values from the passed property dict"""
        self.__dict__.update((k, v) for k, v in props.items() if k in self._allowed)

    def _nearby_cells(self, dist):
        """Find cells within dist of this cell's location"""
        if self.space is not None:
            return self.space.within(self, dist)
        else:
            return []

    def _steer(self):
        """Randomly migrate, subject to the influence from nearby cells"""
        # Perturb the direction a bit
        self.dir += np.random.normal(0, self.direction_dispersion, 2)
        self.dir /= np.linalg.norm(self.dir)
        # Find vectors to nearby cells
        others = self._nearby_cells(self.sensing)
        alter_by = np.zeros(2)
        for oc in others:
            vec = oc.loc - self.loc
            center_dist = np.linalg.norm(vec)
            surface_dist = center_dist - (self.radius + oc.radius)
            i_max, i_decay = self.influence_max, self.influence_decay
            influence = i_max * np.exp(-surface_dist * i_decay)
            influence = np.clip(influence, 0, i_max)  # slight overlap
            alter_by += vec / center_dist * influence
        self.dir += alter_by
        self.dir /= np.linalg.norm(self.dir)

    def _accelerate(self):
        """Perturb the speed a bit"""
        self.speed += np.random.normal(0, self.speed_dispersion)
        self.speed = np.clip(self.speed, 0, self.max_speed)

    def _ljf(self, dist):
        """Lennard-Jones force (derivative of Lennard-Jones potential"""
        if dist <= 0.0:
            dist = np.finfo(np.float16).eps
        e, rm, r = self.adhesion, self.radius, dist
        return 12 * e * (rm ** 6 / r ** 7 - rm ** 12 / r ** 13)

    def _repel(self, other_cell):
        """Two cells shouldn't overlap"""
        vec = other_cell.loc - self.loc
        dist = np.linalg.norm(vec)
        mag = other_cell._ljf(dist - self.radius) + self._ljf(dist - other_cell.radius)
        f_vec = np.clip(mag, -self.repel_limit, self.repel_limit) * vec / dist
        self.loc += f_vec
        if mag > self.repel_limit or mag < -self.repel_limit:
            self._repel(other_cell)

    def _exclude(self):
        """Find nearby cells and make them not overlap"""
        # Find vectors to nearby cells
        others = self._nearby_cells(self.sensing)
        # Repel them, in a random order
        for other in np.random.permutation(others):
            self._repel(other)

    def step(self):
        # Perturb the direction and speed
        self._steer()
        self._accelerate()
        # Calculate the current movement vector and move
        self.loc += self.speed * self.dir
        # Apply exclusion
        self._exclude()
        # Age
        self.age += 1
