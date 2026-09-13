from __future__ import annotations

from dataclasses import dataclass, field
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
    work_groups: dict[str, dict[str, str]] = field(default_factory=dict)
    home: dict[str, dict[str, str]] = field(default_factory=dict)
    url: str = ""
    ui: dict[str, dict[str, str]] = field(default_factory=dict)


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
        work_groups=dict(data.get("work_groups", {})),
        home=dict(data.get("home", {})),
        url=data.get("url", "").rstrip("/"),
        ui=dict(data.get("ui", {})),
    )
