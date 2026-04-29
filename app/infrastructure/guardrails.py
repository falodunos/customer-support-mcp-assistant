from app.domain.models import PlannedToolCall, AvailableTool


class GuardrailViolation(Exception):
    pass


class Guardrails:
    UNSUPPORTED_ACTION_PATTERNS = [
        "issue refund",
        "process refund",
        "send refund",
        "approve refund",
        "cancel order",
        "change address",
        "update address",
        "change delivery address",
        "modify order",
        "delete customer",
        "delete order",
        "charge card",
        "take payment",
        "change payment",
        "give discount",
        "apply discount",
        "override policy",
    ]

    def reject_unsupported_actions(self, question: str) -> None:
        normalized_question = question.lower()

        for pattern in self.UNSUPPORTED_ACTION_PATTERNS:
            if pattern in normalized_question:
                raise GuardrailViolation(
                    "This request appears to require a business-changing action "
                    "that the assistant is not authorized to perform. Please escalate "
                    "to a human support agent."
                )

    def validate_planned_tools(
        self,
        planned_tool_calls: list[PlannedToolCall],
        available_tools: list[AvailableTool],
    ) -> None:
        discovered_tool_names = {tool.name for tool in available_tools}

        for tool_call in planned_tool_calls:
            if tool_call.tool_name not in discovered_tool_names:
                raise GuardrailViolation(
                    f"Planner selected unsupported tool: {tool_call.tool_name}"
                )