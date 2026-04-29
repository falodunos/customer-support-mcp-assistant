"""Unit tests for service orchestration (dependencies mocked)."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.config import AppConfig
from app.domain.models import AvailableTool, PlannedToolCall, ToolPlan, ToolResult
from app.services.support_assistant_service import SupportAssistantService


@pytest.fixture
def api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(AppConfig, "OPENAI_API_KEY", "sk-test-key", raising=False)
    monkeypatch.setattr(AppConfig, "OPENAI_MODEL", "gpt-4o-mini", raising=False)


@pytest.mark.asyncio
async def test_resolve_support_question_returns_escalation_when_no_tool_results(
    api_key: None,
) -> None:
    service = SupportAssistantService()
    service.mcp_client.list_available_tools = AsyncMock(return_value=[])
    service.tool_planner.create_tool_plan = MagicMock(
        return_value=ToolPlan(reasoning="none", tool_calls=[]),
    )
    service.mcp_client.execute_tool_plan = AsyncMock(return_value=[])

    response = await service.resolve_support_question(
        customer_id="CUS-001",
        order_id="ORD-1001",
        question="Any question?",
    )

    assert response.customer_id == "CUS-001"
    assert response.order_id == "ORD-1001"
    assert response.question == "Any question?"
    assert response.selected_tools == []
    assert response.tool_results == []
    assert "human support" in response.agent_response.lower()


@pytest.mark.asyncio
async def test_resolve_support_question_wires_planner_and_mcp_and_response(
    api_key: None,
) -> None:
    service = SupportAssistantService()
    tool_plan = ToolPlan(
        reasoning="because",
        tool_calls=[
            PlannedToolCall(
                tool_name="get_shipping_status",
                arguments={"order_id": "ORD-1001"},
            ),
        ],
    )
    tool_results = [
        ToolResult(
            tool_name="get_shipping_status",
            arguments={"order_id": "ORD-1001"},
            result="Shipped",
        ),
    ]

    service.mcp_client.list_available_tools = AsyncMock(
        return_value=[
            AvailableTool(
                name="get_shipping_status",
                description="Track order",
                input_schema={},
            ),
        ],
    )
    service.tool_planner.create_tool_plan = MagicMock(return_value=tool_plan)
    service.mcp_client.execute_tool_plan = AsyncMock(return_value=tool_results)
    service._generate_agent_response = MagicMock(return_value="Final reply.")

    response = await service.resolve_support_question(
        customer_id="CUS-002",
        order_id="ORD-2002",
        question="Status please?",
    )

    assert response.customer_id == "CUS-002"
    assert response.order_id == "ORD-2002"
    assert response.question == "Status please?"
    assert response.selected_tools == ["get_shipping_status"]
    assert response.tool_results == tool_results
    assert response.agent_response == "Final reply."

    service.tool_planner.create_tool_plan.assert_called_once()
    service.mcp_client.execute_tool_plan.assert_awaited_once()
    service._generate_agent_response.assert_called_once()
