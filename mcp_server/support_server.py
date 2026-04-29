from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Customer Support MCP Server")


ORDERS = {
    "ORD-1001": {
        "customer_id": "CUS-001",
        "status": "SHIPPED",
        "items": ["Wireless Mouse", "USB-C Charger"],
        "total": 37000,
        "payment_status": "PAID",
    },
    "ORD-1002": {
        "customer_id": "CUS-002",
        "status": "PROCESSING",
        "items": ["Office Chair"],
        "total": 85000,
        "payment_status": "PAID",
    },
    "ORD-1003": {
        "customer_id": "CUS-003",
        "status": "DELIVERED",
        "items": ["Notebook Pack", "Premium Pen"],
        "total": 15000,
        "payment_status": "PAID",
    },
}


SHIPMENTS = {
    "ORD-1001": {
        "carrier": "DHL",
        "tracking_number": "DHL-998877",
        "shipping_status": "IN_TRANSIT",
        "estimated_delivery": "2026-05-02",
    },
    "ORD-1002": {
        "carrier": "Internal Dispatch",
        "tracking_number": None,
        "shipping_status": "NOT_SHIPPED",
        "estimated_delivery": "2026-05-05",
    },
    "ORD-1003": {
        "carrier": "GIG Logistics",
        "tracking_number": "GIG-123456",
        "shipping_status": "DELIVERED",
        "estimated_delivery": "2026-04-25",
    },
}


@mcp.tool()
def get_order_status(order_id: str) -> dict:
    """Return order status and payment information for a customer order."""
    order = ORDERS.get(order_id)

    if not order:
        return {
            "found": False,
            "message": f"No order found for order_id {order_id}",
        }

    return {
        "found": True,
        "order_id": order_id,
        **order,
    }


@mcp.tool()
def get_shipping_status(order_id: str) -> dict:
    """Return shipping and delivery information for a customer order."""
    shipment = SHIPMENTS.get(order_id)

    if not shipment:
        return {
            "found": False,
            "message": f"No shipment found for order_id {order_id}",
        }

    return {
        "found": True,
        "order_id": order_id,
        **shipment,
    }


@mcp.tool()
def check_refund_eligibility(order_id: str) -> dict:
    """Check whether an order is eligible for refund based on simple business rules."""
    order = ORDERS.get(order_id)
    shipment = SHIPMENTS.get(order_id)

    if not order:
        return {
            "eligible": False,
            "reason": "Order does not exist.",
        }

    if order["payment_status"] != "PAID":
        return {
            "eligible": False,
            "reason": "Order has not been paid.",
        }

    if shipment and shipment["shipping_status"] == "DELIVERED":
        return {
            "eligible": True,
            "reason": "Order was delivered and can be reviewed under the return policy.",
        }

    if order["status"] == "PROCESSING":
        return {
            "eligible": True,
            "reason": "Order is still processing and can be cancelled or refunded.",
        }

    return {
        "eligible": False,
        "reason": "Order is already in transit and requires support manager approval.",
    }


if __name__ == "__main__":
    mcp.run()