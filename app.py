"""
ChatCure AI - Medical Chatbot Backend
======================================
A robust, asynchronous Flask application providing medical intelligence
powered by the OpenRouter API.

Features:
- Asynchronous route handlers (async/await) with httpx
- Strict medical domain specialization & safety guardrails
- Comprehensive input validation & error handling
- Secure environment configuration via python-dotenv
- Graceful offline/demo fallback mode when API key is not yet configured
"""

import os
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any

import httpx
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify

from medical_service import (
    MEDICAL_SYSTEM_PROMPT,
    is_non_medical_query,
    get_domain_refusal_message,
    get_demo_response,
    validate_chat_input
)

# ---------------------------------------------------------------------------
# Configuration & Initialization
# ---------------------------------------------------------------------------
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("ChatCure")

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)

# OpenRouter Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct").strip()
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    """
    Serve the main ChatCure Medical Web Interface.
    """
    return render_template("index.html")


@app.route("/health", methods=["GET"])
def health_check():
    """
    Application health status and API configuration diagnostic.
    """
    has_api_key = bool(OPENROUTER_API_KEY and OPENROUTER_API_KEY != "your_openrouter_api_key_here")
    return jsonify({
        "status": "healthy",
        "service": "ChatCure Medical AI (Flask)",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model": OPENROUTER_MODEL,
        "api_configured": has_api_key
    }), 200


@app.route("/chat", methods=["POST"])
async def chat():
    """
    Asynchronous medical chat endpoint.
    Receives user messages, performs input validation, applies strict medical
    guardrails, calls the OpenRouter API asynchronously, and returns JSON.
    """
    # 1. Validation: Request Body Format
    if not request.is_json:
        return jsonify({
            "success": False,
            "error": "Invalid Content-Type. Expected application/json."
        }), 400

    try:
        data = request.get_json(silent=True)
    except Exception as parse_err:
        logger.warning(f"JSON parsing error: {parse_err}")
        return jsonify({
            "success": False,
            "error": "Malformed JSON payload."
        }), 400

    is_valid, user_message, error_msg, valid_history = validate_chat_input(data)
    if not is_valid:
        return jsonify({
            "success": False,
            "error": error_msg
        }), 400

    timestamp = datetime.now(timezone.utc).isoformat()

    # 2. Domain Boundary Guardrail Check
    if is_non_medical_query(user_message):
        logger.info(f"Guardrail intercepted non-medical query: '{user_message[:60]}...'")
        return jsonify({
            "success": True,
            "response": get_domain_refusal_message(),
            "model": "chatcure-guardrail",
            "timestamp": timestamp
        }), 200

    # 3. Check for OpenRouter API Key Configuration
    has_valid_key = bool(
        OPENROUTER_API_KEY
        and OPENROUTER_API_KEY != "your_openrouter_api_key_here"
        and not OPENROUTER_API_KEY.startswith("sk-placeholder")
    )

    if not has_valid_key:
        logger.warning("No OpenRouter API key provided. Falling back to offline medical preview.")
        demo_reply = get_demo_response(user_message)
        return jsonify({
            "success": True,
            "response": demo_reply,
            "model": "chatcure-demo-engine",
            "timestamp": timestamp
        }), 200

    # 4. Build Asynchronous OpenRouter API Request
    messages = [{"role": "system", "content": MEDICAL_SYSTEM_PROMPT}]
    messages.extend(valid_history)
    messages.append({"role": "user", "content": user_message})

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": messages,
        "temperature": 0.4,  # Lower temperature for accurate clinical facts
        "max_tokens": 1200,
        "top_p": 0.9,
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://chatcure.ai",
        "X-Title": "ChatCure AI Medical Assistant",
    }

    # 5. Execute Asynchronous Call with Robust Exception Handling
    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post(
                OPENROUTER_URL,
                json=payload,
                headers=headers
            )

        # Handle HTTP Status Codes from OpenRouter
        if response.status_code == 200:
            result = response.json()
            choices = result.get("choices", [])
            if choices and len(choices) > 0:
                ai_text = choices[0].get("message", {}).get("content", "").strip()
                if not ai_text:
                    ai_text = "I received an empty response from the medical knowledge base. Please rephrase your question."
                return jsonify({
                    "success": True,
                    "response": ai_text,
                    "model": result.get("model", OPENROUTER_MODEL),
                    "timestamp": timestamp
                }), 200
            else:
                logger.error(f"OpenRouter returned empty choices: {result}")
                return jsonify({
                    "success": False,
                    "error": "The AI model returned no content. Please try again."
                }), 502

        elif response.status_code == 401:
            logger.error("OpenRouter authentication failed: Invalid API key.")
            return jsonify({
                "success": False,
                "error": "Authentication failed with OpenRouter. Please verify your OPENROUTER_API_KEY in the .env file."
            }), 401

        elif response.status_code == 429:
            logger.warning("OpenRouter rate limit or credit exhaustion encountered.")
            return jsonify({
                "success": False,
                "error": "Rate limit exceeded or insufficient OpenRouter credits. Please wait a moment or check your account."
            }), 429

        else:
            logger.error(f"OpenRouter upstream error [{response.status_code}]: {response.text}")
            return jsonify({
                "success": False,
                "error": f"Medical AI service temporarily unavailable (Error {response.status_code}). Please try again shortly."
            }), 502

    except httpx.TimeoutException:
        logger.error("Request to OpenRouter API timed out after 45 seconds.")
        return jsonify({
            "success": False,
            "error": "The medical consultation request timed out. Please try again with a shorter question."
        }), 504

    except httpx.ConnectError:
        logger.error("Network connection error to OpenRouter.")
        return jsonify({
            "success": False,
            "error": "Unable to connect to the medical AI server. Please verify your internet connection."
        }), 503

    except Exception as exc:
        logger.exception(f"Unexpected error in /chat handler: {exc}")
        return jsonify({
            "success": False,
            "error": "An unexpected server error occurred while processing your medical inquiry."
        }), 500


# ---------------------------------------------------------------------------
# Global Error Handlers
# ---------------------------------------------------------------------------
@app.errorhandler(404)
def not_found_handler(e):
    if request.path.startswith("/chat") or request.path.startswith("/health"):
        return jsonify({"success": False, "error": "Endpoint not found."}), 404
    return render_template("index.html"), 404


@app.errorhandler(500)
def server_error_handler(e):
    return jsonify({"success": False, "error": "Internal server error occurred."}), 500


# ---------------------------------------------------------------------------
# Application Entry Point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", 5000))
    host = os.getenv("HOST", "127.0.0.1")
    debug = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")

    print("\n" + "=" * 65)
    print(" 🏥  ChatCure AI - Medical Chatbot Platform (Flask)")
    print(f" 🌐  Server running at: http://{host}:{port}/")
    print(f" 🤖  Active Model: {OPENROUTER_MODEL}")
    has_key = bool(OPENROUTER_API_KEY and OPENROUTER_API_KEY != "your_openrouter_api_key_here")
    print(f" 🔑  OpenRouter API Key: {'Configured ✅' if has_key else 'Missing (Demo Fallback Active) ⚠️'}")
    print("=" * 65 + "\n")

    app.run(host=host, port=port, debug=debug)
