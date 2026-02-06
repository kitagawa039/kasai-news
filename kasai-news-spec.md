# 葛西ニュースサイト 仕様書

> この仕様書をClaude Codeに渡して実装してもらうためのドキュメントです。

---

## 1. プロジェクト概要

葛西エリア（江戸川区）に関連するニュースを毎朝自動で収集し、カテゴリ別に一覧表示する個人用の静的ニュースサイト。

## 2. 要件

- ニュースソース: Google News RSSフィード（キーワード検索ベース）
- 更新頻度: 毎朝1回（GitHub Actionsで自動実行）
- カテゴリ: 事件・事故 / イベント・お知らせ / グルメ・新店舗 / その他
- ホスティング: GitHub Pages（無料）
- 月額コスト: 0円

## 3. 技術スタック

| 項目 | 技術 |
|------|------|
| ニュース取得・分類 | Python 3（feedparser, jinja2） |
| フロントエンド | 静的HTML/CSS/JS（Pythonで生成） |
| 自動実行 | GitHub Actions（cron） |
| ホスティング | GitHub Pages |
| バージョン管理 | Git / GitHub |

## 4. ファイル構成

```
kasai-news/
├── .github/
│   └── workflows/
│       └── update-news.yml      # GitHub Actions 定時実行設定
├── scripts/
│   ├── fetch_news.py            # ニュース取得スクリプト
│   ├── categorize.py            # カテゴリ分類ロジック
│   └── generate_site.py         # 静的HTML生成
├── templates/
│   └── index.html               # Jinja2テンプレート
├── docs/                        # GitHub Pages公開ディレクトリ
│   ├── index.html               # 生成されたサイト本体
│   └── style.css                # スタイルシート
├── data/
│   └── news.json                # 取得したニュースデータ（履歴）
├── requirements.txt             # Python依存パッケージ
└── README.md
```

## 5. ニュース取得仕様

### 5.1 検索キーワード

Google News RSSから以下のキーワードで取得する（OR検索で網羅性を上げる）:

- `葛西 江戸川区`
- `西葛西`
- `葛西臨海公園`

RSSフィードURL例:
```
https://news.google.com/rss/search?q=葛西+江戸川区&hl=ja&gl=JP&ceid=JP:ja
```

### 5.2 カテゴリ分類ロジック

キーワードマッチングで自動分類する。複数カテゴリに該当する場合は最初にマッチしたものを採用。

```python
CATEGORIES = {
    "事件・事故": ["逮捕", "事故", "火災", "事件", "容疑", "死亡", "被害", "犯罪", "詐欺", "窃盗", "暴行"],
    "イベント・お知らせ": ["祭り", "イベント", "開催", "募集", "教室", "講座", "ボランティア", "選挙", "行政", "区議"],
    "グルメ・新店舗": ["オープン", "開店", "閉店", "ランチ", "カフェ", "レストラン", "ラーメン", "新店", "グルメ"],
}
# 上記いずれにも該当しない場合 → "その他"
```

### 5.3 データ保持

- `data/news.json` に取得済みニュースを蓄積（URLで重複排除）
- 直近30日分を保持し、それ以前は自動削除
- サイトには直近7日分を表示

## 6. フロントエンド仕様

### 6.1 UI要件

- スマホファーストのレスポンシブデザイン
- カテゴリタブまたはフィルターで絞り込み可能
- 各ニュースはタイトル（元記事へのリンク）・ソース名・日時・カテゴリラベルを表示
- ライトモードのみ、親しみやすい暖色系（オレンジ・ベージュ基調）の色合い
- 最終更新日時を表示

### 6.2 デザインイメージ

- シンプルで読みやすいニュースリスト形式
- カテゴリごとに色分けされたラベル（バッジ）
- 外部ライブラリは使わず、素のHTML/CSS/JSで軽量に

## 7. GitHub Actions 設定

### 7.1 ワークフロー

```yaml
name: Update Kasai News

on:
  schedule:
    - cron: '0 22 * * *'  # UTC 22:00 = JST 07:00（毎朝7時）
  workflow_dispatch:        # 手動実行も可能に

jobs:
  update:
    runs-on: ubuntu-latest
    permissions:
      contents: write       # docs/ への書き込みに必要
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -r requirements.txt
      - run: python scripts/fetch_news.py
      - run: python scripts/categorize.py
      - run: python scripts/generate_site.py
      - name: Commit and push
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add docs/ data/
          git diff --staged --quiet || git commit -m "Update news $(date +%Y-%m-%d)"
          git push
```

### 7.2 GitHub Pages 設定

- Source: `docs/` フォルダから配信
- Branch: `main`

## 8. セキュリティ対策

### 8.1 個人情報の保護（重要）

- **gitのコミッターはbot名を使用**: `github-actions[bot]` を設定し、個人のメールアドレスがコミット履歴に残らないようにする
- **GitHubの設定**: Settings → Emails → 「Keep my email addresses private」を有効にする
- **リポジトリ名に個人名を含めない**: `kasai-news` のようなプロジェクト名にする

### 8.2 サイト側の対策

- **個人情報をサイトに表示しない**: フッターに名前やメールアドレスを書かない
- **Google Analyticsなどのトラッキングは不要**（自分用なので）
- **robots.txt**: 検索エンジンにインデックスされたくない場合は以下を配置

```
# docs/robots.txt
User-agent: *
Disallow: /
```

- **metaタグでも検索エンジンを拒否**:

```html
<meta name="robots" content="noindex, nofollow">
```

### 8.3 GitHub Actions のセキュリティ

- **permissions を最小限に**: `contents: write` のみ付与
- **API Keyは使わない構成**: Google News RSSは公開フィードなのでキー不要
- **依存パッケージはバージョン固定**: `requirements.txt` でバージョンを明記

### 8.4 XSS対策

- RSSから取得したタイトルや説明文はHTMLエスケープしてから表示する
- Jinja2の `{{ variable }}` はデフォルトでエスケープされるが、`autoescape=True` を明示的に設定する

## 9. Claude Codeへの指示

以下の順序で実装してください:

1. **リポジトリ作成**: `kasai-news` という名前でGitHubリポジトリを作成（public）
2. **Pythonスクリプト実装**: fetch → categorize → generate の3ステップ
3. **テンプレート・CSS作成**: スマホ対応のレスポンシブデザイン
4. **ローカルで動作確認**: スクリプトを実行してdocs/にサイトが生成されることを確認
5. **GitHub Actions設定**: ワークフローファイルを配置
6. **GitHub Pages有効化**: docs/フォルダから配信する設定
7. **セキュリティ設定**: robots.txt、noindexメタタグ、gitのプライバシー設定
8. **手動実行テスト**: workflow_dispatchで初回実行して動作確認

## 10. 将来の拡張（任意）

- AI要約の追加（Anthropic APIを使ったニュース要約、月数百円程度のAPI費用）
- LINE/Slack通知連携
- ニュースのブックマーク機能
- 過去ニュースの検索機能
