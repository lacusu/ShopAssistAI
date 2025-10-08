"""
Flask routes for ShopAssistAI 2.0
Handles chat input, session memory, and page rendering.
"""
import pandas as pd
from flask import Blueprint, render_template, request, jsonify, session, current_app
from .services.conversation_service import process_message

bp = Blueprint("main", __name__)


# ---------------------------------------------------------------------
# Home page
# ---------------------------------------------------------------------
@bp.route("/")
def index():
    # Initialize chat history in session if missing
    if "history" not in session:
        session["history"] = [
            {"role": "system",
             "content": current_app.config.get(
                 "AI_DESCRIPTION",
                 "You are ShopAssist AI, a helpful laptop assistant."
             ), }]
    return render_template("index.html")


# ---------------------------------------------------------------------
# Chat endpoint
# ---------------------------------------------------------------------
@bp.route("/chat", methods=["POST"])
def chat():
    try:
        user_input = request.json.get("message", "").strip()
        if not user_input:
            return jsonify({"response": "Please type a message."})

        history = session.get("history", [])
        history.append({"role": "user", "content": user_input})

        # Call AI
        reply, reset_context = process_message(history)
        if reset_context:
            session["history"] = [
                {
                    "role": "system",
                    "content": reply
                }
            ]
        else:
            history.append({"role": "assistant", "content": reply})
            session["history"] = history

        ai_name = current_app.config.get("AI_NAME", "ShopAssist AI")

        response_payload = {
            "role": "assistant",
            "name": ai_name,
            "message": reply,
            "timestamp": pd.Timestamp.now().isoformat(),
        }

        return jsonify(response_payload)

    except Exception as e:
        current_app.logger.error(f"[Chat Error] {e}")
        return jsonify({
            "role": "assistant",
            "name": "System",
            "message": "An error occurred while processing your message."
        })


# ---------------------------------------------------------------------
# Clear chat session
# ---------------------------------------------------------------------
@bp.route("/clear", methods=["POST"])
def clear():
    session.pop("history", None)
    return jsonify({"response": "Chat history cleared."})
