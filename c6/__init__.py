# -*- coding: utf-8 -*-

"""Top-level package for Circular Center-based Cell Colony Creation and Clustering."""

__author__ = "C David Williams"
__email__ = "cdavew@alleninstitute.org"
# Do not edit this string manually, always use bumpversion
# Details in CONTRIBUTING.md
__version__ = "0.1.0"


def get_module_version():
    return __version__


from .example import Example  # noqa: F401
from .space import Space
from .cell import Cell
