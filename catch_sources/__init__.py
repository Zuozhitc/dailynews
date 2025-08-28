"""Utility catchers for various news sources.

Each module within this package exposes a ``catch_<source>`` function
that returns a list of news items.  A news item is represented as a
dictionary containing at least ``title`` and ``link`` keys.  The
functions are designed to be resilient: if fetching or parsing fails,
they simply return an empty list so that callers can continue
processing other sources.
"""

from .catch_36kr import catch_36kr
from .catch_IThome import catch_IThome
from .catch_JQZX import catch_JQZX
from .catch_QBitAI import catch_QBitAI
from .catch_theverge import catch_theverge
from . import catch_ProductHunt
from .catch_ProductHunt import catch_producthunt

__all__ = [
    "catch_36kr",
    "catch_IThome",
    "catch_JQZX",
    "catch_QBitAI",
    "catch_theverge",
    "catch_ProductHunt",
    "catch_producthunt",
]
