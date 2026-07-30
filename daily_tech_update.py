import os
import json
import re
import random
import urllib.request
import urllib.error
from datetime import datetime

HN_TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"

TECH_KEYWORDS = [
    "ai", "llm", "software", "github", "programming", "python", "javascript",
    "typescript", "rust", "cloud", "security", "open source", "framework",
    "database", "api", "developer", "code", "app", "startup", "linux",
    "web", "data", "model", "chip", "algorithm"
]

STORIES_TO_SCAN = 30

START_MARKER = "<!-- TECH_UPDATE_START -->"
END_MARKER = "<!-- TECH_UPDATE_END -->"


def fetch_json(url):
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return json.loads(response.read().decode())
    except urllib.error.URLError as e:
        print(f"Network error fetching {url}: {e}")
        return None
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None


def get_tech_story():
    story_ids = fetch_json(HN_TOP_STORIES_URL)
    if not story_ids:
        return None

    candidates = []
    for story_id in story_ids[:STORIES_TO_SCAN]:
        item = fetch_json(HN_ITEM_URL.format(story_id))
        if not item or item.get("type") != "story":
            continue

        title = item.get("title", "")
        url = item.get("url", f"https://news.ycombinator.com/item?id={story_id}")
        score = item.get("score", 0)

        if any(keyword in title.lower() for keyword in TECH_KEYWORDS):
            candidates.append({"title": title, "url": url, "score": score})

    if not candidates:
        top_item = fetch_json(HN_ITEM_URL.format(story_ids[0]))
        if not top_item:
            return None
        return {
            "title": top_item.get("title", "Untitled"),
            "url": top_item.get("url", f"https://news.ycombinator.com/item?id={story_ids[0]}"),
            "score": top_item.get("score", 0),
        }

    candidates.sort(key=lambda c: c["score"], reverse=True)
    top_pool = candidates[:5] if len(candidates) >= 5 else candidates
    return random.choice(top_pool)


def build_section(story):
    date_str = datetime.now().strftime("%B %d, %Y")
    return (
        f"### Tech update - {date_str}\n\n"
        f"**{story['title']}**\n\n"
        f"Link: {story['url']}\n"
        f"Score: {story['score']} points on Hacker News\n"
    )


def update_readme(story):
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        content = f"# aly-abbas11\n\n{START_MARKER}\n_Loading..._\n{END_MARKER}"

    new_section = build_section(story)

    if START_MARKER not in content or END_MARKER not in content:
        content += f"\n\n{START_MARKER}\n{new_section}\n{END_MARKER}\n"
    else:
        pattern = re.compile(
            rf"{re.escape(START_MARKER)}.*?{re.escape(END_MARKER)}",
            re.DOTALL,
        )
        content = pattern.sub(f"{START_MARKER}\n{new_section}\n{END_MARKER}", content)

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)

    print(f"README updated: {story['title']}")


def main():
    story = get_tech_story()
    if story is None:
        print("Could not fetch a story today, skipping update.")
        return

    update_readme(story)


if __name__ == "__main__":
    main()
