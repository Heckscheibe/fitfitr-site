#!/usr/bin/env python3
"""Static checks for the FitFitr site. Standard library only.

Fails (exit 1) on:
  - an internal link or #anchor that does not resolve to a file or id
  - an hreflang alternate whose partner page does not exist or does not point back
  - an `http://` URL anywhere in the markup
  - an off-site script, stylesheet, font, icon or image
  - a page without lang, title, description, viewport or exactly one h1
  - a missing or wrong CNAME, or a missing .nojekyll
  - a root page that does not load assets/lang-redirect.js before the stylesheet,
    or lacks the <noscript> meta refresh to /en/
Warns (does not fail) about every remaining [bracketed placeholder].

Usage: python3 scripts/check.py
"""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
DOMAIN = "fitfitr.app"
ORIGIN = "https://" + DOMAIN
SKIP_DIRS = {".git", "scripts", "node_modules"}
RESOURCE_REL = {"stylesheet", "icon", "shortcut", "apple-touch-icon", "preload", "modulepreload", "manifest", "mask-icon"}
VOID = {"meta", "link", "img", "br", "hr", "input", "source", "area", "base", "col", "embed", "param", "track", "wbr"}


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lang = None
        self.title = ""
        self._in_title = False
        self.meta = {}
        self.ids = set()
        self.links = []        # (tag, attr, value, rel)
        self.alternates = []   # (hreflang, href)
        self.h1 = 0
        self.text = []
        self.stack = []
        self.skip_text = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang")
        if tag == "title":
            self._in_title = True
        if tag == "meta" and a.get("name"):
            self.meta[a["name"]] = a.get("content", "")
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "h1":
            self.h1 += 1
        rel = (a.get("rel") or "").lower().split()
        for attr in ("href", "src", "action", "poster", "data"):
            if attr in a and a[attr] is not None:
                self.links.append((tag, attr, a[attr], rel))
        if tag == "link" and "alternate" in rel and a.get("hreflang"):
            self.alternates.append((a["hreflang"], a.get("href", "")))
        if tag in ("script", "style"):
            self.skip_text += 1

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if tag in ("script", "style") and self.skip_text:
            self.skip_text -= 1

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if not self.skip_text:
            self.text.append(data)


def url_to_file(path):
    """Map a site path to the file that serves it, or None."""
    rel = path.lstrip("/")
    cand = ROOT / rel
    if path.endswith("/") or rel == "":
        cand = cand / "index.html"
    if cand.is_file():
        return cand
    if (ROOT / rel).is_dir() and (ROOT / rel / "index.html").is_file():
        return ROOT / rel / "index.html"
    return None


def main():
    errors, warnings = [], []
    html_files = sorted(p for p in ROOT.rglob("*.html") if not (set(p.relative_to(ROOT).parts) & SKIP_DIRS))
    pages = {}
    for f in html_files:
        raw = f.read_text(encoding="utf-8")
        p = Page()
        p.feed(raw)
        pages[f] = (p, raw)

    def rel(f):
        return str(f.relative_to(ROOT))

    for f, (p, raw) in pages.items():
        name = rel(f)
        if not p.lang:
            errors.append(f"{name}: <html> has no lang")
        if not p.title.strip():
            errors.append(f"{name}: no <title>")
        if not p.meta.get("description"):
            errors.append(f"{name}: no meta description")
        if "viewport" not in p.meta:
            errors.append(f"{name}: no meta viewport")
        if p.meta.get("color-scheme") != "light dark":
            errors.append(f"{name}: meta color-scheme is not 'light dark'")
        if p.h1 != 1:
            errors.append(f"{name}: expected exactly one h1, found {p.h1}")
        if "http://" in raw:
            errors.append(f"{name}: contains an http:// URL")
        if re.search(r"<script(?![^>]*\bsrc=)[^>]*>", raw):
            errors.append(f"{name}: contains an inline <script>")

        for tag, attr, value, relv in p.links:
            value = value.strip()
            if not value:
                errors.append(f"{name}: empty {attr} on <{tag}>")
                continue
            if value.startswith(("mailto:", "tel:")):
                continue
            parts = urlsplit(value)
            resource = tag in ("script", "img", "source", "iframe", "video", "audio", "embed", "object") \
                or (tag == "link" and any(r in RESOURCE_REL for r in relv))
            if parts.scheme in ("http", "https") or value.startswith("//"):
                host = parts.netloc or urlsplit("https:" + value).netloc
                own = host == DOMAIN
                if parts.scheme == "http":
                    continue  # already reported above
                if resource and not own:
                    errors.append(f"{name}: off-site {tag} {attr}: {value}")
                if not own:
                    continue
                path = parts.path or "/"
            elif parts.scheme:
                errors.append(f"{name}: unsupported scheme in {attr}: {value}")
                continue
            else:
                path = parts.path
            if not path and parts.fragment:
                target = f
            else:
                if not path.startswith("/"):
                    base = "/" + rel(f.parent) + "/" if f.parent != ROOT else "/"
                    path = urlsplit(base + path).path
                target = url_to_file(path)
                if target is None:
                    errors.append(f"{name}: broken link {value}")
                    continue
            if parts.fragment:
                tp = pages.get(target)
                if tp is None or parts.fragment not in tp[0].ids:
                    errors.append(f"{name}: anchor #{parts.fragment} not found in {rel(target)}")

        for code, href in p.alternates:
            parts = urlsplit(href)
            if parts.netloc != DOMAIN:
                errors.append(f"{name}: hreflang {code} is not on {DOMAIN}: {href}")
                continue
            target = url_to_file(parts.path)
            if target is None:
                errors.append(f"{name}: hreflang {code} partner missing: {href}")
                continue
            partner = pages[target][0]
            back = [urlsplit(h).path for c, h in partner.alternates]
            self_path = "/" + rel(f)
            self_path = self_path[:-len("index.html")] if self_path.endswith("/index.html") else self_path
            if self_path not in back:
                errors.append(f"{name}: hreflang partner {href} does not point back to this page")
        codes = [c for c, _ in p.alternates]
        if p.alternates and ("en" not in codes or "de" not in codes):
            errors.append(f"{name}: hreflang set lacks en or de")

        body = re.sub(r"<!--.*?-->", "", raw, flags=re.S)
        body_p = Page()
        body_p.feed(body)
        text = "".join(body_p.text)
        for m in re.finditer(r"\[[^\]\[]+\]", text):
            warnings.append(f"{name}: {m.group(0)}")

    root_index = ROOT / "index.html"
    if root_index.is_file():
        raw = root_index.read_text(encoding="utf-8")
        redirect = raw.find('<script src="/assets/lang-redirect.js"></script>')
        sheet = raw.find('<link rel="stylesheet"')
        if redirect < 0:
            errors.append("index.html: does not load /assets/lang-redirect.js synchronously in <head>")
        elif sheet >= 0 and redirect > sheet:
            errors.append("index.html: lang-redirect.js must be loaded before the stylesheet")
        if not re.search(r'<noscript>\s*<meta http-equiv="refresh" content="0;\s*url=/en/">\s*</noscript>', raw):
            errors.append('index.html: missing <noscript><meta http-equiv="refresh" content="0; url=/en/"></noscript>')
        if not (ROOT / "assets" / "lang-redirect.js").is_file():
            errors.append("assets/lang-redirect.js is missing")

    cname = ROOT / "CNAME"
    if not cname.is_file() or cname.read_text() != DOMAIN:
        errors.append("CNAME must contain exactly '%s' (no trailing newline)" % DOMAIN)
    if not (ROOT / ".nojekyll").is_file():
        errors.append(".nojekyll is missing")

    print(f"checked {len(html_files)} HTML files")
    if warnings:
        print(f"\n{len(warnings)} placeholder(s) remaining (warnings):")
        for w in warnings:
            print("  [warn] " + w)
    if errors:
        print(f"\n{len(errors)} error(s):")
        for e in errors:
            print("  [FAIL] " + e)
        return 1
    print("\nOK: all internal links, anchors and hreflang pairs resolve; no external resources.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
