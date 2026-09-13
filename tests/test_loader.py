from blog.loader import parse_front_matter


def test_parse_front_matter_basic():
    text = "---\ntitle: Hello\nsummary: hi there\n---\n# Body\ntext"
    meta, body = parse_front_matter(text)
    assert meta["title"] == "Hello"
    assert meta["summary"] == "hi there"
    assert body.startswith("# Body")


def test_parse_front_matter_none():
    meta, body = parse_front_matter("# No front matter")
    assert meta == {}
    assert body == "# No front matter"


def test_parse_front_matter_body_with_hr():
    text = "---\ntitle: X\n---\nbefore\n\n---\n\nafter"
    meta, body = parse_front_matter(text)
    assert meta["title"] == "X"
    assert "before" in body and "after" in body


import datetime

from blog.loader import load_item, load_all


def _make_item_dir(base, langs, with_meta=True):
    d = base
    d.mkdir(parents=True, exist_ok=True)
    if with_meta:
        (d / "meta.yml").write_text(
            "slug: neon\ndate: 2024-01-15\ncover: /assets/img/neon.png\n"
            "tags: [unity, action]\norder: 2\n",
            encoding="utf-8",
        )
    for lang in langs:
        (d / f"{lang}.md").write_text(
            f"---\ntitle: Neon {lang}\nsummary: s {lang}\n---\n# Body {lang}",
            encoding="utf-8",
        )
    return d


def test_load_item_full(tmp_path):
    d = _make_item_dir(tmp_path / "neon", ["zh", "en", "ja"])
    item = load_item(d, "work", ["zh", "en", "ja"], "en")
    assert item.type == "work"
    assert item.slug == "neon"
    assert item.date == datetime.date(2024, 1, 15)
    assert item.cover == "/assets/img/neon.png"
    assert item.tags == ["unity", "action"]
    assert item.order == 2
    assert item.translations["ja"].title == "Neon ja"
    assert item.missing_langs == set()


def test_load_item_fallback_for_missing_lang(tmp_path, capsys):
    # only en + zh present; ja missing, default_lang=en
    d = _make_item_dir(tmp_path / "neon", ["zh", "en"])
    item = load_item(d, "work", ["zh", "en", "ja"], "en")
    assert item.missing_langs == {"ja"}
    assert item.translations["ja"].title == "Neon en"  # fell back to default
    assert "WARNING" in capsys.readouterr().out


def test_load_item_missing_default_raises(tmp_path):
    d = _make_item_dir(tmp_path / "neon", ["zh"])  # en (default) absent
    import pytest
    with pytest.raises(ValueError):
        load_item(d, "work", ["zh", "en", "ja"], "en")


def test_load_all_scans_types(tmp_path):
    src = tmp_path / "src"
    _make_item_dir(src / "works" / "neon", ["zh", "en", "ja"])
    p = src / "posts" / "hello"
    p.mkdir(parents=True)
    (p / "meta.yml").write_text("slug: hello\ndate: 2024-05-20\n", encoding="utf-8")
    for lang in ["zh", "en", "ja"]:
        (p / f"{lang}.md").write_text(f"---\ntitle: H {lang}\n---\nbody", encoding="utf-8")
    items = load_all(src, ["zh", "en", "ja"], "en")
    types = sorted(i.type for i in items)
    assert types == ["post", "work"]
