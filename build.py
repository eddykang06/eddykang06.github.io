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


# Small line icons shown before each header link, matched by the link's label
# (case-insensitive). Paths are from Lucide (lucide.dev, ISC license).
# Labels without an entry get the generic "link" icon.
ICONS = {
    "email": '<rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>',
    "blog": '<path d="M12 20h9"/><path d="M16.376 3.622a1 1 0 0 1 3.002 3.002L7.368 18.635a2 2 0 0 1-.855.506l-2.872.838a.5.5 0 0 1-.62-.62l.838-2.872a2 2 0 0 1 .506-.854z"/>',
    "linkedin": '<path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"/><rect width="4" height="12" x="2" y="9"/><circle cx="4" cy="4" r="2"/>',
    "github": '<path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"/><path d="M9 18c-4.51 2-5-2-7-2"/>',
    "cv": '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M16 13H8"/><path d="M16 17H8"/><path d="M10 9H8"/>',
    "scholar": '<path d="M21.42 10.922a1 1 0 0 0-.019-1.838L12.83 5.18a2 2 0 0 0-1.66 0L2.6 9.08a1 1 0 0 0 0 1.832l8.57 3.908a2 2 0 0 0 1.66 0z"/><path d="M22 10v6"/><path d="M6 12.5V16a6 3 0 0 0 12 0v-3.5"/>',
    "link": '<path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>',
}
ICONS["resume"] = ICONS["cv"]
ICONS["google scholar"] = ICONS["scholar"]


def icon(label):
    paths = ICONS.get(label.strip().lower(), ICONS["link"])
    return (
        '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
        f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{paths}</svg>'
    )


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

    links = []
    for item in bullets(home["Links"]):
        label = re.match(r"\[([^\]]+)\]", item)
        link = inline(item)
        if label:
            link = re.sub(r"^(<a [^>]*>)", lambda m: m.group(1) + icon(label.group(1)), link, count=1)
        links.append(link)
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
