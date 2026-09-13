from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from pathlib import Path

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


@dataclass
class Translation:
    title: str
    summary: str
    body_md: str
    project: dict[str, str | list[str]] = field(default_factory=dict)


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
    category: str = "game"  # for works: "game" | "other"
    show_on_home: bool = True
    project_url: str | None = None
    store_links: dict[str, str] = field(default_factory=dict)


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
                project=dict(fm.get("project", {})),
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
        category=meta.get("category", "game"),
        show_on_home=meta.get("show_on_home", True),
        project_url=meta.get("project_url"),
        store_links=dict(meta.get("store_links", {})),
    )


_TYPE_DIRS = {"career": "career", "works": "work", "posts": "post", "pages": "page"}


def load_all(src_dir: Path, languages: list[str], default_lang: str) -> list[ContentItem]:
    items: list[ContentItem] = []
    for sub, item_type in _TYPE_DIRS.items():
        base = Path(src_dir) / sub
        if not base.exists():
            continue
        for item_dir in sorted(p for p in base.iterdir() if p.is_dir()):
            items.append(load_item(item_dir, item_type, languages, default_lang))
    return items
