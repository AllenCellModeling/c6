# -*- coding: utf-8 -*-

"""Top-level package for Circular Center-based Cell Colony Creation and Clustering."""

__author__ = "C David Williams"
__email__ = "cdavew@alleninstitute.org"
# Do not edit this string manually, always use bumpversion
# Details in CONTRIBUTING.md
__version__ = "0.4.0"


def get_module_version():
    return __version__


from .space import Space  # noqa: F401,E402
from .cell import Cell  # noqa: F401,E402
