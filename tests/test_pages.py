from copy import deepcopy
from html.parser import HTMLParser
import os
import shutil
from urllib.parse import parse_qs, urlsplit

import pytest

from blog import pages
from blog.config import load_site_config


class RenderedTags(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.tags = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


def test_lang_url():
    assert pages.lang_url("en") == "/en/"
    assert pages.lang_url("en", "works", "neon") == "/en/works/neon/"
    assert pages.lang_url("zh", "posts") == "/zh/posts/"


def test_make_env_exposes_lang_url(templates_dir):
    env = pages.make_env(templates_dir)
    assert "lang_url" in env.globals
    assert env.globals["lang_url"]("ja", "about") == "/ja/about/"


def test_render_root_redirect(site, templates_dir, tmp_path):
    env = pages.make_env(templates_dir)
    pages.render_root_redirect(env, site, tmp_path)
    out = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert "location.replace" in out
    assert '"en"' in out          # default lang appears in the tojson list
    assert "/en/" in out          # noscript / fallback link


def test_render_home(site, work_item, post_item, templates_dir, tmp_path):
    env = pages.make_env(templates_dir)
    pages.render_home(env, site, [work_item, post_item], "en", tmp_path)
    out = (tmp_path / "en" / "index.html").read_text(encoding="utf-8")
    assert "cortexA233" in out
    assert "I make small games" in out            # hero
    assert "Neon en" in out                        # work card
    assert "/en/works/neon/" in out
    assert "Buffering en" in out                   # recent post
    assert 'class="lang active"' in out            # active language marker


@pytest.mark.parametrize("lang", ["zh", "en", "ja"])
def test_home_highlights_first_game_and_keeps_other_entries_once(
        site, work_item, tool_work_item, templates_dir, tmp_path, lang):
    later_game = deepcopy(work_item)
    later_game.slug = "later-game"
    later_game.order = 2
    for translation in later_game.translations.values():
        translation.title = "Later game"
        translation.summary = "A second playable prototype"
    env = pages.make_env(templates_dir)

    pages.render_home(env, site, [later_game, tool_work_item, work_item], lang, tmp_path)
    out = (tmp_path / lang / "index.html").read_text(encoding="utf-8")

    assert f'id="featured-work-title">Neon {lang}</h3>' in out
    assert f"summary Neon {lang}" in out
    assert "A second playable prototype" in out
    assert out.index(f"Neon {lang}</h3>") < out.index("Later game</h3>")
    for slug in ["neon", "later-game", "ktoolkit"]:
        assert out.count(f'href="/{lang}/works/{slug}/"') == 1


@pytest.mark.parametrize("lang", ["zh", "en", "ja"])
def test_home_shows_two_ordered_career_summaries_with_localized_links(
        site, career_item, post_item, templates_dir, tmp_path, lang):
    older = deepcopy(career_item)
    older.slug, older.order = "older-studio", 2
    oldest = deepcopy(career_item)
    oldest.slug, oldest.order = "oldest-studio", 3
    env = pages.make_env(templates_dir)

    pages.render_home(env, site, [oldest, post_item, older, career_item], lang, tmp_path)
    out = (tmp_path / lang / "index.html").read_text(encoding="utf-8")

    assert f"summary Programmer {lang}" in out
    assert out.index(f'href="/{lang}/career/gameplay-programmer/"') < out.index(
        f'href="/{lang}/career/older-studio/"')
    assert f'href="/{lang}/career/oldest-studio/"' not in out
    assert f'href="/{lang}/posts/buffering/"' in out


def test_render_home_uses_deferred_showreel_as_hero_background_for_every_language(
        site, work_item, post_item, templates_dir, tmp_path):
    env = pages.make_env(templates_dir)

    for lang in ["zh", "en", "ja"]:
        pages.render_home(env, site, [work_item, post_item], lang, tmp_path)
        out = (tmp_path / lang / "index.html").read_text(encoding="utf-8")

        hero_start = out.index('<section class="hero hero-showreel">')
        hero_end = out.index("</section>", hero_start)
        video_position = out.index('class="hero-video"', hero_start)

        assert '<body class="page-home">' in out
        assert 'class="home-backdrop"' in out
        assert hero_start < video_position < hero_end
        assert 'class="showreel"' not in out
        assert "autoplay muted loop playsinline" in out
        assert 'preload="none"' in out
        assert 'data-src="/assets/video/homepage-showreel.mp4?v=' in out
        assert 'data-desktop-src="/assets/video/homepage-showreel-desktop.mp4?v=' in out
        assert 'poster="/assets/img/homepage-showreel-poster.jpg?v=' in out
        assert 'href="/assets/css/style.css?v=' in out


@pytest.mark.parametrize("updated_rendition", ["mobile", "desktop"])
def test_home_showreel_url_changes_only_when_video_content_changes(
        site, templates_dir, tmp_path, updated_rendition):
    local_templates = tmp_path / "templates"
    shutil.copytree(templates_dir, local_templates)
    video_dir = tmp_path / "assets" / "video"
    video_dir.mkdir(parents=True)
    videos = {
        "mobile": video_dir / "homepage-showreel.mp4",
        "desktop": video_dir / "homepage-showreel-desktop.mp4",
    }
    for video in videos.values():
        video.write_bytes(b"first clip")
    poster = tmp_path / "assets" / "img" / "homepage-showreel-poster.jpg"
    poster.parent.mkdir()
    poster.write_bytes(b"poster")
    video = videos[updated_rendition]
    original_stat = video.stat()

    def render_urls():
        env = pages.make_env(local_templates)
        out_dir = tmp_path / "out"
        urls = []
        for lang in ["zh", "en", "ja"]:
            pages.render_home(env, site, [], lang, out_dir)
            html = (out_dir / lang / "index.html").read_text(encoding="utf-8")
            sources = [attrs for tag, attrs in RenderedTags(html).tags
                       if tag == "source" and attrs.get("type") == "video/mp4"]
            assert len(sources) == 1
            assert "src" not in sources[0]  # Keep deferred loading.
            renditions = {"mobile": sources[0]["data-src"],
                          "desktop": sources[0]["data-desktop-src"]}
            for key, url in renditions.items():
                parsed = urlsplit(url)
                assert parsed.path == f"/assets/video/{videos[key].name}"
                assert parse_qs(parsed.query).get("v"), "the video URL must be versioned"
            urls.append(renditions)
        assert urls[0] == urls[1] == urls[2]  # Languages share cached renditions.
        return urls[0]

    original_urls = render_urls()
    # Touching an unchanged file must not force visitors to download it again.
    os.utime(video, ns=(original_stat.st_atime_ns, original_stat.st_mtime_ns + 10**9))
    assert render_urls() == original_urls

    # A new edit with the same filename, size and timestamp still needs a new URL.
    video.write_bytes(b"other clip")
    os.utime(video, ns=(original_stat.st_atime_ns, original_stat.st_mtime_ns))
    updated_urls = render_urls()
    assert updated_urls[updated_rendition] != original_urls[updated_rendition]
    unchanged_rendition = "desktop" if updated_rendition == "mobile" else "mobile"
    assert updated_urls[unchanged_rendition] == original_urls[unchanged_rendition]
    assert render_urls() == updated_urls


@pytest.mark.parametrize("lang, works_label, resume_label, pause_label, play_label", [
    ("zh", "探索我的作品", "查看简历", "暂停视频", "播放视频"),
    ("en", "Explore my work", "View resume", "Pause video", "Play video"),
    ("ja", "作品を見る", "履歴書を見る", "動画を一時停止", "動画を再生"),
])
def test_home_has_localized_actions_and_an_accessible_video_control(
        work_item, templates_dir, tmp_path, lang, works_label, resume_label, pause_label, play_label):
    site = load_site_config(templates_dir.parent / "src" / "site.yml")
    env = pages.make_env(templates_dir)
    pages.render_home(env, site, [work_item], lang, tmp_path)
    out = (tmp_path / lang / "index.html").read_text(encoding="utf-8")

    assert f'href="#works">{works_label}' in out
    assert f'href="/{lang}/resume/">{resume_label}' in out
    assert 'aria-controls="home-showreel"' in out
    assert 'id="home-showreel"' in out
    assert f'data-pause-label="{pause_label}"' in out
    assert f'data-play-label="{play_label}"' in out


def test_render_home_groups_works_by_category(site, work_item, tool_work_item, templates_dir, tmp_path):
    env = pages.make_env(templates_dir)
    pages.render_home(env, site, [work_item, tool_work_item], "en", tmp_path)
    out = (tmp_path / "en" / "index.html").read_text(encoding="utf-8")
    assert "Games" in out          # game group heading
    assert "Other" in out          # other group heading
    assert "Neon en" in out        # game work
    assert "KTool en" in out       # other work (engine/renderer category)


def test_render_work(site, work_item, templates_dir, tmp_path):
    env = pages.make_env(templates_dir)
    pages.render_work(env, site, work_item, "ja", tmp_path)
    out = (tmp_path / "ja" / "works" / "neon" / "index.html").read_text(encoding="utf-8")
    assert "Neon ja" in out
    assert "min" in out               # reading time rendered
    assert "<h1" in out               # markdown body rendered
    assert "neon.png" in out          # cover image


def test_render_post(site, post_item, templates_dir, tmp_path):
    env = pages.make_env(templates_dir)
    pages.render_post(env, site, post_item, "en", tmp_path)
    out = (tmp_path / "en" / "posts" / "buffering" / "index.html").read_text(encoding="utf-8")
    assert "Buffering en" in out
    assert "2024-05-20" in out        # ISO date
    assert "min" in out


def test_render_post_list(site, post_item, templates_dir, tmp_path):
    env = pages.make_env(templates_dir)
    pages.render_post_list(env, site, [post_item], "zh", tmp_path)
    out = (tmp_path / "zh" / "posts" / "index.html").read_text(encoding="utf-8")
    assert "Buffering zh" in out
    assert "/zh/posts/buffering/" in out
    assert "随笔" in out               # section title from nav


def test_render_career_list(site, career_item, templates_dir, tmp_path):
    env = pages.make_env(templates_dir)
    pages.render_career_list(env, site, [career_item], "zh", tmp_path)
    out = (tmp_path / "zh" / "career" / "index.html").read_text(encoding="utf-8")
    assert "Programmer zh" in out
    assert "/zh/career/gameplay-programmer/" in out
    assert "职业经历" in out             # section + nav label


def test_render_career(site, career_item, templates_dir, tmp_path):
    env = pages.make_env(templates_dir)
    pages.render_career(env, site, career_item, "en", tmp_path)
    out = (tmp_path / "en" / "career" / "gameplay-programmer" / "index.html").read_text(encoding="utf-8")
    assert "Programmer en" in out
    assert "2022-06-01" in out
    assert "Experience" in out          # career kicker / nav label


def test_render_page_with_fallback_notice(site, about_item, templates_dir, tmp_path):
    env = pages.make_env(templates_dir)
    # about_item.missing_langs == {"ja"}
    pages.render_page(env, site, about_item, "ja", tmp_path)
    out = (tmp_path / "ja" / "about" / "index.html").read_text(encoding="utf-8")
    assert "About ja" in out
    assert "lang-notice" in out                # fallback notice shown
    assert "デフォルト版" in out                # Japanese notice text

    pages.render_page(env, site, about_item, "en", tmp_path)
    out_en = (tmp_path / "en" / "about" / "index.html").read_text(encoding="utf-8")
    assert "lang-notice" not in out_en         # en is not missing


@pytest.mark.parametrize("lang, language_label, navigation_label", [
    ("zh", "切换语言", "主导航"),
    ("en", "Choose language", "Main navigation"),
    ("ja", "言語切り替え", "メインナビゲーション"),
])
def test_language_switch_identifies_each_language_and_current_page(
        work_item, templates_dir, tmp_path, lang, language_label, navigation_label):
    site = load_site_config(templates_dir.parent / "src" / "site.yml")
    env = pages.make_env(templates_dir)

    pages.render_work(env, site, work_item, lang, tmp_path)
    html = (tmp_path / lang / "works" / "neon" / "index.html").read_text(encoding="utf-8")
    tags = RenderedTags(html).tags

    navigation = {attrs["class"]: attrs for tag, attrs in tags if tag == "nav"}
    assert navigation["lang-switch"]["aria-label"] == language_label
    assert navigation["main-nav"]["aria-label"] == navigation_label
    language_links = [attrs for tag, attrs in tags
                      if tag == "a" and "lang" in attrs.get("class", "").split()]
    assert len(language_links) == 3
    assert {link.get("lang"): link["href"] for link in language_links} == {
        "zh": "/zh/works/neon/",
        "en": "/en/works/neon/",
        "ja": "/ja/works/neon/",
    }
    for link in language_links:
        assert link.get("hreflang") == link["lang"]
        assert link.get("aria-current") == ("page" if link["lang"] == lang else None)
