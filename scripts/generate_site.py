"""data/news.jsonからJinja2テンプレートを使って静的HTMLを生成する。"""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

JST = timezone(timedelta(hours=9))

DISPLAY_DAYS = 7

CATEGORY_CLASSES = {
    "事件・事故": "incident",
    "イベント・お知らせ": "event",
    "グルメ・新店舗": "gourmet",
    "その他": "other",
}

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "news.json"
OUTPUT_PATH = BASE_DIR / "docs" / "index.html"


def format_date_jst(iso_str):
    try:
        dt = datetime.fromisoformat(iso_str)
        return dt.astimezone(JST).strftime("%Y/%m/%d %H:%M")
    except (ValueError, TypeError):
        return ""


def category_class(category_name):
    return CATEGORY_CLASSES.get(category_name, "other")


def filter_recent(entries):
    cutoff = datetime.now(tz=timezone.utc) - timedelta(days=DISPLAY_DAYS)
    recent = []
    for entry in entries:
        pub = entry.get("published")
        if pub:
            try:
                if datetime.fromisoformat(pub) >= cutoff:
                    recent.append(entry)
            except ValueError:
                pass
    recent.sort(key=lambda e: e.get("published", ""), reverse=True)
    return recent


def main():
    if not DATA_PATH.exists():
        print("data/news.json が見つかりません。先に fetch_news.py を実行してください。")
        return

    with open(DATA_PATH, encoding="utf-8") as f:
        entries = json.load(f)

    recent = filter_recent(entries)

    env = Environment(
        loader=FileSystemLoader(str(BASE_DIR / "templates")),
        autoescape=True,
    )
    env.filters["format_date_jst"] = format_date_jst
    env.filters["category_class"] = category_class

    template = env.get_template("index.html")

    categories = ["すべて", "事件・事故", "イベント・お知らせ", "グルメ・新店舗", "その他"]
    now_jst = datetime.now(tz=timezone.utc).astimezone(JST)

    html = template.render(
        entries=recent,
        categories=categories,
        updated_at=now_jst.strftime("%Y/%m/%d %H:%M"),
        total_count=len(recent),
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(html, encoding="utf-8")
    print(f"生成: {len(recent)} 件のニュースで docs/index.html を作成")


if __name__ == "__main__":
    main()
