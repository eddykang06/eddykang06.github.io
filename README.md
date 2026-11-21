# eddykang06.github.io

Personal website: https://eddykang06.github.io

## Editing

Everything you edit is in `content/`:

- `content/home.md`: the homepage (bio, links, research, news, projects). Keep the `#` headings. Each project is a `##` heading followed by `- Authors:`, `- Venue:`, `- Links:`, `- Description:` lines (optional `- Image: images/name.jpg`).
- `content/blog/*.md`: blog posts with `$...$` / `$$...$$` math. Start from `content/blog/_example.md`. Files starting with `_` are drafts and are not published.

Push to `main` and GitHub Actions runs `build.py` and deploys the site in about a minute.
To preview locally: `pip install markdown`, run `python build.py`, open `_site/index.html`.

## Credit

This website is built on **[Jon Barron](https://jonbarron.info/)'s** academic website template.
The page layout, `stylesheet.css`, and thumbnail hover script come from his source code at
[github.com/jonbarron/jonbarron.github.io](https://github.com/jonbarron/jonbarron.github.io).
