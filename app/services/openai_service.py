"""
OpenAI Service for ShopAssistAI 2.0
Handles OpenAI model call with Function Calling schema.
"""

import os
from openai import OpenAI
from flask import current_app
from .functions_schema import FUNCTIONS_SCHEMA

_cached_client = None

def get_openai_client():
    global _cached_client
    if _cached_client:
        return _cached_client

    api_key = current_app.config.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Missing OPENAI_API_KEY")
    _cached_client = OpenAI(api_key=api_key)
    return _cached_client


def call_shop_assist_ai(message_history):
    try:
        current_app.logger.info("[OpenAI] Calling model...")
        client = get_openai_client()
        response = client.chat.completions.create(
            model=current_app.config.get("MODEL_NAME"),
            messages=message_history,
            functions=FUNCTIONS_SCHEMA,
            function_call="auto",
        )

        msg = response.choices[0].message

        # Handle function call
        if msg.function_call:
            fn_name = msg.function_call.name
            fn_args = msg.function_call.arguments
            return fn_name, fn_args

        # Normal chat message
        return "chat", msg.content or "[No response content]"

    except Exception as e:
        current_app.logger.error(f"[OpenAI Error] {e}")
        return "chat", "There was an error contacting the AI service."
