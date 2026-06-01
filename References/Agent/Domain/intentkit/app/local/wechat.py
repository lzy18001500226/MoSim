"""IntentKit Local WeChat API Router.

Provides endpoints for WeChat QR code login flow and channel connection.
The frontend calls these endpoints to initiate WeChat bot login via iLink API.
"""

import logging

from fastapi import APIRouter, Body, Query

from intentkit.core.team.channel import set_team_channel
from intentkit.models.team_channel import TeamChannel

from app.common.wechat import (
    WechatConnectRequest,
    WechatQrCodeResponse,
    WechatQrStatusResponse,
    fetch_wechat_qrcode,
    poll_wechat_qrcode,
)

logger = logging.getLogger(__name__)

wechat_router = APIRouter(tags=["WeChat"])

# Hardcoded IDs for local single-user development (same as lead.py)
LEAD_TEAM_ID = "system"
LEAD_USER_ID = "system"


@wechat_router.get(
    "/wechat/qrcode",
    response_model=WechatQrCodeResponse,
    operation_id="get_wechat_qrcode",
    summary="Get WeChat login QR code",
)
async def get_wechat_qrcode():
    """Call iLink API to generate a QR code for WeChat bot login."""
    return await fetch_wechat_qrcode()


@wechat_router.get(
    "/wechat/qrcode/status",
    response_model=WechatQrStatusResponse,
    operation_id="poll_wechat_qrcode_status",
    summary="Poll WeChat QR code scan status",
)
async def poll_wechat_qrcode_status(
    qrcode: str = Query(..., description="QR code UUID from get_wechat_qrcode"),
):
    """Poll iLink API for QR code scan confirmation status."""
    return await poll_wechat_qrcode(qrcode)


@wechat_router.post(
    "/wechat/connect",
    response_model=TeamChannel,
    operation_id="connect_wechat_channel",
    summary="Save WeChat credentials after QR scan",
)
async def connect_wechat_channel(
    request: WechatConnectRequest = Body(...),
):
    """Save WeChat bot credentials to team_channels after successful QR scan."""
    config: dict[str, object] = {
        "bot_token": request.bot_token,
        "baseurl": request.baseurl,
        "ilink_bot_id": request.ilink_bot_id,
        "user_id": request.user_id,
    }
    return await set_team_channel(
        LEAD_TEAM_ID, "wechat", config, created_by=LEAD_USER_ID
    )
