import feedparser
import requests
import time
import openai
from bs4 import BeautifulSoup
import os
import sqlite3
import logging
from dotenv import load_dotenv
from requests.exceptions import RequestException

# .envファイルから環境変数を読み込む
load_dotenv()

# ログの設定
logging.basicConfig(filename='rss_feed.log', level=logging.INFO, format='%(asctime)s %(message)s')

# データベースのセットアップ
conn = sqlite3.connect('rss_feed.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS last_entry_ids (rss_url TEXT PRIMARY KEY, last_entry_id TEXT)''')
conn.commit()

# 設定
rss_urls = [
    'https://www.theverge.com/rss/index.xml',
    'https://techcrunch.com/feed/',
    'http://feeds.bbci.co.uk/news/technology/rss.xml',
    'https://www.cnet.com/rss/news/',
    'https://www.wired.com/feed/tag/ai/latest/rss',
    'https://www.wired.com/feed/rss',   
    'https://www.engadget.com/rss.xml',
    'https://www.technologyreview.com/feed/',
    'https://gizmodo.com/rss',
    'https://venturebeat.com/feed/'
]
CHECK_INTERVAL = 60 * 10  # 10分ごとにチェック
model_name = "gpt-3.5-turbo-0613"
slack_webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
openai_api_key = os.environ.get("OPENAI_API_KEY")

openai.api_key = openai_api_key

while True:
    for rss_url in rss_urls:
        try:
            # RSSフィードをチェック
            feed = feedparser.parse(rss_url)

            # 新しい記事をチェック
            first_entry = feed.entries[0]

            # データベースから最後のentry IDを取得
            cursor.execute("SELECT last_entry_id FROM last_entry_ids WHERE rss_url=?",                           (rss_url,))
            result = cursor.fetchone()
            last_entry_id = result[0] if result else None

            if last_entry_id != first_entry.id:
                # 最後のentry IDをデータベースに保存
                cursor.execute("REPLACE INTO last_entry_ids (rss_url, last_entry_id) VALUES (?, ?)",
                               (rss_url, first_entry.id))
                conn.commit()

                # 記事のURLから内容を取得
                response = requests.get(first_entry.link, timeout=10)
                response.raise_for_status()
                html_content = response.text
                soup = BeautifulSoup(html_content, 'html.parser')
                paragraphs = soup.find_all('p')
                content = ' '.join(p.get_text() for p in paragraphs)

                # GPTで日本語に要約
                response = openai.ChatCompletion.create(
                    model=model_name,
                    messages=[
                        {"role": "user", "content": f"""
                         以下は、{feed.feed.title}の記事です。この内容を400文字以内で日本語で要約してください。
                         記事のタイトルは{first_entry.title}です。
                         初めて、その要約を読んだ人が記事の内容を確実に理解できるようにしてください。
                         不要なHTMLタグなどは削除してください。
                          この要約の内容を見ると記事の重要なポイントがわかるようにしてください。
                        {content}
                         """
                         },
                    ],
                    timeout=30
                )
                result = response.choices[0]["message"]["content"]

                # Slackに通知
                slack_message = {
                    'text': f"\n\n\n新しい記事: {first_entry.link}\n要約: {result}\n\n\n"
                }
                response = requests.post(slack_webhook_url, json=slack_message, timeout=10)
                response.raise_for_status()

        except RequestException as e:
            logging.error(f"Request error: {e}")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")

    # 一定時間待機
    time.sleep(CHECK_INTERVAL)
