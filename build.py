from __future__ import annotations

import argparse
import functools
import http.server
import shutil
import socketserver
from pathlib import Path

from blog import pages
from blog.config import load_site_config
from blog.loader import load_all

ROOT = Path(__file__).resolve().parent
DEFAULT_SRC = ROOT / "src"
DEFAULT_TEMPLATES = ROOT / "templates"
DEFAULT_OUT = ROOT  # output at repo root


def build(src: Path = DEFAULT_SRC, templates: Path = DEFAULT_TEMPLATES, out: Path = DEFAULT_OUT):
    src, templates, out = Path(src), Path(templates), Path(out)
    site = load_site_config(src / "site.yml")

    # clean previous output (only the generated paths; never touch src/assets/etc.)
    (out / "index.html").unlink(missing_ok=True)
    for lang in site.languages:
        d = out / lang
        if d.exists():
            shutil.rmtree(d)

    items = load_all(src, site.languages, site.default_lang)
    careers = [i for i in items if i.type == "career"]
    works = [i for i in items if i.type == "work"]
    posts = [i for i in items if i.type == "post"]
    page_items = [i for i in items if i.type == "page"]

    env = pages.make_env(templates)
    for lang in site.languages:
        pages.render_home(env, site, items, lang, out)
        pages.render_career_list(env, site, careers, lang, out)
        for c in careers:
            pages.render_career(env, site, c, lang, out)
        for w in works:
            pages.render_work(env, site, w, lang, out)
        pages.render_post_list(env, site, posts, lang, out)
        for p in posts:
            pages.render_post(env, site, p, lang, out)
        for pg in page_items:
            pages.render_page(env, site, pg, lang, out)
    pages.render_root_redirect(env, site, out)

    print(f"Built {len(items)} items x {len(site.languages)} languages -> {out}")


def serve(out: Path = DEFAULT_OUT, port: int = 8000):
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(out))
    with socketserver.TCPServer(("127.0.0.1", port), handler) as httpd:
        print(f"Serving http://127.0.0.1:{port}/  (Ctrl+C to stop)")
        httpd.serve_forever()


def main():
    ap = argparse.ArgumentParser(description="Build the trilingual static blog.")
    ap.add_argument("--serve", action="store_true", help="serve after building")
    ap.add_argument("--port", type=int, default=8000)
    args = ap.parse_args()
    build()
    if args.serve:
        serve(port=args.port)


if __name__ == "__main__":
    main()
