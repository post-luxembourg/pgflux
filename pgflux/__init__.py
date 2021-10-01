"""
Main package file
"""

try:
    import importlib.metadata as im
except ImportError:
    import importlib_metadata as im  # type: ignore


__version__ = im.version("pgflux")  # type: ignore
