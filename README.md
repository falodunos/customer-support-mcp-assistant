# Customer Support MCP Assistant

## Problem

E-commerce support agents spend too much time switching between order, shipping, and refund systems to answer basic customer questions.

## Solution

This application uses a Customer Support MCP Server to expose business tools for order status, shipping status, and refund eligibility. A Streamlit app calls those tools through an MCP client and generates a clear support response.

## Stack

- Python
- uv
- Streamlit
- MCP Python SDK
- OpenAI-compatible LLM

## MCP Tools

- get_order_status
- get_shipping_status
- check_refund_eligibility

## Run Locally

```bash
uv sync
uv run streamlit run app/main.py