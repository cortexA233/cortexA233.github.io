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
