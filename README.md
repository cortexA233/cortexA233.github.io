# cortexA233.github.io

自有的中/英/日三语纯静态博客（脱离 Hexo）。Python 构建，零前端框架。

## 本地开发

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1        # Windows PowerShell
python -m pip install -r requirements.txt
python build.py --serve              # 构建并在 http://127.0.0.1:8000 预览
```

## 写一篇新内容

1. 在 `src/posts/<日期-slug>/`（随笔）或 `src/works/<slug>/`（作品）下新建文件夹。
2. 放 `meta.yml`（`slug`、`date`，作品另加 `cover`/`tags`/`order`）。
3. 放 `zh.md` `en.md` `ja.md`，每个文件以 front-matter（`title`、可选 `summary`）开头，正文用 Markdown。
4. `python build.py` 重新生成。
5. `git add -A && git commit && git push` 发布到 https://cortexa233.github.io 。

作品的 `meta.yml` 可设 `show_on_home: false`，从首页精选中隐藏该作品；三语详情页仍会生成，原有链接保持可访问。省略时默认展示。

首页「参与开发 / Professional Work / 開発参加作品」展示 `career/` 中设有 `project_url` 的经历，按 `order` 排序，位于个人作品之前。`meta.yml` 用 `project_url` 保存官网、`cover` 保存图片；每种语言的 front-matter 用 `project` 保存 `title`、`company`、`role`、`period` 和 `contributions`（列表）。设 `show_on_home: false` 可隐藏卡片，完整经历页仍保留。图片来源记录在 `assets/img/credits.md`。

作品的 `meta.yml` 可用 `store_links` 保存「商店名称: URL」映射；构建会在详情页及首页重点作品处统一展示，正文无需重复写商店按钮。Exp10sion 继续以 `order: 1` 保持个人作品首位，Nintendo Switch 版的商店名称为 **10-Second Ghost**。

`src/site.yml` 的 `url` 是正式站点的 HTTPS 域名（如 `https://cortexa233.github.io`）。构建用它生成各页的 canonical 与完整的 hreflang 地址，`x-default` 指向同一内容的默认语言版本。更换域名时更新此字段并重新构建；未配置时不输出这些搜索标记。

缺译文时，回退页仍可通过语言切换访问并显示提示，但 canonical 指向默认语言原文，hreflang 仅列出实际存在的译文。

## 结构

- `src/` 内容源（你编辑这里）
- `templates/` Jinja2 模板
- `blog/` 构建逻辑（config / loader / markdown_render / pages）
- `assets/` 共享 CSS / 字体 / 图片
- `index.html` + `zh/ en/ ja/` 为构建产物（已提交）

## 测试

```powershell
python -m pytest
```
