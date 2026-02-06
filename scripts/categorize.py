"""data/news.jsonのニュースをキーワードマッチングでカテゴリ分類する。"""

import json
from pathlib import Path

CATEGORIES = {
    "事件・事故": ["逮捕", "事故", "火災", "事件", "容疑", "死亡", "被害", "犯罪", "詐欺", "窃盗", "暴行"],
    "イベント・お知らせ": ["祭り", "イベント", "開催", "募集", "教室", "講座", "ボランティア", "選挙", "行政", "区議"],
    "グルメ・新店舗": ["オープン", "開店", "閉店", "ランチ", "カフェ", "レストラン", "ラーメン", "新店", "グルメ"],
}

DEFAULT_CATEGORY = "その他"

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "news.json"


def categorize(entry):
    text = entry.get("title", "") + " " + entry.get("description", "")
    for category, keywords in CATEGORIES.items():
        for keyword in keywords:
            if keyword in text:
                return category
    return DEFAULT_CATEGORY


def main():
    if not DATA_PATH.exists():
        print("data/news.json が見つかりません。先に fetch_news.py を実行してください。")
        return

    with open(DATA_PATH, encoding="utf-8") as f:
        entries = json.load(f)

    categorized_count = 0
    for entry in entries:
        if not entry.get("category"):
            entry["category"] = categorize(entry)
            categorized_count += 1

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)

    print(f"分類: {categorized_count} 件を新規分類 / 合計 {len(entries)} 件")


if __name__ == "__main__":
    main()
