# -*- coding: utf-8 -*-

import json

from copaw.app.channels.dingtalk.ai_card import (
    AICardPendingStore,
    ActiveAICard,
    INPUTING,
    is_group_conversation,
    thinking_or_tool_to_card_text,
)


def test_is_group_conversation() -> None:
    assert is_group_conversation("cid123") is True
    assert is_group_conversation("user_1") is False


def test_thinking_or_tool_to_card_text_truncate_and_quote() -> None:
    text = "a" * 600
    out = thinking_or_tool_to_card_text(text, "🤔 **思考中**")
    assert out.startswith("🤔 **思考中**\n> ")
    assert out.endswith("…")


def test_pending_store_roundtrip(tmp_path) -> None:
    store = AICardPendingStore(tmp_path / "dingtalk-active-cards.json")
    card = ActiveAICard(
        card_instance_id="card_x",
        access_token="t",
        conversation_id="cid1",
        account_id="default",
        store_path=str(tmp_path),
        created_at=1,
        last_updated=2,
        state=INPUTING,
    )
    store.save({"cid1": card})
    loaded = store.load()
    assert len(loaded) == 1
    assert loaded[0]["card_instance_id"] == "card_x"
    data = json.loads((tmp_path / "dingtalk-active-cards.json").read_text())
    assert data["version"] == 1
