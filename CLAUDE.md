# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

葛西エリア（江戸川区）のニュースをGoogle News RSSから毎朝自動収集し、カテゴリ別に表示する個人用静的ニュースサイト。GitHub Actions + GitHub Pagesで完全無料運用。

仕様の詳細は `kasai-news-spec.md` を参照。

## 技術スタック

- **ニュース取得・分類・サイト生成**: Python 3.12（feedparser, jinja2）
- **フロントエンド**: 静的HTML/CSS/JS（外部ライブラリなし、Jinja2テンプレートから生成）
- **自動実行**: GitHub Actions（UTC 22:00 = JST 07:00 の日次cron）
- **ホスティング**: GitHub Pages（`docs/` フォルダから配信）

## コマンド

```bash
# 依存パッケージのインストール
pip install -r requirements.txt

# ニュースの取得→分類→サイト生成（この順序で実行）
python scripts/fetch_news.py
python scripts/categorize.py
python scripts/generate_site.py

# 手動でGitHub Actionsワークフローを実行
gh workflow run update-news.yml
```

## アーキテクチャ

3段階のパイプラインで動作する:

1. **`scripts/fetch_news.py`** — Google News RSSから複数キーワード（`葛西 江戸川区`, `西葛西`, `葛西臨海公園`）でニュースを取得し、`data/news.json` に蓄積（URLで重複排除、30日分保持）
2. **`scripts/categorize.py`** — キーワードマッチングで4カテゴリに自動分類: 事件・事故 / イベント・お知らせ / グルメ・新店舗 / その他
3. **`scripts/generate_site.py`** — `templates/index.html`（Jinja2）と `data/news.json` から直近7日分のニュースを `docs/index.html` として生成

## 重要な設計方針

- **セキュリティ**: RSSから取得したテキストは必ずHTMLエスケープする。Jinja2は `autoescape=True` を明示設定
- **プライバシー**: サイトに個人情報を表示しない。`robots.txt` と `noindex` メタタグで検索エンジンを拒否。gitコミッターはbot名を使用
- **フロントエンド**: スマホファーストのレスポンシブデザイン、ライトモードのみ（暖色系オレンジ・ベージュ基調）、外部ライブラリ不使用
- **API Key不要**: Google News RSSは公開フィードのため認証不要

## 主要ディレクトリ

- `scripts/` — Pythonパイプラインスクリプト
- `templates/` — Jinja2テンプレート
- `docs/` — GitHub Pagesで配信される生成済みファイル（直接編集しない）
- `data/` — ニュースデータJSON（自動生成）
- `.github/workflows/` — GitHub Actions定義
