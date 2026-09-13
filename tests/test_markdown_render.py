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
