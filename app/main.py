import asyncio

import streamlit as st

from app.infrastructure.logging_config import configure_logging
from app.services.support_assistant_service import SupportAssistantService

configure_logging()


class CustomerSupportMcpApplication:
    def __init__(self):
        self.support_service = SupportAssistantService()

    def render(self) -> None:
        st.set_page_config(
            page_title="Customer Support MCP Assistant",
            page_icon="🎧",
            layout="wide",
        )

        st.title("🎧 Customer Support MCP Assistant")

        st.write(
            """
            This assistant discovers available MCP tools at runtime, selects the
            relevant tools for the support question, executes them dynamically,
            and generates a customer support response.
            """
        )

        with st.sidebar:
            st.header("Sample Test Data")
            st.write("Customer IDs: CUS-001, CUS-002, CUS-003")
            st.write("Order IDs: ORD-1001, ORD-1002, ORD-1003")

        customer_id = st.text_input("Customer ID", value="CUS-001")
        order_id = st.text_input("Order ID", value="ORD-1001")
        question = st.text_area(
            "Support Question",
            value="The customer wants to know where their order is and whether they can get a refund.",
        )

        if st.button("Resolve Support Request"):
            try:
                with st.spinner("Discovering MCP tools and resolving request..."):
                    response = asyncio.run(
                        self.support_service.resolve_support_question(
                            customer_id=customer_id,
                            order_id=order_id,
                            question=question,
                        )
                    )

                st.subheader("Recommended Agent Response")
                st.write(response.agent_response)

                st.subheader("Dynamically Selected MCP Tools")
                if response.selected_tools:
                    for tool_name in response.selected_tools:
                        st.write(f"- `{tool_name}`")
                else:
                    st.write("No tool selected.")

                st.subheader("MCP Tool Results")
                for tool_result in response.tool_results:
                    with st.expander(tool_result.tool_name):
                        st.write("Arguments")
                        st.json(tool_result.arguments)
                        st.write("Result")
                        st.write(tool_result.result)

            except ValueError as error:
                st.warning(str(error))

            except Exception:
                st.error(
                    "The support assistant could not complete this request. "
                    "Please check the application logs for details."
                )


def main() -> None:
    app = CustomerSupportMcpApplication()
    app.render()


if __name__ == "__main__":
    main()