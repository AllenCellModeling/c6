#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math


def clip(number, minimum, maximum):
    """Clip a number to be between the minimum and maximum"""
    return max(min(number, maximum), minimum)


def norm(p):
    """2 norm, distance from a point to the origin on the plane"""
    return math.sqrt(p[0] ** 2 + p[1] ** 2)
