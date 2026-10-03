"""mdlite: a small, dependency-free Markdown renderer for site content.

Supports exactly what content writers are allowed to use (see content-engine skill):
  front matter (--- key: value ---), # headings (with auto ids), paragraphs, **bold**, *italic*,
  `code`, [links](url), ![images](src "title"), - / * / 1. lists (one nesting level), > blockquotes,
  GFM pipe tables, --- rules, ``` fenced code, raw HTML blocks, and [[shortcode]] lines.
"""
import html
import re

BLOCK_HTML = re.compile(r"^\s*<(div|section|figure|table|details|aside|iframe|p|ul|ol|h[1-6]|blockquote|hr|!--)", re.I)
SHORTCODE = re.compile(r"^\s*\[\[\s*([a-z][a-z0-9_-]*)\s*(?::\s*(.*?))?\s*\]\]\s*$", re.I)
UL_ITEM = re.compile(r"^(\s*)[-*+]\s+(.*)$")
OL_ITEM = re.compile(r"^(\s*)(\d+)[.)]\s+(.*)$")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
TABLE_SEP = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$")


def parse_front_matter(text):
    """Return (meta dict, body). Values are strings; 'true'/'false' become bools."""
    meta = {}
    if text.startswith("﻿"):
        text = text[1:]
    if not text.startswith("---"):
        return meta, text
    end = re.search(r"^---\s*$", text[3:], re.M)
    if not end:
        return meta, text
    block = text[3:3 + end.start()]
    body = text[3 + end.end():].lstrip("\n")
    for line in block.splitlines():
        if not line.strip() or line.strip().startswith("#") or ":" not in line:
            continue
        key, val = line.split(":", 1)
        val = val.strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
            val = val[1:-1]
        if val.lower() in ("true", "yes"):
            val = True
        elif val.lower() in ("false", "no"):
            val = False
        meta[key.strip().lower()] = val
    return meta, body


def slug_id(text, used):
    base = re.sub(r"[^a-z0-9]+", "-", re.sub(r"<[^>]+>", "", text).lower()).strip("-") or "section"
    slug, i = base, 2
    while slug in used:
        slug, i = f"{base}-{i}", i + 1
    used.add(slug)
    return slug


def inline(text):
    """Escape, then apply inline markdown."""
    codes = []

    def keep_code(m):
        codes.append(f"<code>{html.escape(m.group(1))}</code>")
        return f"\x00{len(codes) - 1}\x00"

    text = re.sub(r"`([^`]+)`", keep_code, text)
    text = html.escape(text, quote=False)

    def img(m):
        alt, src, title = m.group(1), m.group(2), m.group(3)
        t = f' title="{html.escape(title)}"' if title else ""
        return (f'<img src="{html.escape(src, quote=True)}" alt="{html.escape(alt, quote=True)}"{t} '
                f'loading="lazy" decoding="async">')

    def link(m):
        label, href, title = m.group(1), m.group(2), m.group(3)
        attrs = f' title="{html.escape(title)}"' if title else ""
        if re.match(r"^https?://", href):
            attrs += ' rel="noopener"'
        return f'<a href="{html.escape(href, quote=True)}"{attrs}>{label}</a>'

    text = re.sub(r'!\[([^\]]*)\]\(\s*([^)\s]+)(?:\s+"([^"]*)")?\s*\)', img, text)
    text = re.sub(r'\[([^\]]+)\]\(\s*([^)\s]+)(?:\s+"([^"]*)")?\s*\)', link, text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"__(.+?)__", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", text)
    text = re.sub(r"(?<![\w_])_(?!\s)(.+?)(?<!\s)_(?![\w_])", r"<em>\1</em>", text)
    text = re.sub(r"  $", "<br>", text)
    return re.sub(r"\x00(\d+)\x00", lambda m: codes[int(m.group(1))], text)


def _split_row(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in re.split(r"(?<!\\)\|", line)]


def render(body, shortcode=None, used_ids=None):
    """Render markdown body to HTML. `shortcode(name, arg)` returns HTML for [[name: arg]] lines."""
    used = used_ids if used_ids is not None else set()
    lines = body.replace("\r\n", "\n").split("\n")
    out, i, n = [], 0, len(lines)

    def para_end(j):
        s = lines[j]
        return (not s.strip() or HEADING.match(s) or UL_ITEM.match(s) or OL_ITEM.match(s) or s.lstrip().startswith(">")
                or s.strip().startswith("```") or SHORTCODE.match(s) or BLOCK_HTML.match(s)
                or re.match(r"^\s*(-{3,}|\*{3,})\s*$", s)
                or ("|" in s and j + 1 < n and TABLE_SEP.match(lines[j + 1])))

    while i < n:
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.strip().startswith("```"):
            buf, i = [], i + 1
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(lines[i])
                i += 1
            out.append("<pre><code>" + html.escape("\n".join(buf)) + "</code></pre>")
            i += 1
            continue
        m = SHORTCODE.match(line)
        if m:
            out.append(shortcode(m.group(1).lower(), m.group(2)) if shortcode else "")
            i += 1
            continue
        m = HEADING.match(line)
        if m:
            level, text = len(m.group(1)), m.group(2)
            rendered = inline(text)
            out.append(f'<h{level} id="{slug_id(text, used)}">{rendered}</h{level}>')
            i += 1
            continue
        if re.match(r"^\s*(-{3,}|\*{3,})\s*$", line):
            out.append("<hr>")
            i += 1
            continue
        if BLOCK_HTML.match(line):
            buf = []
            while i < n and lines[i].strip():
                buf.append(lines[i])
                i += 1
            out.append("\n".join(buf))
            continue
        if "|" in line and i + 1 < n and TABLE_SEP.match(lines[i + 1]):
            head = _split_row(line)
            i += 2
            rows = []
            while i < n and "|" in lines[i] and lines[i].strip():
                rows.append(_split_row(lines[i]))
                i += 1
            th = "".join(f"<th>{inline(c)}</th>" for c in head)
            trs = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rows)
            out.append(f'<div class="table-wrap"><table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>')
            continue
        if line.lstrip().startswith(">"):
            buf = []
            while i < n and lines[i].lstrip().startswith(">"):
                buf.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            out.append("<blockquote>" + render("\n".join(buf), shortcode, used) + "</blockquote>")
            continue
        if UL_ITEM.match(line) or OL_ITEM.match(line):
            html_list, i = _render_list(lines, i)
            out.append(html_list)
            continue
        buf = [line.strip()]
        i += 1
        while i < n and not para_end(i):
            buf.append(lines[i].strip())
            i += 1
        out.append("<p>" + inline(" ".join(buf)) + "</p>")
    return "\n".join(out)


def _render_list(lines, i):
    n = len(lines)
    first = UL_ITEM.match(lines[i]) or OL_ITEM.match(lines[i])
    ordered = bool(OL_ITEM.match(lines[i]))
    base_indent = len(first.group(1))
    tag = "ol" if ordered else "ul"
    items = []
    while i < n:
        line = lines[i]
        m = (OL_ITEM if ordered else UL_ITEM).match(line)
        if m and len(m.group(1)) == base_indent:
            items.append([m.group(3) if ordered else m.group(2), []])
            i += 1
            continue
        sub = UL_ITEM.match(line) or OL_ITEM.match(line)
        if sub and len(sub.group(1)) > base_indent and items:
            sub_html, i = _render_list(lines, i)
            items[-1][1].append(sub_html)
            continue
        if line.strip() and line.startswith(" " * (base_indent + 2)) and items:
            items[-1][0] += " " + line.strip()  # lazy continuation line
            i += 1
            continue
        break
    body = "".join(f"<li>{inline(text)}{''.join(children)}</li>" for text, children in items)
    return f"<{tag}>{body}</{tag}>", i


def strip_tags(html_text):
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html_text, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()
