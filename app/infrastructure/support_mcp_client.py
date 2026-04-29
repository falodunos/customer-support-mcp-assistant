from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from app.domain.models import AvailableTool, PlannedToolCall, ToolResult
from app.infrastructure.logging_config import get_logger


class SupportMcpClient:
    def __init__(self):
        self.server_command = "uv"
        self.server_args = ["run", "python", "mcp_server/support_server.py"]

    def _server_params(self) -> StdioServerParameters:
        return StdioServerParameters(
            command=self.server_command,
            args=self.server_args,
        )

    async def list_available_tools(self, request_id: str) -> list[AvailableTool]:
        logger = get_logger(__name__, request_id)

        logger.info("mcp_tool_discovery_started")

        try:
            async with stdio_client(self._server_params()) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()

                    result = await session.list_tools()

                    tools = [
                        AvailableTool(
                            name=tool.name,
                            description=tool.description,
                            input_schema=tool.inputSchema or {},
                        )
                        for tool in result.tools
                    ]

                    logger.info(
                        "mcp_tool_discovery_completed tool_count=%s tool_names=%s",
                        len(tools),
                        [tool.name for tool in tools],
                    )

                    return tools

        except Exception:
            logger.exception("mcp_tool_discovery_failed")
            raise

    async def execute_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        allowed_tool_names: set[str],
        request_id: str,
    ) -> ToolResult:
        logger = get_logger(__name__, request_id)

        safe_argument_keys = list(arguments.keys())

        if tool_name not in allowed_tool_names:
            logger.warning(
                "mcp_tool_blocked_unknown_tool tool_name=%s argument_keys=%s",
                tool_name,
                safe_argument_keys,
            )

            return ToolResult(
                tool_name=tool_name,
                arguments=arguments,
                result="Tool was not found on the MCP server.",
            )

        logger.info(
            "mcp_tool_execution_started tool_name=%s argument_keys=%s",
            tool_name,
            safe_argument_keys,
        )

        try:
            async with stdio_client(self._server_params()) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()

                    result = await session.call_tool(tool_name, arguments)

                    logger.info(
                        "mcp_tool_execution_completed tool_name=%s",
                        tool_name,
                    )

                    return ToolResult(
                        tool_name=tool_name,
                        arguments=arguments,
                        result=str(result.content),
                    )

        except Exception:
            logger.exception(
                "mcp_tool_execution_failed tool_name=%s argument_keys=%s",
                tool_name,
                safe_argument_keys,
            )
            raise

    async def execute_tool_plan(
        self,
        tool_calls: list[PlannedToolCall],
        request_id: str,
    ) -> list[ToolResult]:
        logger = get_logger(__name__, request_id)

        logger.info(
            "mcp_tool_plan_execution_started tool_call_count=%s selected_tools=%s",
            len(tool_calls),
            [tool_call.tool_name for tool_call in tool_calls],
        )

        try:
            async with stdio_client(self._server_params()) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()

                    available_tools = await session.list_tools()
                    allowed_tool_names = {tool.name for tool in available_tools.tools}

                    results: list[ToolResult] = []

                    for tool_call in tool_calls:
                        safe_argument_keys = list(tool_call.arguments.keys())

                        if tool_call.tool_name not in allowed_tool_names:
                            logger.warning(
                                "mcp_tool_blocked_unknown_tool tool_name=%s argument_keys=%s",
                                tool_call.tool_name,
                                safe_argument_keys,
                            )

                            results.append(
                                ToolResult(
                                    tool_name=tool_call.tool_name,
                                    arguments=tool_call.arguments,
                                    result="Tool was not found on the MCP server.",
                                )
                            )
                            continue

                        logger.info(
                            "mcp_tool_execution_started tool_name=%s argument_keys=%s",
                            tool_call.tool_name,
                            safe_argument_keys,
                        )

                        result = await session.call_tool(
                            tool_call.tool_name,
                            tool_call.arguments,
                        )

                        logger.info(
                            "mcp_tool_execution_completed tool_name=%s",
                            tool_call.tool_name,
                        )

                        results.append(
                            ToolResult(
                                tool_name=tool_call.tool_name,
                                arguments=tool_call.arguments,
                                result=str(result.content),
                            )
                        )

                    logger.info(
                        "mcp_tool_plan_execution_completed result_count=%s",
                        len(results),
                    )

                    return results

        except Exception:
            logger.exception("mcp_tool_plan_execution_failed")
            raise