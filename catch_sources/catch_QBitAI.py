"""Fetcher for 量子位 (QBitAI) news."""

from __future__ import annotations

import datetime as _dt
from typing import List, Dict

import feedparser


def _parse_feed(url: str, days: int) -> List[Dict[str, str]]:
    try:
        feed = feedparser.parse(url)
    except Exception:
        return []

    cutoff = _dt.datetime.utcnow() - _dt.timedelta(days=days)
    items: List[Dict[str, str]] = []
    for entry in feed.entries:
        published = entry.get("published_parsed") or entry.get("updated_parsed")
        if published:
            dt = _dt.datetime(*published[:6])
            if dt < cutoff:
                continue
        items.append({"title": entry.get("title", ""), "link": entry.get("link", "")})
    return items


def catch_QBitAI(days: int = 1) -> List[Dict[str, str]]:
    """Return recent posts from 量子位 (QBitAI)."""
    url = "https://www.qbitai.com/feed"
    return _parse_feed(url, days)
