# kasai-news

葛西エリア（江戸川区）のニュースを毎朝自動収集し、カテゴリ別に表示する個人用静的ニュースサイト。

## 仕組み

Google News RSSから葛西関連のキーワードでニュースを取得し、カテゴリ分類して静的HTMLを生成します。GitHub Actionsで毎朝JST 7:00に自動実行され、GitHub Pagesで配信されます。

## ローカル実行

```bash
pip install -r requirements.txt
python scripts/fetch_news.py
python scripts/categorize.py
python scripts/generate_site.py
```

生成されたサイトは `docs/index.html` で確認できます。

## カテゴリ

- 事件・事故
- イベント・お知らせ
- グルメ・新店舗
- その他
