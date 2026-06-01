"""
WebUI 前端版本管理路由

提供 WebUI 版本检查和更新触发接口。
"""
from fastapi import APIRouter, HTTPException, Depends

from app.auth.dependencies import verify_admin
from app.services.webui_updater import webui_updater

router = APIRouter(tags=["WebUI"])


@router.get("/webui/version", summary="获取 WebUI 版本信息")
async def get_webui_version():
    """获取当前 WebUI 版本和更新状态。

    前端页面加载时调用此接口，触发后台版本检查（带 30 分钟 cooldown）。
    无需认证，任何访问者都可以查看版本信息。
    """
    result = await webui_updater.check_for_update()
    return result.to_dict()


@router.get("/webui/version/check", summary="强制检查 WebUI 更新")
async def check_webui_update(_=Depends(verify_admin)):
    """强制检查 WebUI 更新（跳过 cooldown）。

    管理员专用，用于手动触发版本检查。
    """
    result = await webui_updater.check_for_update(force=True)
    return result.to_dict()


@router.post("/admin/webui/update", summary="触发 WebUI 更新")
async def trigger_webui_update(_=Depends(verify_admin)):
    """手动触发 WebUI 更新或回滚。

    下载 GitHub Release 最新版本并部署到 static/ 目录。
    如果当前版本已被撤回（标记为 pre-release），会自动降级到安全版本。

    部署过程：
    1. 下载 webui-dist.tar.gz
    2. 备份当前 static/ → static.bak/
    3. 解压新版本到 static/
    4. 验证 index.html 存在
    5. 清理备份（失败时自动恢复）
    """
    if webui_updater.is_updating:
        raise HTTPException(status_code=409, detail="另一个更新正在进行中")

    result = await webui_updater.download_and_apply()

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])

    return result
