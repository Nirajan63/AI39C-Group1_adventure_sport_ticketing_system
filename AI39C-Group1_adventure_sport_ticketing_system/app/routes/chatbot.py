# app/routes/chatbot.py
"""
/chat endpoint -- now backed by a context-aware LangChain agent instead of a
plain Hugging Face text-generation call. The agent has tool access to live
activity/event/booking data and an FAQ knowledge base, so answers are
grounded in the actual site instead of a fixed script of predefined Q&A.

Request body (JSON):
    { "message": "is paragliding available tomorrow?", "history": [...] }

    history is optional: a list of {"role": "user"|"assistant", "content"}
    objects representing the conversation so far. The frontend widget keeps
    this in memory client-side and resends it each turn.

Response body (JSON):
    { "reply": "..." }

On any failure, this endpoint still returns 200 with a friendly fallback
"reply" string rather than surfacing a raw error to the chat widget --
matching the original behavior so the frontend never needs special-case
error handling.
"""

import os
from flask import Blueprint, request, jsonify, session, current_app

chatbot_bp = Blueprint('chatbot', __name__)


@chatbot_bp.route('/chat', methods=['POST'])
def chat():
    data = request.get_json(silent=True) or {}
    user_msg = (data.get('message') or '').strip()
    history = data.get('history') or []

    if not user_msg:
        return jsonify({'error': 'No message provided'}), 400

    # Ensure OpenRouter API key is configured
    if not os.getenv('OPENROUTER_API_KEY'):
        current_app.logger.error('OPENROUTER_API_KEY not set')
        return jsonify({
            'reply': "Sorry, the chatbot service is currently unavailable because the required API key is not configured. Please contact support to set it up."
        })

    try:
        from app.chatbot.agent import get_agent_response
        user = session.get('user')
        user_id = user.get('id') if user else None
        reply = get_agent_response(user_msg, history, user_id=user_id)
        return jsonify({'reply': reply})
    except Exception as e:
        current_app.logger.error(f"Chatbot agent error: {e}")
        return jsonify({
            'reply': "Sorry, I'm having trouble answering right now. You can also browse "
                     "Activities/Events directly or check the FAQ on this page."
        })
key = os.getenv('OPENROUTER_API_KEY')
print("OPENROUTER_API_KEY:", (key[:8] + "...") if key else "Not Set")
