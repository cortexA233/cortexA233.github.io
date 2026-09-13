# 自定义三语静态博客 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 从零搭建一个由 Python 构建的中/英/日三语纯静态博客（脱离 Hexo），B1 纸感暖白视觉，作品展示为主 + 随笔 + 关于我，本地构建产物提交后部署到 GitHub Pages。

**Architecture:** 一个小型自有静态站点生成器。`blog/` 包内分四个职责单一的模块（配置、内容加载、Markdown 渲染、页面生成），`build.py` 编排它们；Jinja2 模板 + 手写 CSS 实现 B1 视觉；构建期为每种语言生成 `/zh/ /en/ /ja/` 完整页面树 + 根语言路由 `index.html`。共享静态资源放 `assets/` 直接被 HTML 引用，不经构建。

**Tech Stack:** Python 3.14 · markdown · pygments · pyyaml · jinja2 · pytest。运行时（浏览器）仅少量内联原生 JS（语言路由/偏好），无前端框架。

参考规范：`docs/superpowers/specs/2026-06-01-custom-i18n-static-blog-design.md`

---

## 文件结构总览

构建逻辑（手写）：
- `build.py` — 入口与编排，CLI（`--serve`）
- `blog/config.py` — 解析 `src/site.yml` → `SiteConfig`
- `blog/loader.py` — 扫描 `src/` → `ContentItem` 列表（含 front-matter 解析、缺译文回退）
- `blog/markdown_render.py` — Markdown → HTML + 阅读时长（纯函数）
- `blog/pages.py` — URL 助手、Jinja 环境、各类页面的生成函数

模板（Jinja2，`templates/`）：`base.html` `home.html` `work.html` `post.html` `post_list.html` `page.html` `redirect.html`

样式与资源（`assets/`）：`css/style.css`（B1）、`css/pygments.css`（代码高亮）、`img/`（图标、默认封面）

内容源（`src/`，作者编辑）：`site.yml`、`works/<slug>/`、`posts/<slug>/`、`pages/about/`

测试（`tests/`）：每个模块一个测试文件 + `conftest.py` 共享 fixtures。

构建产物（提交到仓库根）：`index.html`、`zh/ en/ ja/`。

---

## 数据模型（贯穿全程，类型须一致）

```python
# blog/config.py
@dataclass
class SiteConfig:
    title: str
    default_lang: str
    languages: list[str]
    lang_names: dict[str, str]            # {"zh": "中文", ...}
    nav: dict[str, dict[str, str]]        # {"works": {"zh": "作品", ...}, ...}
    hero: dict[str, dict[str, str]]       # {"title": {lang: ...}, "sub": {lang: ...}}
    social: dict[str, str]                # {"github": "...", "mail": "..."}

# blog/loader.py
@dataclass
class Translation:
    title: str
    summary: str
    body_md: str

@dataclass
class ContentItem:
    type: str                             # "work" | "post" | "page"
    slug: str
    date: datetime.date | None
    cover: str | None
    tags: list[str]
    order: int | None
    translations: dict[str, Translation]  # 每种语言都有（缺失时回退默认语言）
    missing_langs: set[str]               # 哪些语言用了回退

# blog/markdown_render.py
@dataclass
class RenderedDoc:
    html: str
    reading_minutes: int
```

---

## Task 1: 项目脚手架与清理旧 Hexo 产物

**Files:**
- Create: `requirements.txt`, `pyproject.toml`, `.nojekyll`, `blog/__init__.py`, `tests/__init__.py`
- Modify: `.gitignore`
- Delete: 旧 Hexo 产物

- [ ] **Step 1: 删除旧 Hexo 产物**

PowerShell（在仓库根）：
```powershell
Remove-Item -Recurse -Force 2022, 2023, archives, about, css, font, images, img, index.html
```
预期：这些路径被移除。`docs/`、`.git/`、`.gitignore`、`.superpowers/` 保留。

- [ ] **Step 2: 建立目录骨架**

```powershell
New-Item -ItemType Directory -Force blog, tests, templates, assets\css, assets\img, src\works, src\posts, src\pages | Out-Null
New-Item -ItemType File blog\__init__.py, tests\__init__.py, .nojekyll | Out-Null
```
预期：目录与空文件创建成功。`.nojekyll` 用于关闭 GitHub Pages 的 Jekyll 处理。

- [ ] **Step 3: 写 `requirements.txt`**

```
markdown>=3.5
pygments>=2.17
pyyaml>=6.0
jinja2>=3.1
pytest>=8.0
```

- [ ] **Step 4: 写 `pyproject.toml`（让 pytest 能 import `blog` 与 `build`）**

```toml
[tool.pytest.ini_options]
pythonpath = ["."]
testpaths = ["tests"]
```

- [ ] **Step 5: 更新 `.gitignore`**

文件内容（覆盖写）：
```
.superpowers/
.venv/
__pycache__/
*.pyc
.pytest_cache/
```

- [ ] **Step 6: 建虚拟环境并安装依赖**

PowerShell：
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```
预期：依赖安装成功。后续所有 `python` / `pytest` 命令均在此激活的 venv 中运行。

- [ ] **Step 7: 验证 pytest 可运行（暂无测试）**

Run: `python -m pytest -q`
预期：`no tests ran`（退出码 5 或 "collected 0 items"），无 import 错误。

- [ ] **Step 8: Commit**

```bash
git add .gitignore requirements.txt pyproject.toml .nojekyll blog/__init__.py tests/__init__.py
git commit -m "chore: scaffold project, remove legacy Hexo output"
```

---

## Task 2: front-matter 解析

**Files:**
- Create: `blog/loader.py`（先只放 `parse_front_matter`）
- Test: `tests/test_loader.py`

- [ ] **Step 1: 写失败测试**

`tests/test_loader.py`:
```python
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
```

- [ ] **Step 2: 运行测试，确认失败**

Run: `python -m pytest tests/test_loader.py -v`
预期：FAIL（`ImportError: cannot import name 'parse_front_matter'`）

- [ ] **Step 3: 实现**

`blog/loader.py`:
```python
from __future__ import annotations

import yaml


def parse_front_matter(text: str) -> tuple[dict, str]:
    """Split optional `---`-delimited YAML front matter from a Markdown body."""
    text = text.lstrip("﻿")  # strip BOM if present
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            meta = yaml.safe_load(parts[1]) or {}
            body = parts[2].lstrip("\n")
            return meta, body
    return {}, text
```

- [ ] **Step 4: 运行测试，确认通过**

Run: `python -m pytest tests/test_loader.py -v`
预期：3 passed

- [ ] **Step 5: Commit**

```bash
git add blog/loader.py tests/test_loader.py
git commit -m "feat: parse markdown front matter"
```

---

## Task 3: 站点配置加载（`SiteConfig`）

**Files:**
- Create: `blog/config.py`
- Test: `tests/test_config.py`

- [ ] **Step 1: 写失败测试**

`tests/test_config.py`:
```python
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
```

- [ ] **Step 2: 运行测试，确认失败**

Run: `python -m pytest tests/test_config.py -v`
预期：FAIL（`ModuleNotFoundError: No module named 'blog.config'`）

- [ ] **Step 3: 实现**

`blog/config.py`:
```python
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class SiteConfig:
    title: str
    default_lang: str
    languages: list[str]
    lang_names: dict[str, str]
    nav: dict[str, dict[str, str]]
    hero: dict[str, dict[str, str]]
    social: dict[str, str]


def load_site_config(path: Path) -> SiteConfig:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return SiteConfig(
        title=data["title"],
        default_lang=data["default_lang"],
        languages=list(data["languages"]),
        lang_names=dict(data["lang_names"]),
        nav=dict(data["nav"]),
        hero=dict(data["hero"]),
        social=dict(data.get("social", {})),
    )
```

- [ ] **Step 4: 运行测试，确认通过**

Run: `python -m pytest tests/test_config.py -v`
预期：1 passed

- [ ] **Step 5: Commit**

```bash
git add blog/config.py tests/test_config.py
git commit -m "feat: load site config from site.yml"
```

---

## Task 4: 内容加载（`ContentItem`，含缺译文回退）

**Files:**
- Modify: `blog/loader.py`（追加 `Translation`、`ContentItem`、`load_item`、`load_all`）
- Test: `tests/test_loader.py`（追加）

- [ ] **Step 1: 追加失败测试**

在 `tests/test_loader.py` 末尾追加：
```python
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
```

- [ ] **Step 2: 运行测试，确认失败**

Run: `python -m pytest tests/test_loader.py -v`
预期：新增用例 FAIL（`cannot import name 'load_item'`），前 3 个 front-matter 用例仍 PASS。

- [ ] **Step 3: 实现**

在 `blog/loader.py` 顶部 import 处补充，并在 `parse_front_matter` 之后追加：
```python
from dataclasses import dataclass, field
from pathlib import Path
import datetime


@dataclass
class Translation:
    title: str
    summary: str
    body_md: str


@dataclass
class ContentItem:
    type: str
    slug: str
    date: datetime.date | None
    cover: str | None
    tags: list[str]
    order: int | None
    translations: dict[str, Translation]
    missing_langs: set[str] = field(default_factory=set)


def load_item(item_dir: Path, item_type: str, languages: list[str], default_lang: str) -> ContentItem:
    item_dir = Path(item_dir)
    meta = {}
    meta_path = item_dir / "meta.yml"
    if meta_path.exists():
        meta = yaml.safe_load(meta_path.read_text(encoding="utf-8")) or {}
    slug = meta.get("slug", item_dir.name)

    translations: dict[str, Translation] = {}
    missing: set[str] = set()
    for lang in languages:
        md_path = item_dir / f"{lang}.md"
        if md_path.exists():
            fm, body = parse_front_matter(md_path.read_text(encoding="utf-8"))
            translations[lang] = Translation(
                title=fm.get("title", slug),
                summary=fm.get("summary", ""),
                body_md=body,
            )
        else:
            missing.add(lang)

    if default_lang not in translations:
        raise ValueError(
            f"{item_dir}: missing default language '{default_lang}' ({default_lang}.md)"
        )
    for lang in missing:
        print(f"WARNING: {item_dir} has no '{lang}' translation; falling back to '{default_lang}'")
        translations[lang] = translations[default_lang]

    date = meta.get("date")
    if isinstance(date, str):
        date = datetime.date.fromisoformat(date)

    return ContentItem(
        type=item_type,
        slug=slug,
        date=date,
        cover=meta.get("cover"),
        tags=list(meta.get("tags", [])),
        order=meta.get("order"),
        translations=translations,
        missing_langs=missing,
    )


_TYPE_DIRS = {"works": "work", "posts": "post", "pages": "page"}


def load_all(src_dir: Path, languages: list[str], default_lang: str) -> list[ContentItem]:
    items: list[ContentItem] = []
    for sub, item_type in _TYPE_DIRS.items():
        base = Path(src_dir) / sub
        if not base.exists():
            continue
        for item_dir in sorted(p for p in base.iterdir() if p.is_dir()):
            items.append(load_item(item_dir, item_type, languages, default_lang))
    return items
```

- [ ] **Step 4: 运行测试，确认通过**

Run: `python -m pytest tests/test_loader.py -v`
预期：全部 passed（front-matter 3 + 内容 4）

- [ ] **Step 5: Commit**

```bash
git add blog/loader.py tests/test_loader.py
git commit -m "feat: load content items with missing-translation fallback"
```

---

## Task 5: Markdown 渲染与阅读时长

**Files:**
- Create: `blog/markdown_render.py`
- Test: `tests/test_markdown_render.py`

- [ ] **Step 1: 写失败测试**

`tests/test_markdown_render.py`:
```python
from blog.markdown_render import render_markdown, reading_time, render_doc


def test_render_heading_and_paragraph():
    html = render_markdown("# Title\n\nhello world")
    assert "<h1" in html
    assert "hello world" in html


def test_render_fenced_code_has_highlight_wrapper():
    html = render_markdown("```python\nprint('hi')\n```")
    assert "codehilite" in html
    assert "<pre" in html


def test_render_table():
    md = "| a | b |\n|---|---|\n| 1 | 2 |"
    html = render_markdown(md)
    assert "<table" in html


def test_reading_time_latin():
    assert reading_time("one two three") == 1


def test_reading_time_cjk():
    assert reading_time("你好世界" * 200) >= 1  # 800 CJK chars -> ~2 min
    assert reading_time("你好世界" * 200) == 2


def test_render_doc_bundles_html_and_minutes():
    doc = render_doc("# Hi\n\nsome words here")
    assert "<h1" in doc.html
    assert doc.reading_minutes >= 1
```

- [ ] **Step 2: 运行测试，确认失败**

Run: `python -m pytest tests/test_markdown_render.py -v`
预期：FAIL（`ModuleNotFoundError: No module named 'blog.markdown_render'`）

- [ ] **Step 3: 实现**

`blog/markdown_render.py`:
```python
from __future__ import annotations

import math
import re
from dataclasses import dataclass

import markdown


@dataclass
class RenderedDoc:
    html: str
    reading_minutes: int


_MD = markdown.Markdown(
    extensions=["fenced_code", "codehilite", "tables", "toc"],
    extension_configs={"codehilite": {"guess_lang": False, "css_class": "codehilite"}},
)

_CJK = re.compile(r"[一-鿿぀-ヿ㐀-䶿＀-￯]")
_WORD = re.compile(r"[A-Za-z0-9]+")


def render_markdown(md_text: str) -> str:
    _MD.reset()
    return _MD.convert(md_text)


def reading_time(md_text: str) -> int:
    cjk = len(_CJK.findall(md_text))
    words = len(_WORD.findall(md_text))
    minutes = math.ceil(cjk / 400 + words / 200)
    return max(1, minutes)


def render_doc(md_text: str) -> RenderedDoc:
    return RenderedDoc(html=render_markdown(md_text), reading_minutes=reading_time(md_text))
```

- [ ] **Step 4: 运行测试，确认通过**

Run: `python -m pytest tests/test_markdown_render.py -v`
预期：6 passed

- [ ] **Step 5: Commit**

```bash
git add blog/markdown_render.py tests/test_markdown_render.py
git commit -m "feat: render markdown with code highlight and reading time"
```

---

## Task 6: 页面助手 + 测试 fixtures

**Files:**
- Create: `blog/pages.py`（先放 `lang_url`、`make_env`、写文件助手）
- Create: `tests/conftest.py`
- Test: `tests/test_pages.py`

- [ ] **Step 1: 写共享 fixtures**

`tests/conftest.py`:
```python
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
            "works": {"zh": "作品", "en": "Works", "ja": "作品"},
            "posts": {"zh": "随笔", "en": "Log", "ja": "随筆"},
            "about": {"zh": "关于我 About Me", "en": "About Me", "ja": "About Me"},
        },
        hero={
            "title": {"zh": "我做小游戏", "en": "I make small games", "ja": "小さなゲーム"},
            "sub": {"zh": "也写下想法", "en": "and write about them", "ja": "そして書く"},
        },
        social={"github": "https://github.com/cortexA233", "mail": "a@b.c"},
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
def post_item():
    return ContentItem(
        type="post", slug="buffering", date=datetime.date(2024, 5, 20),
        cover=None, tags=["unity"], order=None,
        translations={l: _tr("Buffering " + l) for l in ["zh", "en", "ja"]},
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
```

- [ ] **Step 2: 写失败测试**

`tests/test_pages.py`:
```python
from blog import pages


def test_lang_url():
    assert pages.lang_url("en") == "/en/"
    assert pages.lang_url("en", "works", "neon") == "/en/works/neon/"
    assert pages.lang_url("zh", "posts") == "/zh/posts/"


def test_make_env_exposes_lang_url(templates_dir):
    env = pages.make_env(templates_dir)
    assert "lang_url" in env.globals
    assert env.globals["lang_url"]("ja", "about") == "/ja/about/"
```

- [ ] **Step 3: 运行测试，确认失败**

Run: `python -m pytest tests/test_pages.py -v`
预期：FAIL（`ModuleNotFoundError: No module named 'blog.pages'`）

- [ ] **Step 4: 实现**

`blog/pages.py`:
```python
from __future__ import annotations

import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

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
    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=select_autoescape(["html"]),
    )
    env.globals["lang_url"] = lang_url
    env.globals["now_year"] = datetime.date.today().year
    return env


def _write(out_dir: Path, rel: str, html: str) -> None:
    dest = Path(out_dir) / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html, encoding="utf-8")
```

- [ ] **Step 5: 运行测试，确认通过**

Run: `python -m pytest tests/test_pages.py -v`
预期：2 passed

- [ ] **Step 6: Commit**

```bash
git add blog/pages.py tests/conftest.py tests/test_pages.py
git commit -m "feat: add page url helper, jinja env, test fixtures"
```

---

## Task 7: B1 样式表与代码高亮 CSS

**Files:**
- Create: `assets/css/style.css`
- Create: `assets/css/pygments.css`（由 pygmentize 生成）

> 说明：CSS 是静态资产，无单元测试；在 Task 15 的本地预览中做视觉验证。

- [ ] **Step 1: 写 `assets/css/style.css`（完整 B1 实现）**

```css
:root{
  --bg:#faf7f1; --ink:#33302b; --head:#1d1b18; --mut:#7c756a; --faint:#9a9184;
  --accent:#b5503a; --line:#eae3d8; --line2:#f0ebe1; --code-bg:#2c2a26;
  --serif:Georgia,"Songti SC","Noto Serif SC","Noto Serif JP","Hiragino Mincho ProN",serif;
  --mono:"SF Mono",Consolas,"JetBrains Mono",monospace;
  --measure:640px; --wide:960px;
}
*{box-sizing:border-box}
html{font-size:17px}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--serif);line-height:1.9}
a{color:inherit;text-decoration:none}
img{max-width:100%}

/* header */
.site-header{border-bottom:1px solid var(--line);background:var(--bg)}
.header-inner{max-width:var(--wide);margin:0 auto;padding:14px 24px;display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap}
.header-left{display:flex;align-items:center;gap:16px;flex-wrap:wrap}
.brand{font-size:1.25rem;font-weight:700;color:var(--head)}
.lang-switch{display:inline-flex;align-items:center;border:1.5px solid #d9cdba;border-radius:18px;overflow:hidden;font-size:.8rem}
.lang-switch .globe{padding:5px 6px 5px 10px;color:var(--faint)}
.lang-switch .lang{padding:5px 11px;color:#6b6458}
.lang-switch .lang.active{background:var(--accent);color:#fff;font-weight:700}
.main-nav{display:flex;align-items:center;gap:16px;font-size:.95rem}
.main-nav a.active{color:var(--accent);border-bottom:2px solid var(--accent);padding-bottom:2px}
.main-nav .nav-cta{background:var(--accent);color:#fff;padding:6px 16px;border-radius:18px;font-weight:700;box-shadow:0 2px 7px rgba(181,80,58,.3)}

/* layout */
.site-main{max-width:var(--wide);margin:0 auto;padding:0 24px}
.section-head{display:flex;align-items:baseline;gap:12px;margin:40px 0 18px}
.section-head h2{font-size:1.15rem;margin:0;color:var(--head)}
.section-head .rule{flex:1;height:1px;background:var(--line)}

/* hero */
.hero{padding:54px 0 12px}
.hero-title{font-size:1.9rem;line-height:1.4;color:var(--head);margin:0}
.hero-sub{color:var(--mut);font-style:italic;margin-top:10px}

/* works grid */
.works-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:22px}
.work-card{display:block}
.work-cover{height:150px;border-radius:8px;background-size:cover;background-position:center;background-color:#e7ddd0}
.work-title{font-size:1.05rem;margin:10px 0 2px;color:var(--head)}
.work-card .work-meta{font-size:.8rem;color:var(--faint);margin:0}

/* post list */
.post-list{list-style:none;padding:0;margin:0}
.post-row a{display:flex;gap:16px;align-items:baseline;padding:11px 0;border-bottom:1px solid var(--line2);flex-wrap:wrap}
.post-date{font-size:.78rem;color:var(--faint);min-width:92px}
.post-title{color:var(--ink)}
.post-summary{color:var(--mut);font-size:.85rem;flex-basis:100%;padding-left:108px}

/* article / prose */
.post,.work,.page{max-width:var(--measure);margin:0 auto;padding:46px 0 40px}
.post-kicker{font-size:.72rem;letter-spacing:.08em;text-transform:uppercase;color:var(--faint)}
.post h1,.work h1,.page h1{font-size:1.85rem;line-height:1.4;color:var(--head);margin:.3em 0 .2em}
.post-meta,.work header .work-meta{font-size:.82rem;color:var(--faint)}
.work-hero-cover{height:240px;border-radius:8px;background-size:cover;background-position:center;margin-bottom:18px}
.lang-notice{background:#f3ece0;border-left:3px solid var(--accent);padding:8px 12px;font-size:.85rem;color:var(--mut)}
.prose{font-size:1.06rem}
.prose h2{font-size:1.35rem;color:var(--head);margin:1.6em 0 .5em}
.prose h3{font-size:1.12rem;color:var(--head);margin:1.4em 0 .4em}
.prose p{margin:1em 0}
.prose blockquote{border-left:3px solid var(--line);margin:1em 0;padding:.2em 1em;color:var(--mut)}
.prose img{border-radius:6px;display:block;margin:1.2em auto}
.prose table{border-collapse:collapse;width:100%}
.prose th,.prose td{border:1px solid var(--line);padding:6px 10px}
.prose code{font-family:var(--mono);font-size:.9em;background:#efe9dd;padding:.1em .35em;border-radius:4px}
.codehilite{background:var(--code-bg);border-radius:8px;padding:14px 16px;overflow:auto;margin:1.2em 0}
.codehilite pre{margin:0}
.codehilite code{background:none;padding:0;font-family:var(--mono);font-size:.86rem;color:#e8e3d8}

/* footer */
.site-footer{border-top:1px solid var(--line);margin-top:56px}
.footer-inner{max-width:var(--wide);margin:0 auto;padding:18px 24px;display:flex;justify-content:space-between;font-size:.8rem;color:var(--faint)}
.footer-inner .social a{margin-left:14px}

/* responsive */
@media(max-width:900px){.works-grid{grid-template-columns:repeat(2,1fr)}}
@media(max-width:600px){
  .works-grid{grid-template-columns:1fr}
  .header-inner{flex-direction:column;align-items:flex-start}
  .main-nav{width:100%;justify-content:flex-start}
  .post-summary{padding-left:0}
}
```

- [ ] **Step 2: 生成 `assets/css/pygments.css`**

Run（venv 已激活，pygmentize 随 pygments 安装）：
```powershell
pygmentize -S monokai -f html -a .codehilite | Out-File -Encoding utf8 assets\css\pygments.css
```
预期：生成包含 `.codehilite .k { ... }` 等规则的 CSS 文件。
（`style.css` 在 `base.html` 中**后于** `pygments.css` 加载，因此 `.codehilite` 的背景以 `style.css` 的 `--code-bg` 为准。）

- [ ] **Step 3: 校验生成结果非空**

Run: `python -c "import pathlib,sys; t=pathlib.Path('assets/css/pygments.css').read_text(encoding='utf-8'); sys.exit(0 if '.codehilite' in t else 1)"`
预期：退出码 0。

- [ ] **Step 4: Commit**

```bash
git add assets/css/style.css assets/css/pygments.css
git commit -m "feat: B1 stylesheet and pygments code theme"
```

---

## Task 8: `base.html` + `redirect.html` + 根语言路由

**Files:**
- Create: `templates/base.html`, `templates/redirect.html`
- Modify: `blog/pages.py`（追加 `render_root_redirect`）
- Test: `tests/test_pages.py`（追加）

- [ ] **Step 1: 写 `templates/base.html`**

```html
<!DOCTYPE html>
<html lang="{{ lang }}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{ page_title }}</title>
  <link rel="stylesheet" href="/assets/css/pygments.css">
  <link rel="stylesheet" href="/assets/css/style.css">
  {% for l in site.languages %}
  <link rel="alternate" hreflang="{{ l }}" href="/{{ l }}/{{ page_path }}">
  {% endfor %}
  <link rel="alternate" hreflang="x-default" href="/{{ site.default_lang }}/{{ page_path }}">
</head>
<body>
  <header class="site-header">
    <div class="header-inner">
      <div class="header-left">
        <a class="brand" href="/{{ lang }}/">{{ site.title }}</a>
        <nav class="lang-switch" aria-label="Language">
          <span class="globe">🌐</span>
          {% for l in site.languages %}
          <a href="/{{ l }}/{{ page_path }}"
             class="lang {% if l == lang %}active{% endif %}"
             onclick="localStorage.setItem('lang','{{ l }}')">{{ site.lang_names[l] }}</a>
          {% endfor %}
        </nav>
      </div>
      <nav class="main-nav" aria-label="Main">
        <a href="/{{ lang }}/#works" class="{% if section == 'works' %}active{% endif %}">{{ site.nav.works[lang] }}</a>
        <a href="/{{ lang }}/posts/" class="{% if section == 'posts' %}active{% endif %}">{{ site.nav.posts[lang] }}</a>
        <a href="/{{ lang }}/about/" class="nav-cta">{{ site.nav.about[lang] }}</a>
      </nav>
    </div>
  </header>
  <main class="site-main">
    {% block content %}{% endblock %}
  </main>
  <footer class="site-footer">
    <div class="footer-inner">
      <span>© {{ now_year }} {{ site.title }}</span>
      <span class="social">
        {% if site.social.github %}<a href="{{ site.social.github }}">GitHub</a>{% endif %}
        {% if site.social.mail %}<a href="mailto:{{ site.social.mail }}">Mail</a>{% endif %}
      </span>
    </div>
  </footer>
</body>
</html>
```

- [ ] **Step 2: 写 `templates/redirect.html`**

```html
<!DOCTYPE html>
<html lang="{{ site.default_lang }}">
<head>
  <meta charset="UTF-8">
  <title>{{ site.title }}</title>
  <script>
    (function () {
      var supported = {{ site.languages | tojson }};
      var def = {{ site.default_lang | tojson }};
      var lang = null;
      try { lang = localStorage.getItem('lang'); } catch (e) {}
      if (supported.indexOf(lang) === -1) {
        lang = null;
        var navs = navigator.languages || [navigator.language || ''];
        for (var i = 0; i < navs.length; i++) {
          var code = (navs[i] || '').toLowerCase().split('-')[0];
          if (supported.indexOf(code) !== -1) { lang = code; break; }
        }
      }
      if (!lang) lang = def;
      location.replace('/' + lang + '/');
    })();
  </script>
</head>
<body>
  <p>Redirecting… <a href="/{{ site.default_lang }}/">Enter</a></p>
  <noscript>
    {% for l in site.languages %}<a href="/{{ l }}/">{{ site.lang_names[l] }}</a> {% endfor %}
  </noscript>
</body>
</html>
```

- [ ] **Step 3: 追加失败测试**

在 `tests/test_pages.py` 末尾追加：
```python
def test_render_root_redirect(site, templates_dir, tmp_path):
    env = pages.make_env(templates_dir)
    pages.render_root_redirect(env, site, tmp_path)
    out = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert "location.replace" in out
    assert '"en"' in out          # default lang appears in the tojson list
    assert "/en/" in out          # noscript / fallback link
```

- [ ] **Step 4: 运行测试，确认失败**

Run: `python -m pytest tests/test_pages.py::test_render_root_redirect -v`
预期：FAIL（`AttributeError: module 'blog.pages' has no attribute 'render_root_redirect'`）

- [ ] **Step 5: 实现 `render_root_redirect`**

在 `blog/pages.py` 末尾追加：
```python
def render_root_redirect(env, site, out_dir):
    html = env.get_template("redirect.html").render(site=site)
    _write(out_dir, "index.html", html)
```

- [ ] **Step 6: 运行测试，确认通过**

Run: `python -m pytest tests/test_pages.py -v`
预期：全部 passed

- [ ] **Step 7: Commit**

```bash
git add templates/base.html templates/redirect.html blog/pages.py tests/test_pages.py
git commit -m "feat: base layout, language router, root redirect"
```

---

## Task 9: 首页（`home.html` + `render_home`）

**Files:**
- Create: `templates/home.html`
- Modify: `blog/pages.py`（追加 `render_home`）
- Test: `tests/test_pages.py`（追加）

- [ ] **Step 1: 写 `templates/home.html`**

```html
{% extends "base.html" %}
{% block content %}
<section class="hero">
  <h1 class="hero-title">{{ site.hero.title[lang] }}</h1>
  <p class="hero-sub">{{ site.hero.sub[lang] }}</p>
</section>

<section id="works" class="works">
  <div class="section-head"><h2>{{ site.nav.works[lang] }}</h2><span class="rule"></span></div>
  <div class="works-grid">
    {% for w in works %}
    <a class="work-card" href="{{ lang_url(lang, 'works', w.slug) }}">
      <div class="work-cover" style="background-image:url('{{ w.cover or '/assets/img/default-cover.png' }}')"></div>
      <h3 class="work-title">{{ w.translations[lang].title }}</h3>
      <p class="work-meta">{% if w.date %}{{ w.date.year }}{% endif %}{% if w.tags %} · {{ w.tags | join(' · ') }}{% endif %}</p>
    </a>
    {% endfor %}
  </div>
</section>

<section class="recent">
  <div class="section-head"><h2>{{ site.nav.posts[lang] }}</h2><span class="rule"></span></div>
  <ul class="post-list">
    {% for p in recent_posts %}
    <li class="post-row">
      <a href="{{ lang_url(lang, 'posts', p.slug) }}">
        <span class="post-date">{% if p.date %}{{ p.date.isoformat() }}{% endif %}</span>
        <span class="post-title">{{ p.translations[lang].title }}</span>
      </a>
    </li>
    {% endfor %}
  </ul>
</section>
{% endblock %}
```

- [ ] **Step 2: 追加失败测试**

在 `tests/test_pages.py` 末尾追加：
```python
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
```

- [ ] **Step 3: 运行测试，确认失败**

Run: `python -m pytest tests/test_pages.py::test_render_home -v`
预期：FAIL（`has no attribute 'render_home'`）

- [ ] **Step 4: 实现 `render_home`**

在 `blog/pages.py` 末尾追加：
```python
def _sorted_posts(items):
    posts = [i for i in items if i.type == "post"]
    return sorted(posts, key=lambda i: (i.date or _MIN_DATE), reverse=True)


def render_home(env, site, items, lang, out_dir):
    works = sorted(
        [i for i in items if i.type == "work"],
        key=lambda i: (i.order if i.order is not None else 9999),
    )
    recent = _sorted_posts(items)[:5]
    html = env.get_template("home.html").render(
        site=site, lang=lang, section="home", page_path="",
        page_title=site.title, works=works, recent_posts=recent,
    )
    _write(out_dir, f"{lang}/index.html", html)
```

- [ ] **Step 5: 运行测试，确认通过**

Run: `python -m pytest tests/test_pages.py -v`
预期：全部 passed

- [ ] **Step 6: Commit**

```bash
git add templates/home.html blog/pages.py tests/test_pages.py
git commit -m "feat: home page with works grid and recent posts"
```

---

## Task 10: 作品详情（`work.html` + `render_work`）

**Files:**
- Create: `templates/work.html`
- Modify: `blog/pages.py`（追加 `render_work`）
- Test: `tests/test_pages.py`（追加）

- [ ] **Step 1: 写 `templates/work.html`**

```html
{% extends "base.html" %}
{% block content %}
<article class="work">
  <header>
    {% if item.cover %}<div class="work-hero-cover" style="background-image:url('{{ item.cover }}')"></div>{% endif %}
    <h1>{{ tr.title }}</h1>
    <p class="work-meta">{% if item.date %}{{ item.date.year }}{% endif %}{% if item.tags %} · {{ item.tags | join(' · ') }}{% endif %} · {{ reading_minutes }} min</p>
  </header>
  {% if missing %}<p class="lang-notice">{{ notice_text }}</p>{% endif %}
  <div class="prose">{{ body | safe }}</div>
</article>
{% endblock %}
```

- [ ] **Step 2: 追加失败测试**

在 `tests/test_pages.py` 末尾追加：
```python
def test_render_work(site, work_item, templates_dir, tmp_path):
    env = pages.make_env(templates_dir)
    pages.render_work(env, site, work_item, "ja", tmp_path)
    out = (tmp_path / "ja" / "works" / "neon" / "index.html").read_text(encoding="utf-8")
    assert "Neon ja" in out
    assert "min" in out               # reading time rendered
    assert "<h1" in out               # markdown body rendered
    assert "neon.png" in out          # cover image
```

- [ ] **Step 3: 运行测试，确认失败**

Run: `python -m pytest tests/test_pages.py::test_render_work -v`
预期：FAIL（`has no attribute 'render_work'`）

- [ ] **Step 4: 实现 `render_work`**

在 `blog/pages.py` 顶部 import 处加上 `from .markdown_render import render_doc`，并在末尾追加：
```python
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
```

- [ ] **Step 5: 运行测试，确认通过**

Run: `python -m pytest tests/test_pages.py -v`
预期：全部 passed

- [ ] **Step 6: Commit**

```bash
git add templates/work.html blog/pages.py tests/test_pages.py
git commit -m "feat: work detail page"
```

---

## Task 11: 随笔详情（`post.html` + `render_post`）

**Files:**
- Create: `templates/post.html`
- Modify: `blog/pages.py`（追加 `render_post`）
- Test: `tests/test_pages.py`（追加）

- [ ] **Step 1: 写 `templates/post.html`**

```html
{% extends "base.html" %}
{% block content %}
<article class="post">
  <header>
    <div class="post-kicker">{{ site.nav.posts[lang] }}</div>
    <h1>{{ tr.title }}</h1>
    <p class="post-meta">{% if item.date %}{{ item.date.isoformat() }}{% endif %} · {{ reading_minutes }} min{% if item.tags %} · {{ item.tags | join(' ') }}{% endif %}</p>
  </header>
  {% if missing %}<p class="lang-notice">{{ notice_text }}</p>{% endif %}
  <div class="prose">{{ body | safe }}</div>
</article>
{% endblock %}
```

- [ ] **Step 2: 追加失败测试**

在 `tests/test_pages.py` 末尾追加：
```python
def test_render_post(site, post_item, templates_dir, tmp_path):
    env = pages.make_env(templates_dir)
    pages.render_post(env, site, post_item, "en", tmp_path)
    out = (tmp_path / "en" / "posts" / "buffering" / "index.html").read_text(encoding="utf-8")
    assert "Buffering en" in out
    assert "2024-05-20" in out        # ISO date
    assert "min" in out
```

- [ ] **Step 3: 运行测试，确认失败**

Run: `python -m pytest tests/test_pages.py::test_render_post -v`
预期：FAIL（`has no attribute 'render_post'`）

- [ ] **Step 4: 实现 `render_post`**

在 `blog/pages.py` 末尾追加：
```python
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
```

- [ ] **Step 5: 运行测试，确认通过**

Run: `python -m pytest tests/test_pages.py -v`
预期：全部 passed

- [ ] **Step 6: Commit**

```bash
git add templates/post.html blog/pages.py tests/test_pages.py
git commit -m "feat: post detail page"
```

---

## Task 12: 随笔列表（`post_list.html` + `render_post_list`）

**Files:**
- Create: `templates/post_list.html`
- Modify: `blog/pages.py`（追加 `render_post_list`）
- Test: `tests/test_pages.py`（追加）

- [ ] **Step 1: 写 `templates/post_list.html`**

```html
{% extends "base.html" %}
{% block content %}
<section class="post-index">
  <div class="section-head"><h2>{{ site.nav.posts[lang] }}</h2><span class="rule"></span></div>
  <ul class="post-list">
    {% for p in posts %}
    <li class="post-row">
      <a href="{{ lang_url(lang, 'posts', p.slug) }}">
        <span class="post-date">{% if p.date %}{{ p.date.isoformat() }}{% endif %}</span>
        <span class="post-title">{{ p.translations[lang].title }}</span>
        {% if p.translations[lang].summary %}<span class="post-summary">{{ p.translations[lang].summary }}</span>{% endif %}
      </a>
    </li>
    {% endfor %}
  </ul>
</section>
{% endblock %}
```

- [ ] **Step 2: 追加失败测试**

在 `tests/test_pages.py` 末尾追加：
```python
def test_render_post_list(site, post_item, templates_dir, tmp_path):
    env = pages.make_env(templates_dir)
    pages.render_post_list(env, site, [post_item], "zh", tmp_path)
    out = (tmp_path / "zh" / "posts" / "index.html").read_text(encoding="utf-8")
    assert "Buffering zh" in out
    assert "/zh/posts/buffering/" in out
    assert "随笔" in out               # section title from nav
```

- [ ] **Step 3: 运行测试，确认失败**

Run: `python -m pytest tests/test_pages.py::test_render_post_list -v`
预期：FAIL（`has no attribute 'render_post_list'`）

- [ ] **Step 4: 实现 `render_post_list`**

在 `blog/pages.py` 末尾追加：
```python
def render_post_list(env, site, posts, lang, out_dir):
    ordered = sorted(posts, key=lambda i: (i.date or _MIN_DATE), reverse=True)
    html = env.get_template("post_list.html").render(
        site=site, lang=lang, section="posts", page_path="posts/",
        page_title=f"{site.nav['posts'][lang]} · {site.title}", posts=ordered,
    )
    _write(out_dir, f"{lang}/posts/index.html", html)
```

- [ ] **Step 5: 运行测试，确认通过**

Run: `python -m pytest tests/test_pages.py -v`
预期：全部 passed

- [ ] **Step 6: Commit**

```bash
git add templates/post_list.html blog/pages.py tests/test_pages.py
git commit -m "feat: post list page"
```

---

## Task 13: 关于我（`page.html` + `render_page`）

**Files:**
- Create: `templates/page.html`
- Modify: `blog/pages.py`（追加 `render_page`）
- Test: `tests/test_pages.py`（追加）

- [ ] **Step 1: 写 `templates/page.html`**

```html
{% extends "base.html" %}
{% block content %}
<article class="page">
  <h1>{{ tr.title }}</h1>
  {% if missing %}<p class="lang-notice">{{ notice_text }}</p>{% endif %}
  <div class="prose">{{ body | safe }}</div>
</article>
{% endblock %}
```

- [ ] **Step 2: 追加失败测试**

在 `tests/test_pages.py` 末尾追加：
```python
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
```

- [ ] **Step 3: 运行测试，确认失败**

Run: `python -m pytest tests/test_pages.py::test_render_page_with_fallback_notice -v`
预期：FAIL（`has no attribute 'render_page'`）

- [ ] **Step 4: 实现 `render_page`**

在 `blog/pages.py` 末尾追加：
```python
def render_page(env, site, item, lang, out_dir):
    doc = render_doc(item.translations[lang].body_md)
    html = env.get_template("page.html").render(
        site=site, lang=lang, section="about",
        page_path=f"{item.slug}/", page_title=f"{item.translations[lang].title} · {site.title}",
        item=item, tr=item.translations[lang], body=doc.html,
        missing=lang in item.missing_langs, notice_text=NOTICE.get(lang, ""),
    )
    _write(out_dir, f"{lang}/{item.slug}/index.html", html)
```

- [ ] **Step 5: 运行测试，确认通过**

Run: `python -m pytest tests/test_pages.py -v`
预期：全部 passed

- [ ] **Step 6: Commit**

```bash
git add templates/page.html blog/pages.py tests/test_pages.py
git commit -m "feat: about page with fallback notice"
```

---

## Task 14: 构建编排与 CLI（`build.py`）

**Files:**
- Create: `build.py`
- Test: `tests/test_build.py`

- [ ] **Step 1: 写失败测试（集成）**

`tests/test_build.py`:
```python
from pathlib import Path

import build as build_mod

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
  title: {zh: 我做小游戏, en: I make small games, ja: 小さなゲーム}
  sub: {zh: 也写下想法, en: and write about them, ja: そして書く}
social: {github: https://github.com/cortexA233, mail: a@b.c}
"""

TEMPLATES = Path(__file__).resolve().parent.parent / "templates"


def _seed_src(src: Path):
    (src / "works" / "neon").mkdir(parents=True)
    (src / "posts" / "hello").mkdir(parents=True)
    (src / "pages" / "about").mkdir(parents=True)
    (src / "site.yml").write_text(SITE_YML, encoding="utf-8")
    (src / "works" / "neon" / "meta.yml").write_text(
        "slug: neon\ndate: 2024-01-01\ntags: [unity]\norder: 1\n", encoding="utf-8")
    (src / "posts" / "hello" / "meta.yml").write_text(
        "slug: hello\ndate: 2024-05-20\n", encoding="utf-8")
    for l in ["zh", "en", "ja"]:
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
```

- [ ] **Step 2: 运行测试，确认失败**

Run: `python -m pytest tests/test_build.py -v`
预期：FAIL（`ModuleNotFoundError: No module named 'build'`）

- [ ] **Step 3: 实现 `build.py`**

```python
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
    works = [i for i in items if i.type == "work"]
    posts = [i for i in items if i.type == "post"]
    page_items = [i for i in items if i.type == "page"]

    env = pages.make_env(templates)
    for lang in site.languages:
        pages.render_home(env, site, items, lang, out)
        for w in works:
            pages.render_work(env, site, w, lang, out)
        pages.render_post_list(env, site, posts, lang, out)
        for p in posts:
            pages.render_post(env, site, p, lang, out)
        for pg in page_items:
            pages.render_page(env, site, pg, lang, out)
    pages.render_root_redirect(env, site, out)

    print(f"Built {len(items)} items × {len(site.languages)} languages -> {out}")


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
```

- [ ] **Step 4: 运行测试，确认通过**

Run: `python -m pytest tests/test_build.py -v`
预期：2 passed

- [ ] **Step 5: 运行整套测试**

Run: `python -m pytest -v`
预期：全部 passed（config / loader / markdown_render / pages / build）

- [ ] **Step 6: Commit**

```bash
git add build.py tests/test_build.py
git commit -m "feat: build orchestrator and serve CLI"
```

---

## Task 15: 三语示例内容、资源与本地预览验证

**Files:**
- Create: `src/site.yml`
- Create: `src/works/sample-game/{meta.yml,zh.md,en.md,ja.md}`
- Create: `src/posts/2024-05-20-input-buffering/{meta.yml,zh.md,en.md,ja.md}`
- Create: `src/pages/about/{zh.md,en.md,ja.md}`
- Create: `assets/img/default-cover.png`（占位封面）

- [ ] **Step 1: 写 `src/site.yml`**

```yaml
title: cortexA233
default_lang: en
languages: [zh, en, ja]
lang_names: { zh: 中文, en: English, ja: 日本語 }
nav:
  works: { zh: 作品, en: Works, ja: 作品 }
  posts: { zh: 随笔, en: Log, ja: 随筆 }
  about: { zh: 关于我 About Me, en: About Me, ja: About Me }
hero:
  title:
    zh: 我做一些小游戏，也写下做它们时的想法。
    en: I make small games, and write about making them.
    ja: 小さなゲームを作り、その過程を書き残しています。
  sub:
    zh: 游戏开发者 · Unity / 自研引擎
    en: Game developer · Unity / custom engines
    ja: ゲーム開発者 · Unity / 自作エンジン
social:
  github: https://github.com/cortexA233
  mail: cortexA233@outlook.com
```

- [ ] **Step 2: 写示例作品 `src/works/sample-game/`**

`meta.yml`:
```yaml
slug: sample-game
date: 2024-01-15
cover: /assets/img/default-cover.png
tags: [unity, action]
order: 1
```
`en.md`:
```markdown
---
title: Sample Game
summary: A tiny prototype exploring game feel.
---

This is a placeholder work entry. Replace it with a real project.

## What it is

A short description of the game, the engine, and what you were exploring.

```csharp
void Update() {
    transform.position += Vector3.right * Time.deltaTime;
}
```
```
`zh.md`:
```markdown
---
title: 示例作品
summary: 一个探索手感的小原型。
---

这是一个占位作品条目，请替换为真实项目。

## 这是什么

简单介绍游戏、引擎，以及你在其中探索的东西。

```csharp
void Update() {
    transform.position += Vector3.right * Time.deltaTime;
}
```
```
`ja.md`:
```markdown
---
title: サンプル作品
summary: ゲームの手触りを探る小さな試作。
---

これはプレースホルダーの作品です。実際のプロジェクトに置き換えてください。

## これは何か

ゲーム、エンジン、そして探求した内容の簡単な説明。

```csharp
void Update() {
    transform.position += Vector3.right * Time.deltaTime;
}
```
```

- [ ] **Step 3: 写示例随笔 `src/posts/2024-05-20-input-buffering/`**

`meta.yml`:
```yaml
slug: input-buffering
date: 2024-05-20
tags: [unity, game-feel]
```
`en.md`:
```markdown
---
title: Input Buffering in Bullet Time
summary: Why buffering made the controls feel sticky.
---

I only wanted to verify one thing about game feel: during bullet time, should
player input be buffered? The answer was counter-intuitive.

> Buffering made the controls feel *sticky*, so I tore it down and started over.
```
`zh.md`:
```markdown
---
title: 子弹时间里的输入缓存实验
summary: 为什么缓存反而让操作"粘手"。
---

我只想验证一个手感问题：子弹时间下，玩家输入要不要被缓存？答案出乎意料。

> 缓存反而让操作"粘手"，于是我推翻重来。
```
`ja.md`:
```markdown
---
title: バレットタイムの入力バッファ実験
summary: なぜバッファすると操作が「粘る」のか。
---

確かめたかったのは手触りだけ。バレットタイム中、入力をバッファすべきか。答えは意外だった。

> バッファすると操作が「粘る」感じになり、すべて作り直した。
```

- [ ] **Step 4: 写关于我页 `src/pages/about/`**

`en.md`:
```markdown
---
title: About Me
---

I'm cortexA233, a game developer. I build small games and write devlogs in
Chinese, English, and Japanese.

- GitHub: [cortexA233](https://github.com/cortexA233)
```
`zh.md`:
```markdown
---
title: 关于我
---

我是 cortexA233，一名游戏开发者。我做小游戏，并用中文、英文、日文写开发日志。

- GitHub：[cortexA233](https://github.com/cortexA233)
```
`ja.md`:
```markdown
---
title: About Me
---

cortexA233 です。ゲーム開発者として小さなゲームを作り、中国語・英語・日本語で
開発日誌を書いています。

- GitHub: [cortexA233](https://github.com/cortexA233)
```

- [ ] **Step 5: 放一张占位封面 `assets/img/default-cover.png`**

用 Python 生成一张 B1 暖色占位图（无需额外依赖，Pillow 不引入；直接写一个最小有效 PNG）：
```powershell
python -c "import base64,pathlib; pathlib.Path('assets/img/default-cover.png').write_bytes(base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=='))"
```
预期：生成一个 1×1 PNG 占位。（日后替换为真实封面图即可；CSS 用 `cover` 拉伸填充。）

- [ ] **Step 6: 全量构建**

Run: `python build.py`
预期输出：`Built 3 items × 3 languages -> ...`，无报错。生成 `index.html` 与 `zh/ en/ ja/` 树。

- [ ] **Step 7: 本地预览并人工验证**

Run（前台启动后在浏览器打开）：`python build.py --serve`
打开 http://127.0.0.1:8000/ ，逐项确认：
1. 根路径按浏览器语言/`localStorage` 跳到某语言首页（无偏好时进 `/en/`）。
2. B1 视觉：暖白底、衬线、朱砂红强调；左侧品牌 `cortexA233` + 语言切换分段控件（当前语言填充朱砂红）；右侧 `作品 / 随笔 / 关于我`（CTA 胶囊）。
3. 点中文/English/日本語，跳到**同一页**的对应语言版本，刷新后记住选择。
4. 首页作品网格 + 最近随笔列表；作品页封面/正文/代码高亮；随笔页日期+阅读时长；关于我页正常。
5. 缩小窗口：作品网格 3→2→1 列，导航在窄屏堆叠。
按 Ctrl+C 结束预览。

- [ ] **Step 8: Commit**

```bash
git add src/ assets/img/default-cover.png index.html zh/ en/ ja/
git commit -m "content: seed trilingual sample content and first build"
```

---

## Task 16: README 与最终验证

**Files:**
- Create: `README.md`

- [ ] **Step 1: 写 `README.md`**

```markdown
# cortexA233.github.io

自有的中/英/日三语纯静态博客（脱离 Hexo）。Python 构建，零前端框架。

## 本地开发

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1        # Windows PowerShell
python -m pip install -r requirements.txt
python build.py --serve              # 构建并在 http://127.0.0.1:8000 预览
```

## 写一篇新内容

1. 在 `src/posts/<日期-slug>/`（随笔）或 `src/works/<slug>/`（作品）下新建文件夹。
2. 放 `meta.yml`（`slug`、`date`、作品另加 `cover`/`tags`/`order`）。
3. 放 `zh.md` `en.md` `ja.md`，每个文件以 front-matter（`title`、可选 `summary`）开头，正文用 Markdown。
4. `python build.py` 重新生成。
5. `git add -A && git commit && git push` 发布到 https://cortexa233.github.io 。

## 结构

- `src/` 内容源（你编辑这里）
- `templates/` Jinja2 模板
- `blog/` 构建逻辑（config / loader / markdown_render / pages）
- `assets/` 共享 CSS / 字体 / 图片
- `index.html` + `zh/ en/ ja/` 为构建产物（已提交）

## 测试

```bash
python -m pytest
```
```

- [ ] **Step 2: 运行全套测试做最终确认**

Run: `python -m pytest -v`
预期：全部 passed。

- [ ] **Step 3: 干净重建确认幂等**

Run: `python build.py`
预期：再次成功，`git status` 中产物无意外改动（或仅时间无关的稳定输出）。

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs: add README with authoring and build workflow"
```

- [ ] **Step 5: 完成分支，决定合并策略**

使用 superpowers:finishing-a-development-branch 技能，把 `rebuild-blog` 合并/PR 到 `master`（master 是 GitHub Pages 发布分支）。合并后确认 `https://cortexa233.github.io` 正常（`.nojekyll` 已生效）。

---

## 自检（Self-Review）

**1. Spec 覆盖**
- §3 视觉规范 B1 → Task 7（CSS）+ Task 8（base 布局/导航/语言切换器在左）✓
- §4 信息架构与 URL（/zh /en /ja + 各页型）→ Task 9–13 + Task 14 编排 ✓
- §5 仓库目录结构 → Task 1 脚手架；`assets/` 不进构建（build 只清 `index.html`+语言目录）✓
- §6 数据模型与源格式（site.yml/meta.yml/{lang}.md）→ Task 3、4、15 ✓
- §7 语言路由与切换（localStorage→navigator→default；hreflang）→ Task 8（redirect + base）✓
- §8 构建流程（清理→加载→渲染→根路由；--serve）→ Task 14 ✓
- §9 错误处理（缺译文告警回退、缺默认语言报错）→ Task 4 + Task 13（notice）✓
- §10 依赖 → Task 1 requirements ✓
- §11 迁移（全新开始，删旧产物，含示例内容）→ Task 1 + Task 15 ✓
- §12 成功标准 → Task 15 Step 7 人工验证 + Task 16 ✓

**2. 占位符扫描**：无 TBD/TODO；每个代码步骤含完整代码；每个测试含完整断言。✓

**3. 类型一致性**：`SiteConfig`（含 `hero`）在 config 定义并在 conftest/site.yml/测试中一致；`ContentItem`/`Translation` 字段（`translations`、`missing_langs`）在 loader、pages、fixtures 中一致；`render_doc` 返回 `RenderedDoc(html, reading_minutes)`，pages 中按此访问；`lang_url`、`make_env`、各 `render_*` 签名前后一致；`build(src, templates, out)` 与集成测试调用一致。✓

**4. 默认语言**：site.yml 与 conftest 均为 `en`；根路由无偏好时回退 `en`。✓
