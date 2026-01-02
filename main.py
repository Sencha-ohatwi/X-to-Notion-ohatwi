import os, requests, feedparser
from bs4 import BeautifulSoup

NOTION_TOKEN = os.environ["NOTION_TOKEN"]
DB_ID = os.environ["NOTION_DB_ID"]
USERNAME = os.environ["X_USERNAME"]
KEYWORD = os.environ["KEYWORD"]

RSS_URL = "https://rss-bridge.org/bridge01/?action=display&bridge=TwitterBridge&u=greentra_vrc&format=Atom"

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


# ★ これが抜けてると今回のエラーになる
RSS_URL = f"https://rss-bridge.org/bridge01/?action=display&bridge=TwitterBridge&u={USERNAME}&format=Atom"

feed = feedparser.parse(
    RSS_URL,
    request_headers={
        "User-Agent": "Mozilla/5.0 (X-to-Notion Bot)"
    }
)

print("RSS URL:", RSS_URL)
print("ENTRY COUNT:", len(feed.entries))

for e in feed.entries:
    text = BeautifulSoup(e.summary, "html.parser").get_text()

    if KEYWORD.lower() not in text.lower():
        continue

    tweet_id = e.link.split("/")[-1]
    if exists(tweet_id):
        continue

    imgs = []
    if "media_content" in e:
        for m in e.media_content:
            if "url" in m:
                imgs.append(m["url"])
            
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
