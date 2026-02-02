"""
🎵 strands-strudel - AI-powered live coding music generation

A Strands Agents tool that generates and manipulates Strudel patterns
for algorithmic music composition.
"""

from .strudel import strudel

try:
    from ._version import __version__
except ImportError:
    __version__ = "0.0.0"

__all__ = ["strudel"]
