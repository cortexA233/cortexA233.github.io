from html.parser import HTMLParser
from pathlib import Path

import pytest

import build as build_mod

SITE_YML = """\
title: cortexA233
default_lang: en
languages: [zh, en, ja]
lang_names: {zh: 中文, en: English, ja: 日本語}
nav:
  career: {zh: 职业经历, en: Experience, ja: 経歴}
  works: {zh: 个人作品, en: Works, ja: 作品}
  posts: {zh: 随笔, en: Log, ja: 随筆}
  resume: {zh: 简历, en: Resume, ja: 履歴書}
  about: {zh: 关于我 About Me, en: About Me, ja: About Me}
work_groups:
  game: {zh: 游戏作品, en: Games, ja: ゲーム作品}
  other: {zh: 其他, en: Other, ja: その他}
hero:
  title: {zh: 我做小游戏, en: I make small games, ja: 小さなゲーム}
  sub: {zh: 也写下想法, en: and write about them, ja: そして書く}
social: {github: https://github.com/cortexA233, mail: a@b.c}
"""

TEMPLATES = Path(__file__).resolve().parent.parent / "templates"


@pytest.mark.parametrize("lang, heading, titles", [
    ("zh", "参与开发", ["遗忘之海", "闪耀暖暖", "明日之后"]),
    ("en", "Professional Work", ["Sea of Remnants", "Shining Nikki", "LifeAfter"]),
    ("ja", "開発参加作品", ["シー オブ レムナンツ", "シャイニングニキ", "ライフアフター"]),
])
def test_home_presents_commercial_contributions_before_independent_games(
        tmp_path, lang, heading, titles):
    build_mod.build(out=tmp_path)
    home = (tmp_path / lang / "index.html").read_text(encoding="utf-8")

    assert 'href="#professional"' in home
    start = home.index('id="professional"')
    end = home.index('id="works"')
    assert start < end
    professional = home[start:end]
    assert heading in professional
    positions = [professional.index(f">{title}</h3>") for title in titles]
    assert positions == sorted(positions)
    for slug, url in [
        ("netease", "https://www.seaofremnants.com/"),
        ("papergames", "https://nikki4.playpapergames.com/home"),
        ("netease-internship", "https://www.lifeafter.game/"),
    ]:
        assert f'href="{url}"' in professional
        assert home.count(f'href="/{lang}/career/{slug}/"') == 1
    for period in ["2023.11 – 2025.05", "2020.12 – 2023.06", "2020.07 – 2020.09"]:
        assert period in professional
    assert "C++" in professional and "Unity" in professional and "Python" in professional
    assert f'href="/{lang}/career/"' in professional
    assert 'id="featured-work-title">Exp10sion</h3>' in home[end:]


class HeadLinks(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.in_head = False
        self.links = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        if tag == "head":
            self.in_head = True
        elif tag == "link" and self.in_head:
            self.links.append(dict(attrs))

    def handle_endtag(self, tag):
        if tag == "head":
            self.in_head = False


def test_exp10sion_store_links_are_direct_and_consistent_across_languages(tmp_path):
    class PageLinks(HTMLParser):
        def __init__(self, html):
            super().__init__()
            self.inside_link = False
            self.links = []
            self.feed(html)

        def handle_starttag(self, tag, attrs):
            if tag == "a":
                assert not self.inside_link, "store buttons must not be nested inside the project link"
                self.inside_link = True
                self.links.append(dict(attrs).get("href", ""))

        def handle_endtag(self, tag):
            if tag == "a":
                self.inside_link = False

    build_mod.build(out=tmp_path)
    nintendo = "https://www.nintendo.com/us/store/products/10-second-ghost-switch/"
    for lang in ["zh", "en", "ja"]:
        for page in ["index.html", "works/exp10sion/index.html", "resume/index.html"]:
            html = (tmp_path / lang / page).read_text(encoding="utf-8")
            links = PageLinks(html).links
            assert links.count(nintendo) == 1
            assert any(url.startswith("https://store.steampowered.com/app/2618850") for url in links)
            assert "store-jp.nintendo.com/item/software/D70010000086469" not in html


@pytest.mark.parametrize("lang, role, contact_title", [
    ("zh", "游戏玩法/系统程序员", "联系我"),
    ("en", "Gameplay / Systems Programmer", "Get in touch"),
    ("ja", "ゲームプレイ・システムプログラマー", "お問い合わせ"),
])
def test_game_programming_profile_and_contact_routes_are_consistent(
        tmp_path, lang, role, contact_title):
    build_mod.build(out=tmp_path)
    home = (tmp_path / lang / "index.html").read_text(encoding="utf-8")
    assert f'class="hero-role">{role}</p>' in home
    assert home.count('class="hero-summary-line"') == 3
    assert "Mengxiang Wang" in home[:home.index('id="professional"')]
    assert 'href="#contact"' in home
    start = home.index('id="contact"')
    assert start > home.index('id="works"')
    contact = home[start:home.index('</section>', start)]
    assert contact_title in contact
    assert f'href="/{lang}/resume/"' in contact

    destinations = [
        "mailto:cortexA233@outlook.com",
        "https://github.com/cortexA233",
        "https://www.linkedin.com/in/mengxiang-wang-b4b0a4381/",
    ]
    for url in destinations:
        assert f'href="{url}"' in contact
    for page in ["resume", "about"]:
        html = (tmp_path / lang / page / "index.html").read_text(encoding="utf-8")
        main = html.split('<main class="site-main">', 1)[1].split('</main>', 1)[0]
        assert role in main
        assert "Mengxiang Wang" in main
        for url in destinations:
            assert f'href="{url}"' in main
    for page in (tmp_path / lang).rglob('*.html'):
        html = page.read_text(encoding="utf-8")
        footer = html.split('<footer class="site-footer">', 1)[1]
        for url in destinations:
            assert f'href="{url}"' in footer


def _seed_src(src: Path):
    (src / "career" / "studio").mkdir(parents=True)
    (src / "works" / "neon").mkdir(parents=True)
    (src / "posts" / "hello").mkdir(parents=True)
    (src / "pages" / "about").mkdir(parents=True)
    (src / "site.yml").write_text(SITE_YML, encoding="utf-8")
    (src / "career" / "studio" / "meta.yml").write_text(
        "slug: studio\ndate: 2022-06-01\n", encoding="utf-8")
    (src / "works" / "neon" / "meta.yml").write_text(
        "slug: neon\ndate: 2024-01-01\ntags: [unity]\norder: 1\n", encoding="utf-8")
    (src / "posts" / "hello" / "meta.yml").write_text(
        "slug: hello\ndate: 2024-05-20\n", encoding="utf-8")
    for l in ["zh", "en", "ja"]:
        (src / "career" / "studio" / f"{l}.md").write_text(
            f"---\ntitle: Studio {l}\n---\nrole", encoding="utf-8")
        (src / "works" / "neon" / f"{l}.md").write_text(
            f"---\ntitle: Neon {l}\n---\n# hi", encoding="utf-8")
        (src / "posts" / "hello" / f"{l}.md").write_text(
            f"---\ntitle: Hello {l}\n---\nbody", encoding="utf-8")
        (src / "pages" / "about" / f"{l}.md").write_text(
            f"---\ntitle: About {l}\n---\nme", encoding="utf-8")


def test_build_creates_all_languages(tmp_path):
    src = tmp_path / "src"
    out = tmp_path / "out"
    out.mkdir()
    _seed_src(src)
    build_mod.build(src=src, templates=TEMPLATES, out=out)

    assert (out / "index.html").exists()
    for l in ["zh", "en", "ja"]:
        assert (out / l / "index.html").exists()
        assert (out / l / "career" / "index.html").exists()
        assert (out / l / "career" / "studio" / "index.html").exists()
        assert (out / l / "works" / "neon" / "index.html").exists()
        assert (out / l / "posts" / "index.html").exists()
        assert (out / l / "posts" / "hello" / "index.html").exists()
        assert (out / l / "about" / "index.html").exists()


def test_build_is_idempotent_and_cleans_stale(tmp_path):
    src = tmp_path / "src"
    out = tmp_path / "out"
    out.mkdir()
    _seed_src(src)
    build_mod.build(src=src, templates=TEMPLATES, out=out)
    stale = out / "en" / "works" / "ghost" / "index.html"
    stale.parent.mkdir(parents=True)
    stale.write_text("stale", encoding="utf-8")
    build_mod.build(src=src, templates=TEMPLATES, out=out)
    assert not stale.exists()           # stale output removed on rebuild
    assert (out / "en" / "works" / "neon" / "index.html").exists()


def test_build_omits_unlisted_work_from_home_but_preserves_its_detail_pages(tmp_path):
    src, out = tmp_path / "src", tmp_path / "out"
    _seed_src(src)
    (src / "works" / "neon" / "meta.yml").write_text(
        "slug: neon\norder: 1\nshow_on_home: false\n", encoding="utf-8"
    )
    visible = src / "works" / "visible"
    visible.mkdir()
    (visible / "meta.yml").write_text("slug: visible\norder: 2\n", encoding="utf-8")
    for lang in ["zh", "en", "ja"]:
        (visible / f"{lang}.md").write_text(
            f"---\ntitle: Visible {lang}\n---\nA listed project", encoding="utf-8"
        )

    build_mod.build(src=src, templates=TEMPLATES, out=out)

    for lang in ["zh", "en", "ja"]:
        home = (out / lang / "index.html").read_text(encoding="utf-8")
        assert f'href="/{lang}/works/neon/"' not in home
        assert f'id="featured-work-title">Visible {lang}</h3>' in home
        detail = (out / lang / "works" / "neon" / "index.html").read_text(encoding="utf-8")
        assert f"Neon {lang}" in detail


def test_build_publishes_reciprocal_language_urls_and_canonical_pages(tmp_path):
    src, out = tmp_path / "src", tmp_path / "out"
    _seed_src(src)
    (src / "site.yml").write_text(
        SITE_YML + "url: https://portfolio.example/\n", encoding="utf-8"
    )

    build_mod.build(src=src, templates=TEMPLATES, out=out)

    for page_path in ["", "career/", "career/studio/", "works/neon/",
                      "posts/", "posts/hello/", "about/"]:
        expected_alternates = {
            "zh": f"https://portfolio.example/zh/{page_path}",
            "en": f"https://portfolio.example/en/{page_path}",
            "ja": f"https://portfolio.example/ja/{page_path}",
            "x-default": f"https://portfolio.example/en/{page_path}",
        }
        for lang in ["zh", "en", "ja"]:
            html = (out / lang / page_path / "index.html").read_text(encoding="utf-8")
            links = HeadLinks(html).links
            assert {link["hreflang"]: link["href"] for link in links
                    if link.get("rel") == "alternate"} == expected_alternates
            assert [link["href"] for link in links if link.get("rel") == "canonical"] == [
                expected_alternates[lang]
            ]

    root_links = HeadLinks((out / "index.html").read_text(encoding="utf-8")).links
    assert {link["hreflang"]: link["href"] for link in root_links
            if link.get("rel") == "alternate"} == {
        "zh": "https://portfolio.example/zh/",
        "en": "https://portfolio.example/en/",
        "ja": "https://portfolio.example/ja/",
        "x-default": "https://portfolio.example/en/",
    }
    assert [link["href"] for link in root_links if link.get("rel") == "canonical"] == [
        "https://portfolio.example/en/"
    ]


@pytest.mark.parametrize("source_path, page_path", [
    ("career/studio", "career/studio"),
    ("works/neon", "works/neon"),
    ("posts/hello", "posts/hello"),
    ("pages/about", "about"),
])
def test_untranslated_pages_use_default_canonical_and_only_advertise_real_translations(
        tmp_path, source_path, page_path):
    src, out = tmp_path / "src", tmp_path / "out"
    _seed_src(src)
    (src / "site.yml").write_text(
        SITE_YML + "url: https://portfolio.example\n", encoding="utf-8"
    )
    (src / source_path / "ja.md").unlink()

    build_mod.build(src=src, templates=TEMPLATES, out=out)

    for lang in ["zh", "en", "ja"]:
        html = (out / lang / page_path / "index.html").read_text(encoding="utf-8")
        links = HeadLinks(html).links
        assert {link["hreflang"]: link["href"] for link in links
                if link.get("rel") == "alternate"} == {
            "zh": f"https://portfolio.example/zh/{page_path}/",
            "en": f"https://portfolio.example/en/{page_path}/",
            "x-default": f"https://portfolio.example/en/{page_path}/",
        }
        canonical_lang = "zh" if lang == "zh" else "en"
        assert [link["href"] for link in links if link.get("rel") == "canonical"] == [
            f"https://portfolio.example/{canonical_lang}/{page_path}/"
        ]
        if lang == "ja":
            assert 'class="lang-notice"' in html
            assert f'href="/ja/{page_path}/"' in html
