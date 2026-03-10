# -*- coding: utf-8 -*-

import json

import asyncio
import pytest

from copaw.app.channels.dingtalk.ai_card import (
    AICardPendingStore,
    ActiveAICard,
    INPUTING,
    thinking_or_tool_to_card_text,
)
from copaw.app.channels.dingtalk.channel import DingTalkChannel


class _FakeResponse:
    def __init__(self, status: int, body: dict):
        self.status = status
        self._text = json.dumps(body, ensure_ascii=False)

    async def text(self):
        return self._text


class _FakeRequestContext:
    def __init__(self, response: _FakeResponse):
        self._response = response

    async def __aenter__(self):
        return self._response

    async def __aexit__(self, exc_type, exc, tb):
        return False


class _FakeHTTP:
    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []

    def post(self, url, json=None, headers=None):
        self.calls.append({"url": url, "json": json, "headers": headers})
        return _FakeRequestContext(self._responses.pop(0))


async def _dummy_process(_request):
    if False:
        yield _request


def test_create_ai_card_dm_uses_sender_staff_id() -> None:
    ch = DingTalkChannel(
        process=_dummy_process,
        enabled=True,
        client_id="cid",
        client_secret="sec",
        bot_prefix="",
        message_type="card",
        card_template_id="tpl",
        card_template_key="content",
        robot_code="robot",
    )
    ch._http = _FakeHTTP(
        [
            _FakeResponse(200, {"success": True}),
            _FakeResponse(200, {"result": [{"success": True}], "success": True}),
        ],
    )

    async def _token():
        return "token"

    ch._get_access_token = _token

    asyncio.run(ch._create_ai_card(
        conversation_id="cid_chat_maybe_dm",
        is_group=False,
        sender_staff_id="staff123",
        inbound=False,
    ))

    create = ch._http.calls[0]["json"]
    assert create["imGroupOpenSpaceModel"] == {"supportForward": True}
    assert create["imRobotOpenSpaceModel"] == {"supportForward": True}

    deliver = ch._http.calls[1]["json"]
    assert deliver["openSpaceId"] == "dtv1.card//IM_ROBOT.staff123"
    assert deliver["imRobotOpenDeliverModel"] == {"spaceType": "IM_ROBOT"}


def test_create_ai_card_raises_on_deliver_business_failure() -> None:
    ch = DingTalkChannel(
        process=_dummy_process,
        enabled=True,
        client_id="cid",
        client_secret="sec",
        bot_prefix="",
        message_type="card",
        card_template_id="tpl",
        card_template_key="content",
        robot_code="robot",
    )
    ch._http = _FakeHTTP(
        [
            _FakeResponse(200, {"success": True}),
            _FakeResponse(
                200,
                {
                    "result": [
                        {
                            "success": False,
                            "errorMsg": "chatbot not exist",
                        }
                    ],
                    "success": True,
                },
            ),
        ],
    )

    async def _token():
        return "token"

    ch._get_access_token = _token

    with pytest.raises(RuntimeError, match="chatbot not exist"):
        asyncio.run(ch._create_ai_card(
            conversation_id="cid_any",
            is_group=True,
            sender_staff_id="",
            inbound=False,
        ))


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
