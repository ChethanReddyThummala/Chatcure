"""
ChatCure AI - FastAPI Medical Backend
======================================
Alternative FastAPI implementation offering ASGI asynchronous performance,
Pydantic schema validation, and OpenRouter AI integration.

To run:
    uvicorn fastapi_app:app --reload --port 8000
"""

import os
import logging
from datetime import datetime, timezone
from typing import List, Optional

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from medical_service import (
    MEDICAL_SYSTEM_PROMPT,
    is_non_medical_query,
    get_domain_refusal_message,
    get_demo_response
)

# Load environment configuration
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("ChatCure-FastAPI")

app = FastAPI(
    title="ChatCure AI Medical Assistant",
    description="Professional AI Medical Chatbot API powered by OpenRouter",
    version="1.0.0"
)

# Static and template mounts
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct").strip()
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


# Schemas
class MessageHistoryItem(BaseModel):
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str = Field(..., min_length=1, max_length=2000)

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=3000, description="The user's medical inquiry")
    history: Optional[List[MessageHistoryItem]] = Field(default=[], description="Recent conversation turns")

class ChatResponse(BaseModel):
    success: bool
    response: str
    model: str
    timestamp: str


@app.get("/", response_class=HTMLResponse)
async def serve_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health_check():
    has_api_key = bool(OPENROUTER_API_KEY and OPENROUTER_API_KEY != "your_openrouter_api_key_here")
    return {
        "status": "healthy",
        "service": "ChatCure Medical AI (FastAPI)",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model": OPENROUTER_MODEL,
        "api_configured": has_api_key
    }


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest):
    user_message = payload.message.strip()
    timestamp = datetime.now(timezone.utc).isoformat()

    # Guardrail Check
    if is_non_medical_query(user_message):
        return ChatResponse(
            success=True,
            response=get_domain_refusal_message(),
            model="chatcure-guardrail",
            timestamp=timestamp
        )

    # API Key check
    has_valid_key = bool(
        OPENROUTER_API_KEY
        and OPENROUTER_API_KEY != "your_openrouter_api_key_here"
        and not OPENROUTER_API_KEY.startswith("sk-placeholder")
    )

    if not has_valid_key:
        demo_reply = get_demo_response(user_message)
        return ChatResponse(
            success=True,
            response=demo_reply,
            model="chatcure-demo-engine",
            timestamp=timestamp
        )

    # Prepare OpenRouter payload
    history_messages = [{"role": h.role, "content": h.content} for h in (payload.history or [])[-8:]]
    messages = [{"role": "system", "content": MEDICAL_SYSTEM_PROMPT}] + history_messages + [{"role": "user", "content": user_message}]

    api_payload = {
        "model": OPENROUTER_MODEL,
        "messages": messages,
        "temperature": 0.4,
        "max_tokens": 1200,
        "top_p": 0.9,
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://chatcure.ai",
        "X-Title": "ChatCure AI Medical Assistant",
    }

    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post(OPENROUTER_URL, json=api_payload, headers=headers)

        if response.status_code == 200:
            result = response.json()
            choices = result.get("choices", [])
            ai_text = choices[0].get("message", {}).get("content", "").strip() if choices else ""
            if not ai_text:
                ai_text = "Empty response received. Please try rephrasing your medical question."
            return ChatResponse(
                success=True,
                response=ai_text,
                model=result.get("model", OPENROUTER_MODEL),
                timestamp=timestamp
            )
        elif response.status_code == 401:
            raise HTTPException(status_code=401, detail="Invalid OpenRouter API Key.")
        elif response.status_code == 429:
            raise HTTPException(status_code=429, detail="Rate limit exceeded on OpenRouter.")
        else:
            raise HTTPException(status_code=502, detail=f"OpenRouter upstream error ({response.status_code}).")

    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Medical consultation request timed out.")
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(f"Unexpected error: {exc}")
        raise HTTPException(status_code=500, detail="An internal server error occurred.")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("FASTAPI_PORT", 8000))
    host = os.getenv("HOST", "127.0.0.1")
    uvicorn.run("fastapi_app:app", host=host, port=port, reload=True)
