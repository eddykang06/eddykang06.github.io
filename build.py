"""Build the website from Markdown.

    content/home.md       -> index.html
    content/blog/*.md     -> blog/<name>.html and the list on blog/index.html

Output goes to _site/. Run `python build.py` (needs `pip install markdown`).
"""

import datetime
import html
import re
import shutil
from pathlib import Path

import markdown

ROOT = Path(__file__).parent
CONTENT = ROOT / "content"
TEMPLATES = ROOT / "templates"
OUT = ROOT / "_site"
OWNER = "Eddy Kang"  # bolded in project author lists


def fail(msg):
    raise SystemExit(f"Build failed: {msg}")


def read(path):
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def inline(text):
    """Markdown for a single line or paragraph, without the surrounding <p>."""
    out = markdown.markdown(text.strip())
    return re.sub(r"^<p>(.*)</p>$", r"\1", out, flags=re.S)


def sections(text, marker):
    """Split text on headings that start with `marker` ('# ' or '## ')."""
    parts, name = {}, None
    for line in text.split("\n"):
        if line.startswith(marker):
            name = line[len(marker):].strip()
            parts[name] = []
        elif name is not None:
            parts[name].append(line)
    return {k: "\n".join(v).strip() for k, v in parts.items()}


def bullets(text):
    return [line[2:].strip() for line in text.split("\n") if line.startswith("- ")]


def labeled(items):
    fields = {}
    for item in items:
        label, _, value = item.partition(":")
        fields[label.strip().lower()] = value.strip()
    return fields


# ---------- homepage ----------

def build_home():
    home = sections(read(CONTENT / "home.md"), "# ")
    for name in ["Bio", "Links", "Research", "Recent News", "Projects"]:
        if name not in home:
            fail(f'content/home.md is missing the "# {name}" heading')

    bio = ""
    for para in home["Bio"].split("\n\n"):
        lines = inline(para).split("\n")
        bio += "          <p>\n" + "".join(f"            {l.strip()}\n" for l in lines) + "          </p>\n"

    links = [inline(item) for item in bullets(home["Links"])]
    links = "".join(
        f"            {link}{' &nbsp;/&nbsp;' if i < len(links) - 1 else ''}\n"
        for i, link in enumerate(links)
    )

    research = f"          {inline(home['Research'])}\n"

    news = ""
    for item in bullets(home["Recent News"]):
        date, _, text = item.partition(":")
        news += (
            '          <div class="news-item">\n'
            f'            <span class="news-date">{html.escape(date.strip())}</span>\n'
            f'            <span class="news-text">{inline(text)}</span>\n'
            "          </div>\n"
        )

    projects = ""
    for title, body in sections(home["Projects"], "## ").items():
        f = labeled(bullets(body))
        authors = ", ".join(
            f"<strong>{a}</strong>" if a == OWNER else a
            for a in (x.strip() for x in f.get("authors", "").split(","))
            if a
        )
        venue, _, year = f.get("venue", "").rpartition(", ")
        venue_html = f"<em>{inline(venue)}</em>, {year}" if venue else inline(year)
        image = f.get("image") or "images/placeholder.svg"
        projects += (
            '      <article class="paper">\n'
            '        <div class="paper-media">\n'
            '          <div class="one">\n'
            f'            <img src="{html.escape(image)}" alt="{html.escape(title)}" width="160" height="160">\n'
            "          </div>\n"
            "        </div>\n"
            '        <div class="paper-info">\n'
            f'          <span class="papertitle">{inline(title)}</span>\n'
            f'          <div class="paper-authors">{inline(authors)}</div>\n'
            f'          <div class="paper-venue">{venue_html}</div>\n'
        )
        if f.get("links"):
            found = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", f["links"])
            joined = " / ".join(f'<a href="{html.escape(u)}">{html.escape(n)}</a>' for n, u in found)
            projects += f'          <div class="paper-links">{joined}</div>\n'
        if f.get("description"):
            projects += f'          <p class="paper-desc">{inline(f["description"])}</p>\n'
        projects += "        </div>\n      </article>\n"

    page = read(TEMPLATES / "home.html")
    today = datetime.date.today()
    updated = f"{today:%B} {today.day}, {today.year}"
    for key, value in [("updated", updated), ("bio", bio), ("links", links), ("research", research), ("news", news), ("projects", projects)]:
        page = page.replace("{{" + key + "}}", value)
    (OUT / "index.html").write_text(page, encoding="utf-8")


# ---------- blog ----------

MATH = re.compile(r"\$\$.+?\$\$|(?<![\\$])\$(?!\s)[^$\n]+?(?<!\s)\$", re.S)


def render_post(text):
    """Markdown to HTML, leaving $...$ and $$...$$ untouched for KaTeX."""
    saved = []

    def stash(m):
        saved.append(m.group(0))
        return f"MATHPLACEHOLDER{len(saved) - 1}X"

    body = markdown.markdown(MATH.sub(stash, text), extensions=["fenced_code", "tables"])
    return re.sub(r"MATHPLACEHOLDER(\d+)X", lambda m: html.escape(saved[int(m.group(1))], quote=False), body)


def parse_post(path):
    text = read(path)
    m = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S)
    if not m:
        fail(f"{path.name} needs a header with title and date (see content/blog/_example.md)")
    meta = dict(line.split(":", 1) for line in m.group(1).split("\n") if ":" in line)
    meta = {k.strip().lower(): v.strip() for k, v in meta.items()}
    if "title" not in meta or "date" not in meta:
        fail(f"{path.name} needs both 'title:' and 'date:' in its header")
    try:
        date = datetime.date.fromisoformat(meta["date"])
    except ValueError:
        fail(f"{path.name}: date must look like 2026-11-21")
    return {"slug": path.stem, "title": meta["title"], "date": date, "body": m.group(2)}


def build_blog():
    out = OUT / "blog"
    out.mkdir()
    posts = sorted(
        (parse_post(p) for p in (CONTENT / "blog").glob("*.md") if not p.name.startswith("_")),
        key=lambda p: p["date"],
        reverse=True,
    )

    template = read(TEMPLATES / "post.html")
    for p in posts:
        d = p["date"]
        page = (
            template.replace("{{title}}", html.escape(p["title"]))
            .replace("{{date}}", f"{d:%B} {d.day}, {d.year}")
            .replace("{{body}}", render_post(p["body"]))
        )
        (out / f"{p['slug']}.html").write_text(page, encoding="utf-8")

    if posts:
        listing = "".join(
            f'        <p>{p["date"]:%b %Y} &nbsp;/&nbsp; <a href="{p["slug"]}.html">{html.escape(p["title"])}</a></p>\n'
            for p in posts
        )
    else:
        listing = "        <p>No posts yet.</p>\n"
    (out / "index.html").write_text(read(TEMPLATES / "blog.html").replace("{{posts}}", listing), encoding="utf-8")

    # images and other files saved next to posts
    for f in (CONTENT / "blog").iterdir():
        if f.is_file() and f.suffix != ".md":
            shutil.copy(f, out / f.name)


if __name__ == "__main__":
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copy(ROOT / "stylesheet.css", OUT)
    shutil.copytree(ROOT / "images", OUT / "images")
    build_home()
    build_blog()
    print(f"Built site in {OUT}")
