# -*- coding: utf-8 -*-
"""通知渠道模块初始化"""

from .email import EmailChannel
from .telegram import TelegramChannel
from .wechat import WeChatChannel

__all__ = ['EmailChannel', 'TelegramChannel', 'WeChatChannel']
