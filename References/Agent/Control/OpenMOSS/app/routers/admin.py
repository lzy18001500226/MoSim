"""
管理端路由 — 登录
"""
import secrets
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.config import config


router = APIRouter(prefix="/admin", tags=["Admin"])


# ============================================================
# 管理员会话 Token 存储（内存）
# ============================================================

# 存储有效的 admin session token（服务重启后失效，需重新登录）
_admin_tokens: set[str] = set()


def create_admin_token() -> str:
    """生成随机 admin session token 并存入内存"""
    token = secrets.token_hex(32)
    _admin_tokens.add(token)
    return token


def is_valid_admin_token(token: str) -> bool:
    """验证 admin session token 是否有效"""
    return token in _admin_tokens


# ============================================================
# 请求/响应模型
# ============================================================

class AdminLoginRequest(BaseModel):
    password: str = Field(..., description="管理员密码")


class AdminLoginResponse(BaseModel):
    token: str
    message: str = "登录成功"


# ============================================================
# 路由
# ============================================================

@router.post("/login", response_model=AdminLoginResponse, summary="管理员登录")
async def admin_login(req: AdminLoginRequest):
    """
    管理员使用密码登录，返回随机 session token。
    后续管理操作通过 Header X-Admin-Token 传递此 token。
    token 在服务重启后失效，需重新登录。
    """
    if not config.verify_admin_password(req.password):
        raise HTTPException(status_code=403, detail="密码错误")

    token = create_admin_token()
    return AdminLoginResponse(token=token)
