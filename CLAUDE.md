# CLAUDE.md

cortexA233 的个人博客 —— 自有的 **中 / 英 / 日三语纯静态站点**，由一个小型 Python
生成器构建，部署在 GitHub Pages 用户站点 `cortexa233.github.io`（master 分支根目录）。
**已脱离 Hexo，无前端框架。** 设计与计划见 `docs/superpowers/`。

## 常用命令

所有命令在仓库根、激活虚拟环境后运行：

```powershell
.\.venv\Scripts\Activate.ps1          # 激活环境（每个新终端一次）
python build.py                       # 重新生成全站
python build.py --serve               # 构建并预览 http://127.0.0.1:8000
python -m pytest                      # 跑测试（提交前必跑）
```

部署：`git add -A && git commit -m "..." && git push`，推送到 master 即上线。

## 目录结构

```
src/         内容源（人编辑这里）  site.yml + career/ works/ posts/ pages/
templates/   Jinja2 模板（base / home / work / post / post_list / career / career_list / page / redirect）
blog/        构建逻辑：config（站点配置）· loader（扫描+解析）· markdown_render（md→html）· pages（生成各页）
assets/      共享 CSS / 图片，被 HTML 直接以 /assets/... 引用，不经构建
build.py     编排入口 + CLI（--serve）
tests/       pytest；conftest.py 提供 site / *_item 等 fixtures
index.html + zh/ en/ ja/   ← 构建产物，已提交（勿手改，见下）
```

## 内容创作规范

- 一条内容 = 一个文件夹，含 `meta.yml` + `zh.md` `en.md` `ja.md`。
- 内容类型按目录区分：`career/`（职业经历）、`works/`（个人作品）、`posts/`（随笔）、`pages/`（如 about）。
- `meta.yml` 字段：`slug`（URL 段）、`date`（排序，倒序）、`tags`、`order`（作品/经历排序）、`cover`（作品封面，`/assets/img/...`）、`category`（仅作品：`game` / `other`，用于首页分组「游戏作品 / 其他」，缺省为 `game`）。
- 作品分组文案在 `src/site.yml` 的 `work_groups`（三语）；空的分组在首页自动隐藏。
- `pages/` 下每个目录是一个独立页（如 `about`、`resume`），需在 `src/site.yml` 的 `nav` 加文案、并在 `templates/base.html` 加导航链接。
- 每个 `<lang>.md` 顶部是 front-matter：`title`、可选 `summary`；其下是 Markdown 正文（支持代码块 + pygments 高亮、表格）。

### 两个必须遵守的坑

1. **YAML 冒号后要有空格**：`summary: 《闪耀暖暖》…`（✅），不能 `summary:《…`（❌ 构建报错）。值含特殊符号时加引号：`summary: "a: b"`。
2. **三种语言都要写齐**：每条内容必须有默认语言 `en.md`（缺则构建报错）；缺 zh/ja 不报错，但会回退英文并显示「暂无译文」提示。

## 构建与部署规范

- **产物（`index.html` 与 `zh/ en/ ja/`）是提交进仓库的，但绝不手改**——只改 `src/` 然后 `python build.py` 重新生成。
- **提交前务必先 `python build.py`**，否则线上不更新。构建是幂等的（同输入产同输出）。
- 构建会先清掉 `index.html` 和 `zh/ en/ ja/` 再重写；不会动 `src/ templates/ blog/ assets/`。
- `.nojekyll` 必须保留（关闭 GitHub Pages 的 Jekyll 处理）。

## 代码规范（生成器）

- 模块职责单一：`config` 只读配置、`loader` 只产出 `ContentItem`、`markdown_render` 是纯函数、`pages` 只负责渲染落盘。新增页型时照此分层。
- 走 TDD：先在 `tests/` 写失败测试 → 跑 → 实现 → 跑通 → 提交。每个改动一次小提交。
- 依赖保持最小：仅 `markdown` `pygments` `pyyaml` `jinja2`（+ `pytest`）。新增依赖前先考虑能否自己写。

## i18n 规范

- 每种语言一套页面树：`/zh/ /en/ /ja/`，根 `/` 是按 `localStorage`→浏览器语言→默认语言路由的跳转页。
- 默认语言 `en`（在 `src/site.yml` 的 `default_lang`）。
- **同一内容三语共用同一个 `slug`**，语言切换器只替换路径里的 `/{lang}/` 段，所以加内容时别给不同语言起不同 slug。
- 导航文案、语言名、hero、社交链接都在 `src/site.yml`，三语各一份。

## 视觉规范（B1 · 纸感暖白）

- 全部样式在 `assets/css/style.css`；颜色在顶部 `:root` 变量：背景 `--bg:#faf7f1`、正文 `--ink`、强调（链接/激活/CTA）朱砂红 `--accent:#b5503a`。衬线字体，阅读栏 `--measure:640px`。
- 正文内链接（`.prose a`）为蓝色 `#2563eb`；**导航/品牌/CTA 保持红色体系，不要把站点 chrome 的链接也改蓝。**
- 导航布局：**左**= 品牌 `cortexA233` + 语言切换分段控件；**右**= 职业经历 / 个人作品 / 随笔 / 简历 + `关于我 About Me`（朱砂红实心 CTA）。
- 代码块走 `pygments.css`（monokai）+ `.codehilite` 的暖色底，`style.css` 在其后加载以覆盖背景。

## 不要做

- 不要手改 `zh/ en/ ja/` 或根 `index.html`（构建产物）。
- 不要在没跑 `build.py` 的情况下提交内容改动。
- 不要引入前端框架或重型依赖；不要恢复 Hexo。
- 不要给同一内容的不同语言用不同 slug。
