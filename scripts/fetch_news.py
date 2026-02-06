"""Google News RSSから葛西エリアのニュースを取得し、data/news.jsonに蓄積する。"""

import calendar
import json
import urllib.parse
from datetime import datetime, timedelta, timezone
from pathlib import Path

import feedparser

KEYWORDS = [
    "葛西 江戸川区",
    "西葛西",
    "葛西臨海公園",
]

BASE_URL = "https://news.google.com/rss/search?q={query}&hl=ja&gl=JP&ceid=JP:ja"

RETENTION_DAYS = 30

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "news.json"


def build_urls():
    return [BASE_URL.format(query=urllib.parse.quote(kw)) for kw in KEYWORDS]


def fetch_feed(url):
    try:
        feed = feedparser.parse(url)
        if feed.bozo:
            print(f"Warning: フィード解析に問題あり {url}: {feed.bozo_exception}")
        return feed.entries
    except Exception as e:
        print(f"Error: フィード取得失敗 {url}: {e}")
        return []


def parse_entry(entry):
    published_utc = None
    if entry.get("published_parsed"):
        utc_ts = calendar.timegm(entry.published_parsed)
        published_utc = datetime.fromtimestamp(utc_ts, tz=timezone.utc)

    source = ""
    if entry.get("source"):
        source = entry.source.get("title", "")

    return {
        "title": entry.get("title", ""),
        "link": entry.get("link", ""),
        "source": source,
        "published": published_utc.isoformat() if published_utc else "",
        "description": entry.get("summary", ""),
        "category": "",
        "fetched_at": datetime.now(tz=timezone.utc).isoformat(),
    }


def load_existing(path):
    if path.exists():
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            print(f"Warning: 既存データの読み込み失敗: {e}")
    return []


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def prune_old_entries(entries):
    cutoff = datetime.now(tz=timezone.utc) - timedelta(days=RETENTION_DAYS)
    result = []
    for entry in entries:
        pub = entry.get("published")
        if pub:
            try:
                if datetime.fromisoformat(pub) >= cutoff:
                    result.append(entry)
                    continue
            except ValueError:
                pass
        fetched = entry.get("fetched_at")
        if fetched:
            try:
                if datetime.fromisoformat(fetched) >= cutoff:
                    result.append(entry)
                    continue
            except ValueError:
                pass
    return result


def main():
    existing = load_existing(DATA_PATH)
    existing_urls = {e["link"] for e in existing if e.get("link")}

    new_entries = []
    for url in build_urls():
        entries = fetch_feed(url)
        for entry in entries:
            parsed = parse_entry(entry)
            if parsed["link"] and parsed["link"] not in existing_urls:
                new_entries.append(parsed)
                existing_urls.add(parsed["link"])

    all_entries = existing + new_entries
    all_entries = prune_old_entries(all_entries)

    save_json(DATA_PATH, all_entries)
    print(f"取得: 新規 {len(new_entries)} 件 / 合計 {len(all_entries)} 件")


if __name__ == "__main__":
    main()
