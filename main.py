import os, requests, feedparser
from bs4 import BeautifulSoup

NOTION_TOKEN = os.environ["NOTION_TOKEN"]
DB_ID = os.environ["NOTION_DB_ID"]
USERNAME = os.environ["X_USERNAME"]
KEYWORD = os.environ["KEYWORD"]

RSS_URL = f"https://nitter.poast.org/{USERNAME}/rss"

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

def exists(tweet_id):
    q = {
        "filter": {
            "property": "取得ID",
            "rich_text": {"equals": tweet_id}
        }
    }
    r = requests.post(
        f"https://api.notion.com/v1/databases/{DB_ID}/query",
        headers=headers,
        json=q
    )
    return len(r.json()["results"]) > 0

feed = feedparser.parse(RSS_URL)

for e in feed.entries:
    text = BeautifulSoup(e.summary, "html.parser").get_text()

    if KEYWORD not in text:
        continue

    tweet_id = e.link.split("/")[-1]
    if exists(tweet_id):
        continue

    soup = BeautifulSoup(e.summary, "html.parser")
    imgs = [img["src"] for img in soup.find_all("img")]

    payload = {
        "parent": {"database_id": DB_ID},
        "properties": {
            "本文": {"title": [{"text": {"content": text[:2000]}}]},
            "取得ID": {"rich_text": [{"text": {"content": tweet_id}}]},
            "元URL": {"url": e.link},
            "投稿日時": {"date": {"start": e.published}},
            "画像": {
                "files": [
                    {"name": "image", "external": {"url": u}}
                    for u in imgs
                ]
            }
        }
    }

    requests.post(
        "https://api.notion.com/v1/pages",
        headers=headers,
        json=payload
    )

feed = feedparser.parse(RSS_URL)

print("RSS URL:", RSS_URL)
print("ENTRY COUNT:", len(feed.entries))

for e in feed.entries:
    print("ENTRY FOUND")
    text = BeautifulSoup(e.summary, "html.parser").get_text()
    print("TEXT:", text)

    if KEYWORD not in text:
        continue
