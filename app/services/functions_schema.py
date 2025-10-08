"""
Function schema definitions for ShopAssistAI 2.0
"""

FUNCTIONS_SCHEMA = [
    {
        "name": "recommend_product",
        "description": "Recommend laptops matching user requirements.",
        "parameters": {
            "type": "object",
            "properties": {
                "brand": {"type": "string", "description": "Brand or company name (e.g., Dell, HP, Apple)."},
                "cpu": {"type": "string", "description": "CPU keyword (e.g., i7, Ryzen 5, M2)."},
                "ram": {"type": "string", "description": "RAM amount (e.g., 8GB, 16GB)."},
                "gpu": {"type": "string", "description": "Graphics processor keyword (e.g., RTX, Radeon)."},
                "os": {"type": "string", "description": "Operating system (e.g., Windows, macOS, Linux)."},
                "category": {"type": "string", "description": "Laptop type (e.g., gaming, ultrabook, business)."},
                "price_range": {
                    "type": "string",
                    "enum": ["low", "mid", "high"],
                    "description": "Price segment: low (<$500), mid ($500–1000), or high (>$1000)."
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results to return (e.g., 3 or 5). Default 10."
                }
            },
            "required": [],
        },
    }
]
