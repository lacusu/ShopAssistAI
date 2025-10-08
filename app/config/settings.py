"""
Configuration loader for ShopAssistAI 2.0.
Reads values from .env using python-dotenv.
"""

import os
from dotenv import load_dotenv


def load_config():
    # Reads .env file in project root
    load_dotenv()
    # Returns config dictionary with defaults if not set
    return {
        "SECRET_KEY": os.getenv("SECRET_KEY", "dev-secret-key"),
        "SESSION_TYPE": "filesystem",
        "SESSION_PERMANENT": False,
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "MODEL_NAME": os.getenv("MODEL_NAME", "gpt-4o-mini"),
        "AI_NAME": os.getenv("AI_NAME", "ShopAssist AI"),  # AI display name
        "AI_WELCOME": os.getenv("AI_WELCOME",
                                "Hi there! I'm ShopAssist AI, your personal shopping assistant. How can I help you today?"),
        "CUSTOMER_NAME": os.getenv("CUSTOMER_NAME", "You"),
    }
