"""Refresh the "Latest videos" block of README.md from the channel's YouTube RSS feed.

Standard library only. Exits non-zero if the feed cannot be read or has no
entries, so a broken feed shows up as a red run instead of an emptied README.
"""
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from html import escape

CHANNEL_ID = "UClwDjN7I1v1AqlWsmUh3MCA"
FEED = f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"
COUNT = 5
NS = {"a": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015"}
START, END = "<!-- VIDEOS:START -->", "<!-- VIDEOS:END -->"


def fetch_entries():
    req = urllib.request.Request(FEED, headers={"User-Agent": "profile-readme-refresh"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        root = ET.fromstring(resp.read())
    entries = []
    for e in root.findall("a:entry", NS)[:COUNT]:
        title = e.findtext("a:title", default="", namespaces=NS).strip()
        vid = e.findtext("yt:videoId", default="", namespaces=NS).strip()
        date = e.findtext("a:published", default="", namespaces=NS)[:10]
        if title and vid:
            entries.append((title, vid, date))
    return entries


def render(entries):
    lines = [f"- [{t.replace('[', '(').replace(']', ')')}](https://www.youtube.com/watch?v={v}) ({d})" for t, v, d in entries]
    return "\n".join(lines)


def main():
    entries = fetch_entries()
    if not entries:
        sys.exit("feed returned no entries; leaving README untouched")
    with open("README.md", encoding="utf-8") as f:
        text = f.read()
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
    if not pattern.search(text):
        sys.exit("markers not found in README.md")
    block = f"{START}\n{render(entries)}\n{END}"
    new = pattern.sub(lambda _m: block, text)
    if new != text:
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(new)
        print(f"updated with {len(entries)} videos")
    else:
        print("no change")


if __name__ == "__main__":
    main()
