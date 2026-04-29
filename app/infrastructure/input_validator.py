import re


class InputValidator:
    CUSTOMER_ID_PATTERN = re.compile(r"^CUS-\d{3,10}$")
    ORDER_ID_PATTERN = re.compile(r"^ORD-\d{3,10}$")

    MAX_QUESTION_LENGTH = 500

    UNSAFE_PATTERNS = [
        "ignore previous instructions",
        "ignore all previous instructions",
        "system prompt",
        "developer message",
        "reveal secrets",
        "show api key",
        "print env",
        "bypass",
        "jailbreak",
    ]

    def validate_support_request(
        self,
        customer_id: str,
        order_id: str,
        question: str,
    ) -> None:
        customer_id = customer_id.strip()
        order_id = order_id.strip()
        question = question.strip()

        if not self.CUSTOMER_ID_PATTERN.match(customer_id):
            raise ValueError("Customer ID must look like CUS-001.")

        if not self.ORDER_ID_PATTERN.match(order_id):
            raise ValueError("Order ID must look like ORD-1001.")

        if not question:
            raise ValueError("Support question cannot be empty.")

        if len(question) > self.MAX_QUESTION_LENGTH:
            raise ValueError(
                f"Support question cannot exceed {self.MAX_QUESTION_LENGTH} characters."
            )

        lowered_question = question.lower()

        for unsafe_pattern in self.UNSAFE_PATTERNS:
            if unsafe_pattern in lowered_question:
                raise ValueError("Support question contains unsafe instruction-like content.")