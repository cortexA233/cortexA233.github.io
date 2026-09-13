from blog.config import load_site_config

SITE_YML = """\
title: cortexA233
default_lang: en
languages: [zh, en, ja]
lang_names: {zh: 中文, en: English, ja: 日本語}
nav:
  works: {zh: 作品, en: Works, ja: 作品}
  posts: {zh: 随笔, en: Log, ja: 随筆}
  about: {zh: 关于我 About Me, en: About Me, ja: About Me}
hero:
  title: {zh: 我做小游戏, en: I make small games, ja: 小さなゲームを作る}
  sub: {zh: 也写下想法, en: and write about them, ja: そして書く}
social: {github: https://github.com/cortexA233, mail: a@b.c}
"""


def test_load_site_config(tmp_path):
    p = tmp_path / "site.yml"
    p.write_text(SITE_YML, encoding="utf-8")
    cfg = load_site_config(p)
    assert cfg.title == "cortexA233"
    assert cfg.default_lang == "en"
    assert cfg.languages == ["zh", "en", "ja"]
    assert cfg.lang_names["ja"] == "日本語"
    assert cfg.nav["works"]["en"] == "Works"
    assert cfg.hero["title"]["en"] == "I make small games"
    assert cfg.social["github"].endswith("cortexA233")


def test_load_homepage_labels_without_requiring_them_in_older_configs(tmp_path):
    p = tmp_path / "site.yml"
    p.write_text(SITE_YML, encoding="utf-8")
    assert load_site_config(p).home == {}

    p.write_text(SITE_YML + "home:\n  view_project: {zh: 查看项目, en: View project, ja: 詳細を見る}\n",
                 encoding="utf-8")
    assert load_site_config(p).home["view_project"]["ja"] == "詳細を見る"
