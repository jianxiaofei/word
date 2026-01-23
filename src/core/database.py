# -*- coding: utf-8 -*-
"""数据库管理器 - 向后兼容层（已重构）

此文件保留用于向后兼容。
新代码请使用: from core.db import DatabaseManager
"""

from .db.manager import DatabaseManager as _DatabaseManager

# 向后兼容：保持旧的导入路径可用
DatabaseManager = _DatabaseManager


# 为了完全兼容，也导出旧的函数
def get_db():
    """获取数据库实例（向后兼容）"""
    return DatabaseManager()
