# 设计文档：自定义三语静态博客（脱离 Hexo）

日期：2026-06-01
状态：已确认，待写实现计划

## 1. 目标与背景

当前 `cortexA233.github.io` 仓库里只有 Hexo 6.3.0 生成的成品 HTML，源码（`_config.yml`、`source/`、主题）已丢失，且模板无法自定义。本项目**彻底抛弃 Hexo**，从零搭建一个：

- **纯静态**、部署在 GitHub Pages 用户站点（`cortexa233.github.io`，master 分支根目录）
- **前端样式完全自定义**，由我们自己拥有、能完整读懂的代码
- **支持中 / 英 / 日三语切换**，每篇内容三语写齐
- 面向**游戏开发者**：以**作品 / Demo 展示为主**，配**随笔 / 开发日志**与**关于我**页面

非目标（YAGNI，本期不做）：评论系统、全文搜索、标签聚合页、RSS、暗色模式、CMS 后台、自动翻译。这些都可后续增量加。

## 2. 关键决策（已与用户确认）

| 决策点 | 选择 |
|---|---|
| 写作工作流 | Markdown 源文件 + **本地 Python 构建脚本** 生成静态 HTML |
| 三语交付 | **构建期生成三套语言页面**（`/zh/ /en/ /ja/`），切语言 = 跳到同篇对应语言页 |
| 翻译完整度 | 每篇三语写齐；构建对缺失语言**告警并回退**到默认语言，不让站点崩 |
| 发布方式 | **本地构建 + 提交产物**到 master 根目录，零 CI |
| 起点 | **全新开始**，移除旧的 Hexo 测试内容 |
| 视觉方向 | **B1 · 纸感暖白**：暖白底 + 衬线字 + 朱砂红强调，可读性优先 |

## 3. 视觉规范（B1）

**配色**
- 背景 `#faf7f1`（暖白纸色）
- 正文 `#33302b`，标题 `#1d1b18`
- 次要文字 `#7c756a`，更弱 `#9a9184` / `#b0a899`
- 强调色（链接、激活态、CTA、分隔线）朱砂红 `#b5503a`
- 边框/分隔 `#eae3d8`、`#f0ebe1`
- 代码块底 `#2c2a26`，代码文字 `#e8e3d8`

**字体**
- 衬线栈（含 CJK 回退）：`Georgia, "Songti SC", "Noto Serif SC", "Noto Serif JP", "Hiragino Mincho ProN", serif`
- 等宽（代码）：`"SF Mono", Consolas, "JetBrains Mono", monospace`
- 本期用系统字体栈，不引外部 webfont（性能 + 少依赖）。若日后要三语视觉统一，可自托管 Noto Serif SC/JP（列为后续可选项）

**排版与间距**
- 正文 16–17px，行高 ~1.9，正文两端对齐可选
- 文章阅读栏 `max-width: 640px`，居中
- 首页内容区 `max-width: ~960px`
- 标题字重 700，区块标题旁带细横线分隔

**组件视觉**（以确认的 v4 mockup 为准）
- 顶部导航：**左侧** `cortexA233` 品牌，**紧随其后**是语言切换分段控件；**右侧** `作品` `随笔` + `关于我 About Me`（朱砂红实心胶囊 CTA，最醒目）
- 语言切换：分段控件，🌐 图标 + `中文 / English / 日本語`，当前语言填充朱砂红；位于左侧品牌之后
- 作品网格：3 列（响应式降为 2 / 1 列），每项封面图 + 标题 + 年份·技术标签
- 文章页：分类小标签 → 大标题 → 元信息（日期 · 阅读时长 · 标签）→ 正文 → 代码块（深色 + 语法高亮）→ 配图带图注
- 页脚：极简，版权 + 社交链接

**响应式**
- `> 900px`：作品 3 列，导航单行
- `600–900px`：作品 2 列
- `< 600px`：作品 1 列；导航折叠为汉堡菜单，语言切换与 About 在展开菜单内仍醒目

## 4. 信息架构与 URL

每种语言一套完整页面树，路径前缀为语言码：

```
/                         → 语言路由（见 §7），重定向到 /zh/ 或 /en/ 或 /ja/
/{lang}/                  → 首页（hero + 作品网格 + 最近随笔）
/{lang}/works/{slug}/     → 作品详情
/{lang}/posts/           → 随笔 / 开发日志列表
/{lang}/posts/{slug}/    → 随笔详情
/{lang}/about/            → 关于我
```

`{lang}` ∈ `{zh, en, ja}`。同一内容在三语下 `{slug}` 一致，因此语言切换器只需把当前路径的 `/{lang}/` 段替换即可跳到对应译文页。

## 5. 仓库目录结构

```
cortexA233.github.io/
├── .nojekyll                 # 关闭 GitHub Pages 的 Jekyll 处理（必需）
├── .gitignore                # 含 .superpowers/
├── build.py                  # 构建入口（python build.py [--serve]）
├── requirements.txt          # markdown, pygments, pyyaml, jinja2
├── README.md                 # 写作 + 构建 + 发布说明
│
├── src/                      # ← 你日常编辑的内容源
│   ├── site.yml              # 站点配置（标题、三语导航文案、社交链接、默认语言、语言列表）
│   ├── works/
│   │   └── project-neon/
│   │       ├── meta.yml      # 共享字段：slug, date, cover, tags, order
│   │       ├── zh.md         # front-matter: title, summary；正文 Markdown
│   │       ├── en.md
│   │       └── ja.md
│   ├── posts/
│   │   └── 2024-05-20-input-buffering/
│   │       ├── meta.yml
│   │       ├── zh.md / en.md / ja.md
│   └── pages/
│       └── about/
│           ├── zh.md / en.md / ja.md
│
├── templates/                # Jinja2 模板
│   ├── base.html             # 公共骨架：head、导航、语言切换、页脚
│   ├── home.html
│   ├── work.html
│   ├── post.html
│   ├── post_list.html
│   ├── page.html
│   └── redirect.html         # 根语言路由页
│
├── blog/                     # 构建逻辑（被 build.py 调用，便于分块理解）
│   ├── __init__.py
│   ├── config.py             # 读取 site.yml
│   ├── loader.py             # 扫描 src/，解析为内存数据模型
│   ├── markdown_render.py    # md → html（fenced_code + codehilite/pygments + tables）
│   └── pages.py              # 各类页面的生成函数
│
├── assets/                   # ← 共享静态资源，直接被 HTML 引用（不经构建转换）
│   ├── css/style.css         # 全部样式（手写，实现 B1 规范）
│   ├── css/pygments.css      # 代码高亮主题（适配暖色调）
│   ├── fonts/                # （可选）自托管字体
│   └── img/                  # 站点图标、默认封面、文章配图
│
└── [构建产物，提交到仓库，由 build.py 生成]
    ├── index.html            # 根语言路由
    ├── zh/  …                # 中文整站
    ├── en/  …                # 英文整站
    └── ja/  …                # 日文整站
```

**为何 `assets/` 不进构建产物**：CSS / 字体 / 图片是静态文件，无需转换，统一放 `assets/`，生成的 HTML 一律用绝对路径 `/assets/...` 引用。这样构建脚本**只写** `index.html` 与 `zh/ en/ ja/`，不会与源文件冲突。

**关于源文件公开**：`src/`、`templates/`、`build.py` 也会被 Pages 一并提供（可公开访问）。对个人博客无害，换来"全在一个分支、零 CI"的简单。

## 6. 内容数据模型与源格式

**`src/site.yml`（站点级）**
```yaml
title: cortexA233
default_lang: en
languages: [zh, en, ja]
lang_names: { zh: "中文", en: "English", ja: "日本語" }
nav:
  works:   { zh: "作品", en: "Works", ja: "作品" }
  posts:   { zh: "随笔", en: "Log",   ja: "随筆" }
  about:   { zh: "关于我 About Me", en: "About Me", ja: "About Me" }
social:
  github: https://github.com/cortexA233
  mail: cortexA233@outlook.com
```

**`meta.yml`（每个作品 / 随笔，语言无关的共享字段）**
```yaml
slug: project-neon
date: 2024-05-20
cover: /assets/img/neon-cover.jpg   # 作品才需要
tags: [unity, action]
order: 1                            # 作品在首页网格的排序（可选）
```

**`{lang}.md`（每种语言一份，含轻量 front-matter）**
```markdown
---
title: Input Buffering in Bullet Time
summary: 一句话摘要，用于列表/卡片
---

正文用标准 Markdown 书写，支持：
- 标题、列表、引用、表格
- ![图](/assets/img/xxx.png) 图片（带图注）
- ```lang 代码块（pygments 语法高亮）
```

**内存模型**：`loader.py` 把每个内容项解析为
```
ContentItem {
  type: "work" | "post" | "page"
  slug, date, cover, tags, order
  translations: { zh: {title, summary, body_html}, en: {...}, ja: {...} }
}
```

## 7. 语言路由与切换

- **根 `/index.html`**（由 `redirect.html` 模板生成）：极小的 HTML + 内联脚本，按优先级决定语言并 `location.replace`：
  1. `localStorage.lang`（用户上次选择）
  2. `navigator.languages` 匹配 `zh/en/ja`
  3. 回退到 `site.yml` 的 `default_lang`
  并提供三语手动入口链接作为无脚本回退（渐进增强）。
- **语言切换器**：每个页面内联一小段脚本，点击某语言时：① 写入 `localStorage.lang`；② 跳转到当前路径把 `/{lang}/` 段替换为目标语言（slug 三语一致，保证可对应）。激活语言高亮（朱砂红）。
- 每页 `<html lang="...">` 设为当前语言；`<head>` 输出 `hreflang` 互链（zh/en/ja + x-default），利于 SEO。

## 8. 构建流程（`build.py`）

1. **加载配置**：读取 `src/site.yml`。
2. **发现内容**：扫描 `src/works/*`、`src/posts/*`、`src/pages/*`，对每项读 `meta.yml` + 各 `{lang}.md`，解析 front-matter 与正文。
3. **渲染 Markdown**：`markdown` 库，启用 `fenced_code`、`codehilite`(pygments)、`tables`、`toc`(可选)；产出正文 HTML 片段，计算阅读时长。
4. **清理输出**：删除旧的 `index.html` 与 `zh/ en/ ja/` 目录（幂等，避免残留过期页面）；**不动** `assets/`、`src/`、`templates/`、`blog/`。
5. **逐语言生成**：对每个 `lang`：
   - 首页 `{lang}/index.html`（hero + 按 `order`/日期排的作品网格 + 最近 5 篇随笔）
   - 每个作品 `{lang}/works/{slug}/index.html`
   - 随笔列表 `{lang}/posts/index.html`（按日期倒序）
   - 每篇随笔 `{lang}/posts/{slug}/index.html`
   - 关于我 `{lang}/about/index.html`
6. **生成根路由** `index.html`。
7. **本地预览**：`python build.py --serve` 构建后用 `http.server` 起在 `127.0.0.1:8000`；或手动 `python -m http.server 8000`。

**模块边界（便于独立理解与测试）**
- `config.py`：输入 `site.yml` → 站点配置对象。
- `loader.py`：输入 `src/` 目录 → `ContentItem` 列表。不依赖模板/Markdown 渲染细节。
- `markdown_render.py`：输入 md 文本 → (html, 元信息)。纯函数，可单测。
- `pages.py`：输入（配置 + 内容 + 已渲染 html）→ 写出 HTML 文件。依赖 Jinja2 模板。
- `build.py`：编排上述步骤 + CLI（`--serve`）。

## 9. 错误处理

- **缺某语言 `{lang}.md`**：打印 `WARNING: <slug> 缺少 <lang> 译文，回退到 <default_lang>`，该语言页用默认语言正文渲染并在页面顶部加一行小字提示"本页暂无该语言译文"。**不中断构建**。
- **`meta.yml` 缺必填字段 / 日期格式错误**：明确报错并指出文件路径，**中断构建**（属内容错误，需修正）。
- **作品缺 `cover`**：用 `assets/img/default-cover.*` 兜底并告警。
- 构建对输出目录先清后写，保证可重复运行结果一致。

## 10. 依赖

`requirements.txt`：
```
markdown        # md → html
pygments        # 代码高亮
pyyaml          # 解析 site.yml / meta.yml / front-matter
jinja2          # HTML 模板
```
用户已装 Python 3.14。无 npm、无前端框架、无构建工具链；运行时（浏览器侧）仅少量内联原生 JS（语言路由/切换），无 JS 库。

## 11. 迁移（全新开始）

- 删除旧 Hexo 产物：`2022/`、`2023/`、`archives/`、`about/`、`css/`、`font/`、`images/`、`img/`、旧 `index.html`。
- 不迁移旧的 6 篇测试内容（`222`、`Booom`、`life_after` 等正文基本为空）。
- 新建 §5 的目录结构，附 1 个示例作品 + 1 篇示例随笔 + 关于我页（三语），用于验证与作为模板。

## 12. 成功标准

1. `python build.py` 无报错，生成 `index.html` + `zh/ en/ ja/` 三套完整页面。
2. `python build.py --serve`（或 `http.server`）本地打开：B1 样式正确呈现，长文阅读舒适。
3. 语言切换器在中/英/日间跳转到**同一篇**的对应译文；刷新后记住上次语言；根路径按浏览器语言/偏好正确路由。
4. 首页作品网格、随笔列表、文章阅读页、代码高亮、关于我页均正常。
5. 新增一篇内容 = 建 1 个文件夹 + `meta.yml` + 三个 `{lang}.md`，重新构建即出现，无需改模板。
6. `git add -A && git commit && git push` 后，`https://cortexa233.github.io` 正常显示（`.nojekyll` 生效）。
7. 响应式：桌面/平板/手机下导航与作品网格表现正常。
```

