import json

from openai import OpenAI

from app.config import AppConfig
from app.domain.models import AvailableTool, ToolPlan

class ToolPlanner:
    def __init__(self):
        if not AppConfig.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required.")

        self.llm_client = OpenAI(api_key=AppConfig.OPENAI_API_KEY)

    def create_tool_plan(
        self,
        customer_id: str,
        order_id: str,
        question: str,
        available_tools: list[AvailableTool],
    ) -> ToolPlan:
        tools_json = [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_schema,
            }
            for tool in available_tools
        ]

        prompt = f"""
        You are a tool-planning assistant for a customer support system.

        Your job is to select only the MCP tools needed to answer the support question.

        Context:
        customer_id = {customer_id}
        order_id = {order_id}
        question = {question}

        Available MCP tools:
        {json.dumps(tools_json, indent=2)}

        Rules:
        - Return JSON only.
        - Use only tools from the available MCP tools list.
        - Do not invent tool names.
        - Do not call unnecessary tools.
        - Use the provided customer_id and order_id when required.
        - If no tool is relevant, return an empty tool_calls list.

        JSON response format:
        {{
          "reasoning": "brief reason for selected tools",
          "tool_calls": [
            {{
              "tool_name": "exact_tool_name",
              "arguments": {{
                "order_id": "ORD-1001"
              }}
            }}
          ]
        }}
        """

        response = self.llm_client.chat.completions.create(
            model=AppConfig.OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You select MCP tools and return valid JSON only.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0,
        )

        content = response.choices[0].message.content or "{}"
        data = json.loads(content)

        return ToolPlan(**data)