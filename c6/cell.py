#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
import uuid
import numpy as np

from .utils.encoding import NumpyToCore


class Cell:
    """A circular cell that meanders about"""

    def __init__(self, space=None, loc=[0, 0], radius=2, **kwargs):
        """Create our circular cell.

        Parameters
        ==========
        space: c6.space
            a parent space, default is None
        loc: 2 tuple
            starting xy location of this cell, (default 0,0)
        radius: float
            cell size
        dir: 2 tuple
            initial direction of movement
        speed: float
            initial migratory speed
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
        # Set default values
        defaults = dict(
            space=space,
            loc=loc,
            radius=radius,
            dir=np.random.normal(size=2),  # gets normed below
            speed=np.abs(np.random.normal(0.1, 0.01)),
            age=0,
            growth_rate=0.1,
            growth_var=0.5,
            min_growth=0.01,
            min_radius=2.0,
            max_radius=3.5,
            mitosis_50=3.3,
            mitosis_steepness=0.1,
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
        # Add cell to space
        if space is not None:
            space.add_cell(self)

    def _to_serializeable_dict(self):
        """State of the cell, anything we can set"""
        return {key: NumpyToCore(self.__dict__[key]) for key in self._allowed}

    def _from_serializeable_dict(self, props):
        """Set values from the passed property dict"""
        self.__dict__.update((k, v) for k, v in props.items() if k in self._allowed)

    def _grow(self):
        """Get bigger according to current/min/max sizes, growth rate, and growth variance.
        """
        # Local copies of variables for readability
        r, r_min, r_max = self.radius, self.min_radius, self.max_radius
        g_rate, g_var = self.growth_rate, self.growth_var
        # Benavides: within size, grow, out of size, the law (of min growth)
        if r < r_min or r > r_max:
            return r + self.min_growth
        # Allow variability in growth rates
        if g_var is not None:
            g_rate *= np.random.normal(1.0, g_rate * g_var)
        # Calculate change and add to current radius
        change = g_rate * (r - r_min) * (1 - (r - r_min) / (r_max - r_min))
        change = np.clip(change, self.min_growth, np.inf)
        self.radius += change

    def _undergo_mitosis(self):
        """Should we undergo mitosis now?
        This is implicitly calculated relative to a rate per timestep.
        """
        m_50, steep = self.mitosis_50, self.mitosis_steepness
        p = 0.5 * (1 + np.tanh((self.radius - m_50) / steep))
        return np.random.rand() < p

    def _divide(self):
        """Undergo mitosis, creating two daughter cells"""
        # Conserve volume
        rad = self.radius / np.sqrt(2)
        # One daughter goes in direction parent was, one in opposite
        dirs = self.dir, -self.dir
        locs = [self.loc + dir * rad for dir in dirs]
        dicts = [
            dict(age=0, radius=rad, parent=self.id, dir=dir, loc=loc)
            for dir, loc in zip(dirs, locs)
        ]
        # Start with defaults from parent cell, but make daughters create new ids
        defaults = copy.copy(self.__dict__)
        defaults.pop("id")
        # Create new cells, delete the old
        for new_dict in dicts:
            defaults.update(new_dict)
            Cell(**defaults)
        self.remove()
        return

    def remove(self):
        """Remove self from simulation"""
        if self.space is not None:
            self.space.remove_cell(self)

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
        # Age and grow
        self.age += 1
        self._grow()
        if self._undergo_mitosis():
            self._divide()
            return  # daughter cells do next steps
        # Perturb the direction and speed
        self._steer()
        self._accelerate()
        # Calculate the current movement vector and move
        self.loc += self.speed * self.dir
        # Apply exclusion
        self._exclude()
