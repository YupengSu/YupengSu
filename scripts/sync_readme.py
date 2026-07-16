#!/usr/bin/env python3
"""Sync the News and Publications sections of README.md from the homepage repo's
_data/*.yml (the single source of truth). Static sections are left untouched.

Set HOMEPAGE_DATA_URL to override the data source (used for local testing with a
file:// URL); defaults to the homepage repo's raw main branch.
"""
import os
import re
import urllib.request
import yaml

BASE = os.environ.get(
    "HOMEPAGE_DATA_URL",
    "https://raw.githubusercontent.com/YupengSu/YupengSu.github.io/main/_data/",
)
README = os.path.join(os.path.dirname(__file__), "..", "README.md")


def load(name):
    with urllib.request.urlopen(BASE + name) as r:
        return yaml.safe_load(r.read().decode("utf-8"))


def bold(authors):
    return authors.replace("Yupeng Su", "**Yupeng Su**")


def render_news(news):
    out = []
    for n in news:
        emoji = (n.get("emoji", "") + " ") if n.get("emoji") else ""
        out.append(f"- *{n['date']}* : &nbsp; {emoji}{n['text']}")
    return "\n".join(out)


def render_pubs(pubs):
    out = []
    for p in pubs:
        star = "★ " if p.get("first_author") else ""
        title = f"[{p['title']}]({p['links']['paper']})"
        links = p.get("links", {})
        code = f" [[Code]]({links['code']})" if links.get("code") else ""
        out.append(f"- `{p['venue']}` {star}{title}, {bold(p['authors'])}.{code}")
    return "\n\n".join(out)


def replace_block(text, key, content):
    start, end = f"<!-- {key}:START -->", f"<!-- {key}:END -->"
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
    if not pattern.search(text):
        raise SystemExit(f"Markers {start} / {end} not found in README.md")
    return pattern.sub(f"{start}\n{content}\n{end}", text)


def main():
    news = load("news.yml")
    pubs = load("publications.yml")
    path = os.path.abspath(README)
    with open(path, encoding="utf-8") as f:
        text = f.read()
    text = replace_block(text, "NEWS", render_news(news))
    text = replace_block(text, "PUBS", render_pubs(pubs))
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Synced README.md: {len(news)} news, {len(pubs)} publications.")


if __name__ == "__main__":
    main()
