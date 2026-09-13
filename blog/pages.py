from __future__ import annotations

import datetime
import hashlib
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .markdown_render import render_doc

_MIN_DATE = datetime.date.min

# Trilingual notice shown when a page falls back to the default language.
NOTICE = {
    "zh": "本页暂无该语言译文，已显示默认语言版本。",
    "en": "This page is not yet available in this language; showing the default version.",
    "ja": "このページはこの言語の翻訳がまだありません。デフォルト版を表示しています。",
}


def lang_url(lang: str, *parts: str) -> str:
    segs = [lang, *[p for p in parts if p]]
    return "/" + "/".join(segs) + "/"


def make_env(templates_dir: Path) -> Environment:
    site_root = Path(templates_dir).resolve().parent

    def asset_url(path: str) -> str:
        """Keep unchanged assets cacheable; give new content a new URL."""
        asset = site_root / path.lstrip("/")
        version = hashlib.sha256(asset.read_bytes()).hexdigest()[:12]
        return f"{path}?v={version}"

    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=select_autoescape(["html"]),
    )
    env.globals["lang_url"] = lang_url
    env.globals["asset_url"] = asset_url
    env.globals["now_year"] = datetime.date.today().year
    return env


def _write(out_dir: Path, rel: str, html: str) -> None:
    dest = Path(out_dir) / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html, encoding="utf-8")


def render_root_redirect(env, site, out_dir):
    html = env.get_template("redirect.html").render(site=site)
    _write(out_dir, "index.html", html)


def _sorted_posts(items):
    posts = [i for i in items if i.type == "post"]
    return sorted(posts, key=lambda i: (i.date or _MIN_DATE), reverse=True)


def render_home(env, site, items, lang, out_dir):
    works = sorted(
        [i for i in items if i.type == "work" and i.show_on_home],
        key=lambda i: (i.order if i.order is not None else 9999),
    )
    recent = _sorted_posts(items)[:5]
    careers = sorted(
        [i for i in items if i.type == "career"],
        key=lambda i: (i.order if i.order is not None else 9999),
    )
    professional_projects = [i for i in careers if i.project_url and i.show_on_home]
    html = env.get_template("home.html").render(
        site=site, lang=lang, section="home", page_path="",
        page_title=site.home.get("page_title", {}).get(lang, site.title),
        works=works, recent_posts=recent, careers=careers[:2],
        professional_projects=professional_projects,
    )
    _write(out_dir, f"{lang}/index.html", html)


def render_work(env, site, item, lang, out_dir):
    doc = render_doc(item.translations[lang].body_md)
    html = env.get_template("work.html").render(
        site=site, lang=lang, section="works",
        page_path=f"works/{item.slug}/", page_title=f"{item.translations[lang].title} · {site.title}",
        item=item, tr=item.translations[lang], body=doc.html,
        reading_minutes=doc.reading_minutes,
        missing=lang in item.missing_langs, notice_text=NOTICE.get(lang, ""),
    )
    _write(out_dir, f"{lang}/works/{item.slug}/index.html", html)


def render_post(env, site, item, lang, out_dir):
    doc = render_doc(item.translations[lang].body_md)
    html = env.get_template("post.html").render(
        site=site, lang=lang, section="posts",
        page_path=f"posts/{item.slug}/", page_title=f"{item.translations[lang].title} · {site.title}",
        item=item, tr=item.translations[lang], body=doc.html,
        reading_minutes=doc.reading_minutes,
        missing=lang in item.missing_langs, notice_text=NOTICE.get(lang, ""),
    )
    _write(out_dir, f"{lang}/posts/{item.slug}/index.html", html)


def render_post_list(env, site, posts, lang, out_dir):
    ordered = sorted(posts, key=lambda i: (i.date or _MIN_DATE), reverse=True)
    html = env.get_template("post_list.html").render(
        site=site, lang=lang, section="posts", page_path="posts/",
        page_title=f"{site.nav['posts'][lang]} · {site.title}", posts=ordered,
    )
    _write(out_dir, f"{lang}/posts/index.html", html)


def render_career_list(env, site, items, lang, out_dir):
    ordered = sorted(items, key=lambda i: (i.date or _MIN_DATE), reverse=True)
    html = env.get_template("career_list.html").render(
        site=site, lang=lang, section="career", page_path="career/",
        page_title=f"{site.nav['career'][lang]} · {site.title}", items=ordered,
    )
    _write(out_dir, f"{lang}/career/index.html", html)


def render_career(env, site, item, lang, out_dir):
    doc = render_doc(item.translations[lang].body_md)
    html = env.get_template("career.html").render(
        site=site, lang=lang, section="career",
        page_path=f"career/{item.slug}/", page_title=f"{item.translations[lang].title} · {site.title}",
        item=item, tr=item.translations[lang], body=doc.html,
        missing=lang in item.missing_langs, notice_text=NOTICE.get(lang, ""),
    )
    _write(out_dir, f"{lang}/career/{item.slug}/index.html", html)


def render_page(env, site, item, lang, out_dir):
    doc = render_doc(item.translations[lang].body_md)
    html = env.get_template("page.html").render(
        site=site, lang=lang, section=item.slug,
        page_path=f"{item.slug}/", page_title=f"{item.translations[lang].title} · {site.title}",
        item=item, tr=item.translations[lang], body=doc.html,
        missing=lang in item.missing_langs, notice_text=NOTICE.get(lang, ""),
    )
    _write(out_dir, f"{lang}/{item.slug}/index.html", html)
