# slack-news-feed-os

`slack-news-feed-os`は、指定されたRSSフィードから最新の記事を取得し、その内容を要約してSlackに通知する自動化システムです。Pythonを使用し、`feedparser`, `requests`, `BeautifulSoup`, `sqlite3`, `logging`, `dotenv`などのライブラリを活用しています。

## 主な機能

- 指定されたRSSフィードURLから最新記事を定期的にチェック
- 新しい記事が見つかった場合、その内容をGPTモデルを使って日本語に要約
- 要約された記事をSlackに自動通知
- 記事のIDをデータベースに保存し、重複通知を避ける

## 環境設定

このシステムを実行する前に、以下の環境変数を設定する必要があります。

- `SLACK_WEBHOOK_URL`: SlackのWebhook URL
- `OPENAI_API_KEY`: OpenAI APIのキー

これらの値は`.env`ファイルに保存してください。

## インストール方法

1. 必要なPythonパッケージをインストールします。
    ```bash
    pip install -r requirements.txt
    ```

2. `.env`ファイルをプロジェクトのルートに作成し、上記の環境変数を設定します。

## 使い方

1. `main.py`スクリプトを実行します。
    ```bash
    python main.py
    ```

2. スクリプトは指定された間隔でRSSフィードをチェックし、新しい記事がある場合はSlackに通知します。

