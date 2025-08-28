"""Fetcher for 机器之心 (Machine Heart) news."""

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


def catch_JQZX(days: int = 1) -> List[Dict[str, str]]:
    """Return recent posts from 机器之心."""
    url = "https://www.jiqizhixin.com/rss"
    return _parse_feed(url, days)
