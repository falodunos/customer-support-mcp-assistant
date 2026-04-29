from pydantic import BaseModel, Field

class SupportRequest(BaseModel):
    customer_id: str
    order_id: str
    question: str

class AvailableTool(BaseModel):
    name: str
    description: str | None = None
    input_schema: dict = Field(default_factory=dict)

class PlannedToolCall(BaseModel):
    tool_name: str
    arguments: dict

class ToolPlan(BaseModel):
    reasoning: str
    tool_calls: list[PlannedToolCall]

class ToolResult(BaseModel):
    tool_name: str
    arguments: dict
    result: str

class SupportResponse(BaseModel):
    customer_id: str
    order_id: str
    question: str
    selected_tools: list[str]
    tool_results: list[ToolResult]
    agent_response: str