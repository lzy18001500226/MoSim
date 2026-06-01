#!/usr/bin/env python3
"""
WordPress REST API CLI 工具
用于 AI小珂 等角色发布文章到 WordPress。

用法：python wordpress-cli.py <命令> [参数]

站点地址、用户名、应用密码在下方配置区修改。
"""
import sys
import json
import argparse
import base64
import os

import requests

# ============================================================
# 配置：修改为你的 WordPress 站点信息
# ============================================================
WP_URL = "https://www.1m-reviews.com"          # WordPress 站点地址（不含尾 /）
WP_USER = "1mreviews_admin"                          # WordPress 用户名
WP_APP_PASSWORD = "UcFL VRpD 3lZc yQns KlZo tFtJ"    # 应用密码

# API 基础地址
API_BASE = f"{WP_URL}/wp-json/wp/v2"

# 代理配置（留空则不使用代理）
PROXIES = {
    "http": "http://127.0.0.1:7890",
    "https": "http://127.0.0.1:7890",
}


# ============================================================
# HTTP 工具
# ============================================================

def _headers() -> dict:
    token = base64.b64encode(f"{WP_USER}:{WP_APP_PASSWORD}".encode()).decode()
    return {
        "Authorization": f"Basic {token}",
        "Accept": "application/json",
    }


def _request(method: str, path: str, **kwargs):
    """发送请求并处理错误"""
    url = f"{API_BASE}{path}"
    try:
        resp = requests.request(method, url, headers=_headers(), timeout=30, proxies=PROXIES, **kwargs)
        if resp.status_code >= 400:
            try:
                err = resp.json()
                print(f"❌ 错误 {resp.status_code}: {err.get('message', resp.text)}")
            except Exception:
                print(f"❌ 错误 {resp.status_code}: {resp.text[:200]}")
            sys.exit(1)
        if resp.status_code == 204:
            return {}
        return resp.json()
    except requests.exceptions.ConnectionError:
        print(f"❌ 无法连接到 {WP_URL}")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
        sys.exit(1)


def _print_json(data):
    """美化输出 JSON"""
    print(json.dumps(data, ensure_ascii=False, indent=2))


# ============================================================
# Posts 命令
# ============================================================

def cmd_post_list(args):
    """列出文章"""
    params = {"per_page": args.per_page, "page": args.page}
    if args.status:
        params["status"] = args.status
    if args.search:
        params["search"] = args.search
    if args.categories:
        params["categories"] = args.categories
    if args.order:
        params["order"] = args.order
    if args.orderby:
        params["orderby"] = args.orderby
    if args.after:
        params["after"] = args.after
    if args.before:
        params["before"] = args.before
    if args.author:
        params["author"] = args.author
    params["_fields"] = "id,title,slug,status,link,date,modified,categories,tags"

    data = _request("GET", "/posts", params=params)
    if not data:
        print("暂无文章")
        return
    for p in data:
        title = p["title"]["rendered"] if isinstance(p["title"], dict) else p["title"]
        print(f"  [{p['id']}] {p['status']:10s} {title}")
        print(f"       {p['link']}")


def cmd_post_get(args):
    """获取单篇文章"""
    context = "edit" if args.edit else "view"
    data = _request("GET", f"/posts/{args.id}", params={"context": context})
    title = data["title"]["rendered"] if isinstance(data["title"], dict) else data["title"]
    print(f"ID:     {data['id']}")
    print(f"标题:   {title}")
    print(f"状态:   {data['status']}")
    print(f"链接:   {data['link']}")
    print(f"日期:   {data['date']}")
    print(f"分类:   {data.get('categories', [])}")
    print(f"标签:   {data.get('tags', [])}")
    if args.edit:
        content = data["content"]["raw"] if isinstance(data["content"], dict) else data["content"]
        print(f"\n--- 正文 ---\n{content}")


def cmd_post_create(args):
    """创建文章"""
    body = {
        "title": args.title,
        "status": args.status,
    }
    if args.content:
        body["content"] = args.content
    if args.content_file:
        with open(args.content_file, "r", encoding="utf-8") as f:
            body["content"] = f.read()
    if args.excerpt:
        body["excerpt"] = args.excerpt
    if args.categories:
        body["categories"] = [int(c) for c in args.categories.split(",")]
    if args.tags:
        body["tags"] = [int(t) for t in args.tags.split(",")]
    if args.slug:
        body["slug"] = args.slug
    if args.featured_media:
        body["featured_media"] = args.featured_media
    if args.format:
        body["format"] = args.format
    if args.comment_status:
        body["comment_status"] = args.comment_status
    if args.ping_status:
        body["ping_status"] = args.ping_status
    if args.sticky:
        body["sticky"] = True

    data = _request("POST", "/posts", json=body)
    title = data["title"]["rendered"] if isinstance(data["title"], dict) else data["title"]
    print(f"✅ 文章已创建: [{data['id']}] {title}")
    print(f"   状态: {data['status']}")
    print(f"   链接: {data['link']}")


def cmd_post_update(args):
    """更新文章"""
    body = {}
    if args.title:
        body["title"] = args.title
    if args.status:
        body["status"] = args.status
    if args.content:
        body["content"] = args.content
    if args.content_file:
        with open(args.content_file, "r", encoding="utf-8") as f:
            body["content"] = f.read()
    if args.excerpt:
        body["excerpt"] = args.excerpt
    if args.categories:
        body["categories"] = [int(c) for c in args.categories.split(",")]
    if args.tags:
        body["tags"] = [int(t) for t in args.tags.split(",")]
    if args.slug:
        body["slug"] = args.slug
    if args.featured_media:
        body["featured_media"] = args.featured_media
    if args.format:
        body["format"] = args.format
    if args.comment_status:
        body["comment_status"] = args.comment_status
    if args.ping_status:
        body["ping_status"] = args.ping_status
    if args.sticky is not None:
        body["sticky"] = args.sticky

    if not body:
        print("❌ 至少指定一个要更新的字段")
        sys.exit(1)

    data = _request("POST", f"/posts/{args.id}", json=body)
    title = data["title"]["rendered"] if isinstance(data["title"], dict) else data["title"]
    print(f"✅ 文章已更新: [{data['id']}] {title}")
    print(f"   状态: {data['status']}")
    print(f"   链接: {data['link']}")


def cmd_post_delete(args):
    """删除文章"""
    params = {}
    if args.force:
        params["force"] = "true"
    data = _request("DELETE", f"/posts/{args.id}", params=params)
    print(f"✅ 文章已删除: {args.id}")


# ============================================================
# Pages 命令
# ============================================================

def cmd_page_list(args):
    """列出页面"""
    params = {"per_page": args.per_page, "page": args.page}
    if args.status:
        params["status"] = args.status
    if args.search:
        params["search"] = args.search
    if args.parent is not None:
        params["parent"] = args.parent
    if args.order:
        params["order"] = args.order
    if args.orderby:
        params["orderby"] = args.orderby
    params["_fields"] = "id,title,slug,status,link,date,modified,parent,menu_order"

    data = _request("GET", "/pages", params=params)
    if not data:
        print("暂无页面")
        return
    for p in data:
        title = p["title"]["rendered"] if isinstance(p["title"], dict) else p["title"]
        parent_info = f" (parent:{p['parent']})" if p.get("parent", 0) > 0 else ""
        print(f"  [{p['id']}] {p['status']:10s} {title}{parent_info}")
        print(f"       {p['link']}")


def cmd_page_get(args):
    """获取单个页面"""
    context = "edit" if args.edit else "view"
    data = _request("GET", f"/pages/{args.id}", params={"context": context})
    title = data["title"]["rendered"] if isinstance(data["title"], dict) else data["title"]
    print(f"ID:     {data['id']}")
    print(f"标题:   {title}")
    print(f"状态:   {data['status']}")
    print(f"链接:   {data['link']}")
    print(f"日期:   {data['date']}")
    print(f"父页面: {data.get('parent', 0)}")
    print(f"排序:   {data.get('menu_order', 0)}")
    if args.edit:
        content = data["content"]["raw"] if isinstance(data["content"], dict) else data["content"]
        print(f"\n--- 正文 ---\n{content}")


def cmd_page_create(args):
    """创建页面"""
    body = {
        "title": args.title,
        "status": args.status,
    }
    if args.content:
        body["content"] = args.content
    if args.content_file:
        with open(args.content_file, "r", encoding="utf-8") as f:
            body["content"] = f.read()
    if args.excerpt:
        body["excerpt"] = args.excerpt
    if args.slug:
        body["slug"] = args.slug
    if args.parent is not None:
        body["parent"] = args.parent
    if args.featured_media:
        body["featured_media"] = args.featured_media
    if args.menu_order is not None:
        body["menu_order"] = args.menu_order
    if args.comment_status:
        body["comment_status"] = args.comment_status
    if args.ping_status:
        body["ping_status"] = args.ping_status

    data = _request("POST", "/pages", json=body)
    title = data["title"]["rendered"] if isinstance(data["title"], dict) else data["title"]
    print(f"✅ 页面已创建: [{data['id']}] {title}")
    print(f"   状态: {data['status']}")
    print(f"   链接: {data['link']}")


def cmd_page_update(args):
    """更新页面"""
    body = {}
    if args.title:
        body["title"] = args.title
    if args.status:
        body["status"] = args.status
    if args.content:
        body["content"] = args.content
    if args.content_file:
        with open(args.content_file, "r", encoding="utf-8") as f:
            body["content"] = f.read()
    if args.excerpt:
        body["excerpt"] = args.excerpt
    if args.slug:
        body["slug"] = args.slug
    if args.parent is not None:
        body["parent"] = args.parent
    if args.featured_media:
        body["featured_media"] = args.featured_media
    if args.menu_order is not None:
        body["menu_order"] = args.menu_order
    if args.comment_status:
        body["comment_status"] = args.comment_status
    if args.ping_status:
        body["ping_status"] = args.ping_status

    if not body:
        print("❌ 至少指定一个要更新的字段")
        sys.exit(1)

    data = _request("POST", f"/pages/{args.id}", json=body)
    title = data["title"]["rendered"] if isinstance(data["title"], dict) else data["title"]
    print(f"✅ 页面已更新: [{data['id']}] {title}")
    print(f"   状态: {data['status']}")
    print(f"   链接: {data['link']}")


def cmd_page_delete(args):
    """删除页面"""
    params = {}
    if args.force:
        params["force"] = "true"
    data = _request("DELETE", f"/pages/{args.id}", params=params)
    print(f"✅ 页面已删除: {args.id}")


# ============================================================
# Media 命令
# ============================================================

def cmd_media_list(args):
    """列出媒体"""
    params = {"per_page": args.per_page, "page": args.page}
    if args.media_type:
        params["media_type"] = args.media_type
    if args.search:
        params["search"] = args.search
    params["_fields"] = "id,title,source_url,media_type,mime_type,date"

    data = _request("GET", "/media", params=params)
    if not data:
        print("暂无媒体")
        return
    for m in data:
        title = m["title"]["rendered"] if isinstance(m["title"], dict) else m["title"]
        print(f"  [{m['id']}] {m.get('media_type', '?'):8s} {title}")
        print(f"       {m['source_url']}")


def cmd_media_upload(args):
    """上传媒体文件"""
    filepath = args.file
    if not os.path.exists(filepath):
        print(f"❌ 文件不存在: {filepath}")
        sys.exit(1)

    filename = os.path.basename(filepath)
    import mimetypes
    mime_type, _ = mimetypes.guess_type(filepath)
    if not mime_type:
        mime_type = "application/octet-stream"

    token = base64.b64encode(f"{WP_USER}:{WP_APP_PASSWORD}".encode()).decode()
    headers = {
        "Authorization": f"Basic {token}",
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Content-Type": mime_type,
    }

    with open(filepath, "rb") as f:
        resp = requests.post(
            f"{API_BASE}/media",
            headers=headers,
            data=f.read(),
            timeout=60,
            proxies=PROXIES,
        )

    if resp.status_code >= 400:
        try:
            err = resp.json()
            print(f"❌ 上传失败 {resp.status_code}: {err.get('message', resp.text)}")
        except Exception:
            print(f"❌ 上传失败 {resp.status_code}: {resp.text[:200]}")
        sys.exit(1)

    data = resp.json()
    print(f"✅ 媒体已上传: [{data['id']}]")
    print(f"   URL: {data['source_url']}")
    print(f"   类型: {data.get('mime_type', '?')}")

    # 设置 alt 文本
    if args.alt:
        _request("POST", f"/media/{data['id']}", json={"alt_text": args.alt})
        print(f"   Alt: {args.alt}")


def cmd_media_get(args):
    """获取单个媒体"""
    data = _request("GET", f"/media/{args.id}")
    title = data["title"]["rendered"] if isinstance(data["title"], dict) else data["title"]
    print(f"ID:    {data['id']}")
    print(f"标题:  {title}")
    print(f"URL:   {data['source_url']}")
    print(f"类型:  {data.get('mime_type', '?')}")
    print(f"Alt:   {data.get('alt_text', '')}")
    caption = data.get("caption", {})
    if isinstance(caption, dict):
        caption = caption.get("rendered", "")
    print(f"描述:  {caption}")


def cmd_media_update(args):
    """更新媒体元信息"""
    body = {}
    if args.alt is not None:
        body["alt_text"] = args.alt
    if args.caption is not None:
        body["caption"] = args.caption
    if args.description is not None:
        body["description"] = args.description
    if args.title is not None:
        body["title"] = args.title
    if args.post is not None:
        body["post"] = args.post

    if not body:
        print("❌ 至少指定一个要更新的字段")
        sys.exit(1)

    data = _request("POST", f"/media/{args.id}", json=body)
    title = data["title"]["rendered"] if isinstance(data["title"], dict) else data["title"]
    print(f"✅ 媒体已更新: [{data['id']}] {title}")
    print(f"   URL: {data['source_url']}")


def cmd_media_delete(args):
    """删除媒体"""
    _request("DELETE", f"/media/{args.id}", params={"force": "true"})
    print(f"✅ 媒体已删除: {args.id}")


# ============================================================
# Categories / Tags 命令
# ============================================================

def cmd_cat_list(args):
    """列出分类"""
    params = {"per_page": 100}
    if args.search:
        params["search"] = args.search
    params["_fields"] = "id,name,slug,count,parent"
    data = _request("GET", "/categories", params=params)
    for c in data:
        parent = f" (parent:{c['parent']})" if c.get("parent", 0) > 0 else ""
        print(f"  [{c['id']}] {c['name']} ({c['slug']}) — {c['count']} 篇{parent}")


def cmd_cat_create(args):
    """创建分类"""
    body = {"name": args.name}
    if args.slug:
        body["slug"] = args.slug
    if args.parent:
        body["parent"] = args.parent
    data = _request("POST", "/categories", json=body)
    print(f"✅ 分类已创建: [{data['id']}] {data['name']}")


def cmd_tag_list(args):
    """列出标签"""
    params = {"per_page": 100}
    if args.search:
        params["search"] = args.search
    params["_fields"] = "id,name,slug,count"
    data = _request("GET", "/tags", params=params)
    for t in data:
        print(f"  [{t['id']}] {t['name']} ({t['slug']}) — {t['count']} 篇")


def cmd_tag_create(args):
    """创建标签"""
    body = {"name": args.name}
    if args.slug:
        body["slug"] = args.slug
    data = _request("POST", "/tags", json=body)
    print(f"✅ 标签已创建: [{data['id']}] {data['name']}")


# ============================================================
# Search 命令
# ============================================================

def cmd_search(args):
    """搜索"""
    params = {
        "search": args.query,
        "per_page": args.per_page,
        "type": args.type,
    }
    if args.subtype:
        params["subtype"] = args.subtype
    if args.exclude:
        params["exclude"] = args.exclude
    if args.include:
        params["include"] = args.include

    data = _request("GET", "/search", params=params)
    if not data:
        print("无搜索结果")
        return
    for r in data:
        print(f"  [{r['id']}] [{r['type']}/{r.get('subtype', '?')}] {r['title']}")
        print(f"       {r['url']}")


# ============================================================
# 主入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="WordPress REST API CLI 工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # --- post ---
    post_p = subparsers.add_parser("post", help="文章管理")
    post_sub = post_p.add_subparsers(dest="post_cmd")

    p = post_sub.add_parser("list", help="列出文章")
    p.add_argument("--page", type=int, default=1, help="页码")
    p.add_argument("--per-page", type=int, default=10, help="每页数量")
    p.add_argument("--status", help="状态筛选: publish/draft/pending/private")
    p.add_argument("--search", help="搜索关键词")
    p.add_argument("--categories", help="分类 ID 筛选")
    p.add_argument("--order", choices=["asc", "desc"], help="排序方向（默认 desc）")
    p.add_argument("--orderby", help="排序字段: date/id/title/slug/modified/author/relevance")
    p.add_argument("--after", help="仅返回此时间之后发布的文章（ISO8601）")
    p.add_argument("--before", help="仅返回此时间之前发布的文章（ISO8601）")
    p.add_argument("--author", help="作者 ID 筛选")
    p.set_defaults(func=cmd_post_list)

    p = post_sub.add_parser("get", help="获取单篇文章")
    p.add_argument("id", type=int, help="文章 ID")
    p.add_argument("--edit", action="store_true", help="获取编辑模式（含原始内容）")
    p.set_defaults(func=cmd_post_get)

    p = post_sub.add_parser("create", help="创建文章")
    p.add_argument("title", help="文章标题")
    p.add_argument("--content", help="正文内容（HTML/Markdown）")
    p.add_argument("--content-file", help="从文件读取正文内容")
    p.add_argument("--status", default="draft", help="状态: draft/publish/pending/private（默认 draft）")
    p.add_argument("--excerpt", help="摘要")
    p.add_argument("--categories", help="分类 ID，逗号分隔")
    p.add_argument("--tags", help="标签 ID，逗号分隔")
    p.add_argument("--slug", help="URL Slug")
    p.add_argument("--featured-media", type=int, help="特色图媒体 ID")
    p.add_argument("--format", help="文章格式: standard/aside/chat/gallery/link/image/quote/status/video/audio")
    p.add_argument("--comment-status", choices=["open", "closed"], help="评论状态")
    p.add_argument("--ping-status", choices=["open", "closed"], help="Pingback 状态")
    p.add_argument("--sticky", action="store_true", help="置顶文章")
    p.set_defaults(func=cmd_post_create)

    p = post_sub.add_parser("update", help="更新文章")
    p.add_argument("id", type=int, help="文章 ID")
    p.add_argument("--title", help="新标题")
    p.add_argument("--content", help="新正文")
    p.add_argument("--content-file", help="从文件读取新正文")
    p.add_argument("--status", help="新状态")
    p.add_argument("--excerpt", help="新摘要")
    p.add_argument("--categories", help="新分类 ID，逗号分隔")
    p.add_argument("--tags", help="新标签 ID，逗号分隔")
    p.add_argument("--slug", help="新 Slug")
    p.add_argument("--featured-media", type=int, help="新特色图媒体 ID")
    p.add_argument("--format", help="新文章格式")
    p.add_argument("--comment-status", choices=["open", "closed"], help="评论状态")
    p.add_argument("--ping-status", choices=["open", "closed"], help="Pingback 状态")
    p.add_argument("--sticky", type=bool, help="是否置顶")
    p.set_defaults(func=cmd_post_update)

    p = post_sub.add_parser("delete", help="删除文章")
    p.add_argument("id", type=int, help="文章 ID")
    p.add_argument("--force", action="store_true", help="跳过回收站直接删除")
    p.set_defaults(func=cmd_post_delete)

    # --- page ---
    page_p = subparsers.add_parser("page", help="页面管理")
    page_sub = page_p.add_subparsers(dest="page_cmd")

    p = page_sub.add_parser("list", help="列出页面")
    p.add_argument("--page", type=int, default=1, help="页码")
    p.add_argument("--per-page", type=int, default=10, help="每页数量")
    p.add_argument("--status", help="状态筛选: publish/draft/pending/private")
    p.add_argument("--search", help="搜索关键词")
    p.add_argument("--parent", type=int, help="父页面 ID 筛选")
    p.add_argument("--order", choices=["asc", "desc"], help="排序方向（默认 desc）")
    p.add_argument("--orderby", help="排序字段: date/id/title/slug/modified/author/menu_order")
    p.set_defaults(func=cmd_page_list)

    p = page_sub.add_parser("get", help="获取单个页面")
    p.add_argument("id", type=int, help="页面 ID")
    p.add_argument("--edit", action="store_true", help="获取编辑模式（含原始内容）")
    p.set_defaults(func=cmd_page_get)

    p = page_sub.add_parser("create", help="创建页面")
    p.add_argument("title", help="页面标题")
    p.add_argument("--content", help="正文内容（HTML）")
    p.add_argument("--content-file", help="从文件读取正文内容")
    p.add_argument("--status", default="draft", help="状态: draft/publish/pending/private（默认 draft）")
    p.add_argument("--excerpt", help="摘要")
    p.add_argument("--slug", help="URL Slug")
    p.add_argument("--parent", type=int, help="父页面 ID")
    p.add_argument("--featured-media", type=int, help="特色图媒体 ID")
    p.add_argument("--menu-order", type=int, help="菜单排序")
    p.add_argument("--comment-status", choices=["open", "closed"], help="评论状态")
    p.add_argument("--ping-status", choices=["open", "closed"], help="Pingback 状态")
    p.set_defaults(func=cmd_page_create)

    p = page_sub.add_parser("update", help="更新页面")
    p.add_argument("id", type=int, help="页面 ID")
    p.add_argument("--title", help="新标题")
    p.add_argument("--content", help="新正文")
    p.add_argument("--content-file", help="从文件读取新正文")
    p.add_argument("--status", help="新状态")
    p.add_argument("--excerpt", help="新摘要")
    p.add_argument("--slug", help="新 Slug")
    p.add_argument("--parent", type=int, help="新父页面 ID")
    p.add_argument("--featured-media", type=int, help="新特色图媒体 ID")
    p.add_argument("--menu-order", type=int, help="新菜单排序")
    p.add_argument("--comment-status", choices=["open", "closed"], help="评论状态")
    p.add_argument("--ping-status", choices=["open", "closed"], help="Pingback 状态")
    p.set_defaults(func=cmd_page_update)

    p = page_sub.add_parser("delete", help="删除页面")
    p.add_argument("id", type=int, help="页面 ID")
    p.add_argument("--force", action="store_true", help="跳过回收站直接删除")
    p.set_defaults(func=cmd_page_delete)

    # --- media ---
    media_p = subparsers.add_parser("media", help="媒体管理")
    media_sub = media_p.add_subparsers(dest="media_cmd")

    p = media_sub.add_parser("list", help="列出媒体")
    p.add_argument("--page", type=int, default=1)
    p.add_argument("--per-page", type=int, default=10)
    p.add_argument("--media-type", help="类型筛选: image/video/audio")
    p.add_argument("--search", help="搜索关键词")
    p.set_defaults(func=cmd_media_list)

    p = media_sub.add_parser("upload", help="上传媒体")
    p.add_argument("file", help="文件路径")
    p.add_argument("--alt", help="Alt 文本")
    p.set_defaults(func=cmd_media_upload)

    p = media_sub.add_parser("get", help="获取媒体详情")
    p.add_argument("id", type=int, help="媒体 ID")
    p.set_defaults(func=cmd_media_get)

    p = media_sub.add_parser("update", help="更新媒体元信息")
    p.add_argument("id", type=int, help="媒体 ID")
    p.add_argument("--alt", help="Alt 文本")
    p.add_argument("--caption", help="媒体说明")
    p.add_argument("--description", help="媒体描述")
    p.add_argument("--title", help="媒体标题")
    p.add_argument("--post", type=int, help="关联文章 ID")
    p.set_defaults(func=cmd_media_update)

    p = media_sub.add_parser("delete", help="删除媒体")
    p.add_argument("id", type=int, help="媒体 ID")
    p.set_defaults(func=cmd_media_delete)

    # --- category ---
    cat_p = subparsers.add_parser("category", help="分类管理")
    cat_sub = cat_p.add_subparsers(dest="cat_cmd")

    p = cat_sub.add_parser("list", help="列出分类")
    p.add_argument("--search", help="搜索分类名")
    p.set_defaults(func=cmd_cat_list)

    p = cat_sub.add_parser("create", help="创建分类")
    p.add_argument("name", help="分类名称")
    p.add_argument("--slug", help="Slug")
    p.add_argument("--parent", type=int, help="父分类 ID")
    p.set_defaults(func=cmd_cat_create)

    # --- tag ---
    tag_p = subparsers.add_parser("tag", help="标签管理")
    tag_sub = tag_p.add_subparsers(dest="tag_cmd")

    p = tag_sub.add_parser("list", help="列出标签")
    p.add_argument("--search", help="搜索标签名")
    p.set_defaults(func=cmd_tag_list)

    p = tag_sub.add_parser("create", help="创建标签")
    p.add_argument("name", help="标签名称")
    p.add_argument("--slug", help="Slug")
    p.set_defaults(func=cmd_tag_create)

    # --- search ---
    p = subparsers.add_parser("search", help="搜索站点内容")
    p.add_argument("query", help="搜索关键词")
    p.add_argument("--type", default="post", help="类型: post/term/post-format（默认 post）")
    p.add_argument("--subtype", help="子类型: post/page/category/post_tag")
    p.add_argument("--per-page", type=int, default=10)
    p.add_argument("--exclude", help="排除的 ID，逗号分隔")
    p.add_argument("--include", help="仅包含的 ID，逗号分隔")
    p.set_defaults(func=cmd_search)

    # 解析
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.parse_args([args.command, "-h"])


if __name__ == "__main__":
    main()
