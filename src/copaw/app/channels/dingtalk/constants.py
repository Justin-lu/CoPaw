# -*- coding: utf-8 -*-
"""DingTalk channel constants."""

# When consumer sends all messages via sessionWebhook, process() skips reply
SENT_VIA_WEBHOOK = "__SENT_VIA_WEBHOOK__"

# Token cache TTL (1 hour)
DINGTALK_TOKEN_TTL_SECONDS = 3600

# Time debounce (300ms)
DINGTALK_DEBOUNCE_SECONDS = 0.3

# Short suffix length for session_id from conversation_id
DINGTALK_SESSION_ID_SUFFIX_LEN = 8

# DingTalk message type to runtime content type
DINGTALK_TYPE_MAPPING = {
    "picture": "image",
}

AI_CARD_TOKEN_PREEMPTIVE_REFRESH_SECONDS = 90 * 60
AI_CARD_RECOVERY_FINAL_TEXT = "⚠️ 上一次回复处理中断，已自动结束。请重新发送你的问题。"
