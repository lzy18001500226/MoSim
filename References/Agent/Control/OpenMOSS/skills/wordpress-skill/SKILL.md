---
name: wordpress-skill
description: WordPress 站点管理 Skill — 通过 CLI 工具管理文章、页面、媒体、分类、标签和搜索
---

# WordPress Skill

你可以使用 `wordpress-cli.py` 工具来管理 WordPress 站点。该工具位于本 Skill 目录下。

## 站点信息

- 站点地址：`https://www.1m-reviews.com`
- 工具路径：`wordpress-cli.py`

## 可用命令

### 文章管理（post）

```bash
# 列出文章
post list                                       # 列出文章（默认 10 篇）
post list --status draft                        # 按状态筛选: publish/draft/pending/private
post list --categories 3                        # 按分类 ID 筛选
post list --search "关键词"                      # 搜索文章
post list --order asc --orderby date            # 排序: asc/desc，字段: date/id/title/modified
post list --after "2026-03-01T00:00:00"         # 仅返回此时间之后发布的文章
post list --before "2026-03-06T00:00:00"        # 仅返回此时间之前发布的文章
post list --author 1                            # 按作者 ID 筛选
post list --page 2 --per-page 20               # 分页

# 获取单篇文章
post get <id>                                   # 查看文章详情
post get <id> --edit                            # 编辑模式（含原始正文内容）

# 创建文章（默认状态: draft）
post create "文章标题"                           # 创建草稿
post create "标题" --content "<p>正文 HTML</p>"  # 指定正文
post create "标题" --content-file article.html   # 从文件读取正文
post create "标题" --status publish              # 直接发布: draft/publish/pending/private
post create "标题" --categories 3,5             # 分类 ID，逗号分隔
post create "标题" --tags 1,2                   # 标签 ID，逗号分隔
post create "标题" --slug "my-article"          # URL Slug
post create "标题" --excerpt "摘要"              # 文章摘要
post create "标题" --featured-media 8           # 特色图媒体 ID
post create "标题" --format standard            # 格式: standard/aside/gallery/link/image/quote/video/audio
post create "标题" --comment-status closed      # 评论: open/closed
post create "标题" --ping-status closed         # Pingback: open/closed
post create "标题" --sticky                     # 置顶文章

# 更新文章
post update <id> --title "新标题"
post update <id> --content "<p>新正文</p>"
post update <id> --status publish               # 草稿改为发布
post update <id> --categories 3 --tags 1,2
post update <id> --slug "new-slug"
post update <id> --featured-media 10

# 删除文章
post delete <id>                                # 移至回收站
post delete <id> --force                        # 跳过回收站直接删除
```

### 页面管理（page）

```bash
# 列出页面
page list                                       # 列出页面
page list --status draft                        # 按状态筛选
page list --parent 11                           # 按父页面 ID 筛选
page list --search "关键词"
page list --order asc --orderby menu_order      # 排序字段: date/id/title/menu_order

# 获取单个页面
page get <id>
page get <id> --edit                            # 编辑模式

# 创建页面（默认状态: draft）
page create "页面标题"
page create "标题" --content "<p>正文</p>"
page create "标题" --parent 11                  # 父页面 ID
page create "标题" --menu-order 5               # 菜单排序
page create "标题" --slug "about-us"
page create "标题" --status publish

# 更新页面
page update <id> --title "新标题"
page update <id> --content "<p>新正文</p>"
page update <id> --status publish
page update <id> --parent 11 --menu-order 3

# 删除页面
page delete <id>
page delete <id> --force
```

### 媒体管理（media）

```bash
# 列出媒体
media list                                      # 列出媒体
media list --media-type image                   # 按类型筛选: image/video/audio
media list --search "logo"
media list --page 2 --per-page 20

# 上传媒体
media upload /path/to/image.jpg                 # 上传文件
media upload /path/to/image.jpg --alt "描述"    # 上传并设 Alt 文本

# 获取媒体详情
media get <id>

# 更新媒体元信息
media update <id> --alt "新 Alt 文本"
media update <id> --caption "媒体说明"
media update <id> --description "详细描述"
media update <id> --title "新标题"
media update <id> --post 23                     # 关联到文章 ID

# 删除媒体
media delete <id>
```

### 分类管理（category）

```bash
category list                                   # 列出所有分类
category list --search "AI"                     # 搜索分类
category create "分类名"                         # 创建分类
category create "分类名" --slug "category-slug"
category create "子分类" --parent 3              # 创建子分类
```

### 标签管理（tag）

```bash
tag list                                        # 列出所有标签
tag list --search "AI"
tag create "标签名"                              # 创建标签
tag create "标签名" --slug "tag-slug"
```

### 搜索（search）

```bash
search "关键词"                                  # 搜索站点内容
search "关键词" --type post                     # 类型: post/term/post-format
search "关键词" --subtype page                  # 子类型: post/page/category/post_tag
search "关键词" --per-page 20
search "关键词" --exclude "1,2,3"               # 排除指定 ID
search "关键词" --include "4,5"                 # 仅包含指定 ID
```

## 站点分类参考

| ID  | 分类名       | 用途           |
| --- | ------------ | -------------- |
| 3   | AI Signals   | AI 相关资讯    |
| 4   | EV Signals   | 新能源汽车资讯 |
| 5   | Tech Signals | 科技/数码资讯  |

## 典型工作流

### 发布文章

```bash
# 1. 上传特色图（可选）
media upload /path/to/cover.jpg --alt "文章封面"
# 记录返回的媒体 ID

# 2. 创建草稿
post create "Article Title" \
  --content-file article.html \
  --categories 3 \
  --tags 1,2 \
  --slug "article-title" \
  --excerpt "Summary for SEO" \
  --featured-media <media_id> \
  --status draft

# 3. 确认无误后发布
post update <post_id> --status publish
```

### 检查文章状态

```bash
# 查看最近发布的文章
post list --status publish --per-page 5

# 查看所有草稿
post list --status draft

# 搜索特定文章
search "keyword" --type post
```

## 注意事项

- 创建文章/页面时默认状态为 `draft`（草稿），确认无误后再改为 `publish`
- 正文内容支持 HTML 格式
- `--content-file` 从文件读取正文，适合长文章
- 分类和标签使用 ID（数字），不是名称，需先用 `category list` / `tag list` 查询
- 删除操作默认移至回收站，`--force` 才是永久删除
- 媒体上传支持图片、视频、音频等常见格式
