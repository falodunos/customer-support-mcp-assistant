from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from app.domain.models import AvailableTool, PlannedToolCall, ToolResult

class SupportMcpClient:
    def __init__(self):
        self.server_command = "uv"
        self.server_args = ["run", "python", "mcp_server/support_server.py"]

    def _server_params(self) -> StdioServerParameters:
        return StdioServerParameters(
            command=self.server_command,
            args=self.server_args,
        )

    async def list_available_tools(self) -> list[AvailableTool]:
        async with stdio_client(self._server_params()) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()

                result = await session.list_tools()

                return [
                    AvailableTool(
                        name=tool.name,
                        description=tool.description,
                        input_schema=tool.inputSchema or {},
                    )
                    for tool in result.tools
                ]

    async def execute_tool_plan(
        self,
        tool_calls: list[PlannedToolCall],
    ) -> list[ToolResult]:
        async with stdio_client(self._server_params()) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()

                available_tools = await session.list_tools()
                allowed_tool_names = {tool.name for tool in available_tools.tools}

                results: list[ToolResult] = []

                for tool_call in tool_calls:
                    if tool_call.tool_name not in allowed_tool_names:
                        results.append(
                            ToolResult(
                                tool_name=tool_call.tool_name,
                                arguments=tool_call.arguments,
                                result="Tool was not found on the MCP server.",
                            )
                        )
                        continue

                    result = await session.call_tool(
                        tool_call.tool_name,
                        tool_call.arguments,
                    )

                    results.append(
                        ToolResult(
                            tool_name=tool_call.tool_name,
                            arguments=tool_call.arguments,
                            result=str(result.content),
                        )
                    )

                return results