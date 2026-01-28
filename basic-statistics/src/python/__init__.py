"""
Basic Statistics Package

A comprehensive statistics library with Python and Fortran implementations.
"""

__version__ = "1.0.0"
__author__ = "Data Engineering Team"

from .descriptive import CentralTendency, Dispersion, Shape
from .probability import Distributions

__all__ = [
    "CentralTendency",
    "Dispersion",
    "Shape",
    "Distributions",
]
