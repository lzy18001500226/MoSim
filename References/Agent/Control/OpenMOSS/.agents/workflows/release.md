---
description: Build and release from dev branch to main branch
---

# Release Workflow: dev → main

## Overview

- **dev branch**: 后端开发分支
- **main branch**: 稳定发布分支
- **webui branch**: 前端独立分支（orphan），通过 tag 独立发版
- 前端静态文件由后端 WebUIUpdater 服务启动时自动从 GitHub Release 下载，main 分支不再需要 `static/`

## Steps

// turbo
### 1. Ensure dev branch is ready

```bash
git checkout dev
git pull origin dev
git status
```

// turbo
### 2. Switch to main and merge dev

```bash
git checkout main
git pull origin main
git merge dev -m "merge: dev → main"
```

### 3. Push to remote

```bash
git push origin main
```

// turbo
### 4. Switch back to dev

```bash
git checkout dev
```

## WebUI Release (独立流程)

前端版本通过在 `webui` 分支上打 tag 发布：

```bash
# 在 webui 分支上打 tag（触发 CI 自动构建并发布到 GitHub Release）
git checkout webui
git tag webui-v0.0.1
git push origin webui-v0.0.1
```

> CI 会自动执行: npm ci → npm run build-only → 打包 webui-dist.tar.gz → 发布到 GitHub Release
> 后端 WebUIUpdater 会在启动时或通过管理端 API 自动拉取最新 Release
