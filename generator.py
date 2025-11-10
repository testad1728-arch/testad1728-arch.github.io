

import os, json, re, hashlib, datetime, textwrap
from urllib.request import urlopen, Request
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(__file__)
POSTS_DIR = os.path.join(ROOT, "posts")

def fetch(url):
    req = Request(url, headers={"User-Agent":"Mozilla/5.0"})
    with urlopen(req, timeout=20) as r:
        return r.read()

def parse_rss(xml_bytes, limit=10):
    items = []
    try:
        root = ET.fromstring(xml_bytes)
        # handle namespaces roughly
        channel = root.find("channel")
        if channel is None:
            # namespaced rss
            for child in root.iter():
                if child.tag.endswith("channel"):
                    channel = child
                    break
        if channel is None:
            return items
        for item in channel.findall("item"):
            title = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            desc = (item.findtext("description") or "").strip()
            pub = item.findtext("pubDate") or ""
            if title and link:
                items.append({"title": title, "link": link, "description": desc, "pubDate": pub})
            if len(items) >= limit:
                break
    except Exception as e:
        print("rss parse error:", e)
    return items

def summarize(text, lang="en", max_sent=3):
    # very simple extractive summary: pick first N sentences after cleaning.
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = re.sub(r"\s+", " ", text).strip()
    # sentence split naive
    if lang == "ar":
        parts = re.split(r"(?<=[.!؟])\s+", text)
    else:
        parts = re.split(r"(?<=[.!?])\s+", text)
    parts = [p.strip() for p in parts if p.strip()]
    summary = " ".join(parts[:max_sent])[:600]
    return summary

def slugify(s):
    s = re.sub(r"[^\w\s-]", "", s, flags=re.U)
    s = re.sub(r"\s+", "-", s.strip(), flags=re.U)
    return s[:60].lower() or hashlib.md5(s.encode("utf-8")).hexdigest()[:10]

def write_post(title, summary, source_url, lang="en"):
    slug = slugify(title)
    fname = f"{slug}.html"
    path = os.path.join(POSTS_DIR, fname)
    date = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    html = f"""<!DOCTYPE html>
<html lang="{ 'ar' if lang=='ar' else 'en' }" dir="{ 'rtl' if lang=='ar' else 'ltr' }">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>{title}</title>
  <link rel="stylesheet" href="../assets/style.css" />
  <meta name="robots" content="index,follow" />
</head>
<body>
  <main class="container">
    <a href="../index.html">↩ {'الرئيسية' if lang=='ar' else 'Home'}</a>
    <article class="card" style="margin-top:12px">
      <div class="meta">{date}</div>
      <h1>{title}</h1>
      <p>{summary}</p>
      <p>{'المصدر' if lang=='ar' else 'Source'}: <a href="{source_url}" rel="nofollow noopener" target="_blank">{source_url}</a></p>
      <p class="muted">{'هذه المادة تلخيص تحويلي مع رابط للمصدر' if lang=='ar' else 'Transformative summary with a source link.'}</p>
    </article>
  </main>
</body>
</html>"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return {"path": f"posts/{fname}", "title": title, "summary": summary[:180], "date": date, "lang": "AR" if lang=="ar" else "EN"}

def rebuild_index(entries):
    idx_path = os.path.join(POSTS_DIR, "index.json")
    try:
        with open(idx_path, "r", encoding="utf-8") as f:
            current = json.load(f)
    except Exception:
        current = []
    # prepend new
    all_entries = entries + current
    # dedup by path
    seen, unique = set(), []
    for e in all_entries:
        if e["path"] not in seen:
            unique.append(e)
            seen.add(e["path"])
    with open(idx_path, "w", encoding="utf-8") as f:
        json.dump(unique[:200], f, ensure_ascii=False, indent=2)

def update_sitemap(site_url):
    sm_path = os.path.join(ROOT, "sitemap.xml")
    try:
        with open(os.path.join(POSTS_DIR, "index.json"), "r", encoding="utf-8") as f:
            posts = json.load(f)
    except Exception:
        posts = []
    lastmod = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    urls = [f"""  <url><loc>{site_url}</loc><lastmod>{lastmod}</lastmod><changefreq>daily</changefreq></url>"""]
    for p in posts[:500]:
        urls.append(f"""  <url><loc>{site_url}{p["path"]}</loc><lastmod>{lastmod}</lastmod><changefreq>weekly</changefreq></url>""")
    xml = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">\n" + "\n".join(urls) + "\n</urlset>\n"
    with open(sm_path, "w", encoding="utf-8") as f:
        f.write(xml)

def main():
    cfg = json.load(open(os.path.join(ROOT, "site.config.json"), "r", encoding="utf-8"))
    feeds = json.load(open(os.path.join(ROOT, "feeds.json"), "r", encoding="utf-8"))
    os.makedirs(POSTS_DIR, exist_ok=True)
    new_entries = []
    for feed in feeds:
        try:
            data = fetch(feed["url"])
            items = parse_rss(data, limit=3)
            for it in items:
                summary = summarize(it.get("description",""), lang=feed.get("lang","en"))
                if not summary:
                    continue
                entry = write_post(it["title"], summary, it["link"], lang=feed.get("lang","en"))
                new_entries.append(entry)
        except Exception as e:
            print("feed error", feed.get("name"), e)
    if new_entries:
        rebuild_index(new_entries)
    update_sitemap(cfg.get("site_url","/"))
    print("Generated", len(new_entries), "posts")

if __name__ == "__main__":
    main()
