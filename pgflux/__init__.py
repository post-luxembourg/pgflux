"""
Main package file
"""

try:  # pragma: no cover
    import importlib.metadata as im
except ImportError:  # pragma: no cover
    import importlib_metadata as im  # type: ignore


__version__ = im.version("pgflux")  # type: ignore
