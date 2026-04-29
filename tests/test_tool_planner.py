"""Unit tests for tool plan JSON parsing (same shape ToolPlanner expects from the LLM)."""

import json
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from app.config import AppConfig
from app.domain.models import AvailableTool, ToolPlan
from app.services.tool_planner import ToolPlanner


def test_tool_plan_parses_valid_llm_payload() -> None:
    payload = {
        "reasoning": "Customer needs shipping and refund info.",
        "tool_calls": [
            {
                "tool_name": "get_shipping_status",
                "arguments": {"order_id": "ORD-1001"},
            },
            {
                "tool_name": "check_refund_eligibility",
                "arguments": {"order_id": "ORD-1001"},
            },
        ],
    }
    plan = ToolPlan.model_validate(payload)
    assert plan.reasoning.startswith("Customer needs")
    assert [c.tool_name for c in plan.tool_calls] == [
        "get_shipping_status",
        "check_refund_eligibility",
    ]
    assert plan.tool_calls[0].arguments["order_id"] == "ORD-1001"


def test_tool_plan_rejects_missing_tool_calls() -> None:
    with pytest.raises(ValidationError):
        ToolPlan.model_validate({"reasoning": "only reasoning"})


def test_create_tool_plan_parses_openai_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(AppConfig, "OPENAI_API_KEY", "sk-test-key", raising=False)
    monkeypatch.setattr(AppConfig, "OPENAI_MODEL", "gpt-4o-mini", raising=False)

    planner = ToolPlanner()
    expected = ToolPlan(
        reasoning="test",
        tool_calls=[],
    )
    content = json.dumps(
        {"reasoning": expected.reasoning, "tool_calls": []},
    )
    fake_message = MagicMock(content=content)
    fake_choice = MagicMock(message=fake_message)
    fake_response = MagicMock(choices=[fake_choice])
    planner.llm_client = MagicMock()
    planner.llm_client.chat.completions.create = MagicMock(return_value=fake_response)

    available = [
        AvailableTool(name="get_shipping_status", description="Ship", input_schema={}),
    ]
    plan = planner.create_tool_plan(
        customer_id="CUS-1",
        order_id="ORD-1",
        question="Where is my order?",
        available_tools=available,
        request_id="req-test",
    )

    assert plan.reasoning == "test"
    assert plan.tool_calls == []
