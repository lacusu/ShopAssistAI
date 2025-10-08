"""
Conversation Service for ShopAssistAI 2.0
Handles message flow, OpenAI responses, and function calls.
"""

import json
from flask import current_app, session
from .openai_service import call_shop_assist_ai
from .product_service import map_products, recommend_products

# Keep track of the last used filters (for "show it" follow-ups)
_last_filters = None

def process_message(message_history):
    try:
        fn_name, fn_args = call_shop_assist_ai(message_history)
        current_app.logger.info(f"[Conversation] Function = {fn_name}")

        # --- Handle normal text reply ---
        if fn_name == "chat":
            return fn_args, False

        # --- Handle product recommendation call ---
        elif fn_name == "recommend_product":
            global _last_filters
            filters = json.loads(fn_args) if fn_args else {}

            # Reuse last filters if user says "show it"
            if not filters and _last_filters:
                filters = _last_filters
            else:
                _last_filters = filters

            products = map_products(filters)
            if not products:
                _last_filters = None
                not_found_msg = f"Sorry, I couldn't find any products matching your criteria. Please try different filters."
                # session["history"] = [
                #     {
                #         "role": "system",
                #         "content": not_found_msg
                #     }
                # ]
                return not_found_msg, True
            response = recommend_products({
                "products": products,
                "message": f"Here are top {len(products)} laptops matching your criteria:"
            })
            return response, False

        else:
            return f"Unknown function call: {fn_name}", False

    except Exception as e:
        current_app.logger.error(f"[Conversation Error] {e}")
        return "Sorry, something went wrong while processing your request.", False
