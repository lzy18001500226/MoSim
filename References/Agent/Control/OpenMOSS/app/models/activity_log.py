"""
活动日志表模型
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey

from app.database import Base


class ActivityLog(Base):
    __tablename__ = "activity_log"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String(36), ForeignKey("agent.id"), nullable=False, index=True, comment="操作 Agent")
    sub_task_id = Column(String(36), ForeignKey("sub_task.id"), nullable=True, index=True, comment="关联子任务（可为空）")
    action = Column(String(50), nullable=False, comment="操作类型: create_task/submit/review/claim 等")
    summary = Column(Text, default="", comment="操作摘要")
    session_id = Column(String(200), nullable=True, comment="OpenClaw 会话 ID")
    created_at = Column(DateTime, default=datetime.now, comment="操作时间")
