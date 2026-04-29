"""Unit tests for MCP client validation paths (no subprocess / MCP server)."""

import pytest

from app.infrastructure.support_mcp_client import SupportMcpClient


@pytest.mark.asyncio
async def test_execute_tool_blocks_unknown_tool_without_calling_server() -> None:
    client = SupportMcpClient()
    result = await client.execute_tool(
        tool_name="not_on_server",
        arguments={"order_id": "ORD-1"},
        allowed_tool_names={"allowed_tool_only"},
        request_id="unit-test-req",
    )
    assert result.tool_name == "not_on_server"
    assert result.arguments == {"order_id": "ORD-1"}
    assert "not found" in result.result.lower()


def test_server_params_use_uv_run_support_server() -> None:
    client = SupportMcpClient()
    params = client._server_params()
    assert params.command == "uv"
    assert params.args == ["run", "python", "mcp_server/support_server.py"]
