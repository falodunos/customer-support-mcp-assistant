from openai import OpenAI

from app.config import AppConfig
from app.domain.models import SupportResponse, ToolResult
from app.infrastructure.support_mcp_client import SupportMcpClient
from app.services.tool_planner import ToolPlanner


class SupportAssistantService:
    def __init__(self):
        if not AppConfig.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required.")

        self.mcp_client = SupportMcpClient()
        self.tool_planner = ToolPlanner()
        self.llm_client = OpenAI(api_key=AppConfig.OPENAI_API_KEY)

    async def resolve_support_question(
        self,
        customer_id: str,
        order_id: str,
        question: str,
    ) -> SupportResponse:
        available_tools = await self.mcp_client.list_available_tools()

        tool_plan = self.tool_planner.create_tool_plan(
            customer_id=customer_id,
            order_id=order_id,
            question=question,
            available_tools=available_tools,
        )

        tool_results = await self.mcp_client.execute_tool_plan(tool_plan.tool_calls)

        agent_response = self._generate_agent_response(
            customer_id=customer_id,
            order_id=order_id,
            question=question,
            tool_results=tool_results,
        )

        return SupportResponse(
            customer_id=customer_id,
            order_id=order_id,
            question=question,
            selected_tools=[tool_call.tool_name for tool_call in tool_plan.tool_calls],
            tool_results=tool_results,
            agent_response=agent_response,
        )

    def _generate_agent_response(
        self,
        customer_id: str,
        order_id: str,
        question: str,
        tool_results: list[ToolResult],
    ) -> str:
        if not tool_results:
            return (
                "I could not find a relevant MCP tool to answer this support request. "
                "Please escalate this case to a human support agent."
            )

        tool_context = "\n\n".join(
            [
                f"""
                Tool: {tool_result.tool_name}
                Arguments: {tool_result.arguments}
                Result: {tool_result.result}
                """
                for tool_result in tool_results
            ]
        )

        prompt = f"""
        You are a customer support assistant for an e-commerce company.

        Customer ID:
        {customer_id}

        Order ID:
        {order_id}

        Support question:
        {question}

        MCP tool results:
        {tool_context}

        Write a clear support-agent response.

        Rules:
        - Use only the MCP tool results.
        - Do not invent facts.
        - Be empathetic and concise.
        - Include the next best action.
        """

        response = self.llm_client.chat.completions.create(
            model=AppConfig.OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You write support responses based only on MCP tool results.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )

        return response.choices[0].message.content or "No response generated."