import datetime
from pathlib import Path

import pytest

from blog.config import SiteConfig
from blog.loader import ContentItem, Translation

TEMPLATES = Path(__file__).resolve().parent.parent / "templates"


@pytest.fixture
def templates_dir():
    return TEMPLATES


@pytest.fixture
def site():
    return SiteConfig(
        title="cortexA233",
        default_lang="en",
        languages=["zh", "en", "ja"],
        lang_names={"zh": "中文", "en": "English", "ja": "日本語"},
        nav={
            "career": {"zh": "职业经历", "en": "Experience", "ja": "経歴"},
            "works": {"zh": "个人作品", "en": "Works", "ja": "作品"},
            "posts": {"zh": "随笔", "en": "Log", "ja": "随筆"},
            "resume": {"zh": "简历", "en": "Resume", "ja": "履歴書"},
            "about": {"zh": "关于我 About Me", "en": "About Me", "ja": "About Me"},
        },
        hero={
            "title": {"zh": "我做小游戏", "en": "I make small games", "ja": "小さなゲーム"},
            "sub": {"zh": "也写下想法", "en": "and write about them", "ja": "そして書く"},
        },
        social={"github": "https://github.com/cortexA233", "mail": "a@b.c"},
        work_groups={
            "game": {"zh": "游戏作品", "en": "Games", "ja": "ゲーム作品"},
            "other": {"zh": "其他", "en": "Other", "ja": "その他"},
        },
    )


def _tr(title):
    return Translation(title=title, summary="summary " + title, body_md="# H\n\nbody words here")


@pytest.fixture
def work_item():
    return ContentItem(
        type="work", slug="neon", date=datetime.date(2024, 1, 1),
        cover="/assets/img/neon.png", tags=["unity", "action"], order=1,
        translations={l: _tr("Neon " + l) for l in ["zh", "en", "ja"]},
        missing_langs=set(),
    )


@pytest.fixture
def tool_work_item():
    return ContentItem(
        type="work", slug="ktoolkit", date=datetime.date(2023, 7, 1),
        cover=None, tags=["engine"], order=1,
        translations={l: _tr("KTool " + l) for l in ["zh", "en", "ja"]},
        missing_langs=set(), category="other",
    )


@pytest.fixture
def post_item():
    return ContentItem(
        type="post", slug="buffering", date=datetime.date(2024, 5, 20),
        cover=None, tags=["unity"], order=None,
        translations={l: _tr("Buffering " + l) for l in ["zh", "en", "ja"]},
        missing_langs=set(),
    )


@pytest.fixture
def career_item():
    return ContentItem(
        type="career", slug="gameplay-programmer", date=datetime.date(2022, 6, 1),
        cover=None, tags=["unity"], order=1,
        translations={l: _tr("Programmer " + l) for l in ["zh", "en", "ja"]},
        missing_langs=set(),
    )


@pytest.fixture
def about_item():
    return ContentItem(
        type="page", slug="about", date=None,
        cover=None, tags=[], order=None,
        translations={l: _tr("About " + l) for l in ["zh", "en", "ja"]},
        missing_langs={"ja"},  # exercise the fallback notice
    )
