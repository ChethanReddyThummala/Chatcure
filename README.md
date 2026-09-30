# 🏥 ChatCure AI — Clinical Medical Chatbot Platform

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0+-000000?style=flat&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Alternative_Backend-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![OpenRouter](https://img.shields.io/badge/OpenRouter-AI_API-6366f1?style=flat)](https://openrouter.ai/)
[![Domain](https://img.shields.io/badge/Domain-Medical_%26_Healthcare-0284c7?style=flat)](https://chatcure.ai)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**ChatCure AI** is an intelligent, domain-specialized clinical medical chatbot web application. Built with an asynchronous Python backend (Flask & optional FastAPI) and integrated with the **OpenRouter API**, ChatCure AI provides evidence-based medical information, symptom analysis, pharmacology explanations, and wellness education.

The frontend is crafted following modern clinical design principles—featuring a crisp hospital blue-and-white theme, light/dark modes, accessible typography, typing animations, interactive quick-prompt pills, global emergency helpline directories, and strict medical guardrails.

---

## 📑 Table of Contents

- [Domain Specialization](#-domain-specialization)
- [Key Features](#-key-features)
- [Project Architecture & Folder Structure](#-project-architecture--folder-structure)
- [Prerequisites](#-prerequisites)
- [Quick Start Guide](#-quick-start-guide)
  - [1. Environment Setup](#1-environment-setup)
  - [2. Install Dependencies](#2-install-dependencies)
  - [3. Configure Environment Variables](#3-configure-environment-variables)
  - [4. Run the Application](#4-run-the-application)
- [Running with FastAPI (Alternative)](#-running-with-fastapi-alternative)
- [API Reference](#-api-reference)
- [Chatbot Behavior & Clinical Guardrails](#-chatbot-behavior--clinical-guardrails)
- [Offline Demo Mode](#-offline-demo-mode)
- [Testing](#-testing)
- [Medical Disclaimer](#-medical-disclaimer)

---

## 🩺 Domain Specialization

ChatCure AI is strictly designed and optimized for the **Medical and Healthcare Domain**:

- **Visual Theme:** Clean clinical aesthetic with hospital blues (`#0284c7`, `#0369a1`), calming teals (`#0d9488`), crisp whites, and gentle slate contrasts.
- **Iconography:** Healthcare symbols including medical crosses, stethoscopes, activity pulses, pills, and emergency triage alerts.
- **Strict Domain Boundary:** Politely rejects out-of-domain inquiries (coding, car mechanics, finance, general pop culture) and redirects the user back to health topics.
- **Emergency Triage Protocol:** Detects critical symptoms (chest pain, stroke signs, difficulty breathing, trauma, poisoning) and displays immediate emergency contact advice.

---

## ✨ Key Features

### 🖥️ Backend (Flask & OpenRouter)
- **Asynchronous Architecture (`async`/`await`):** Uses `httpx.AsyncClient` for non-blocking communication with OpenRouter's language models.
- **Secure Key Management:** Stores API keys safely in `.env` using `python-dotenv`.
- **POST `/chat` Endpoint:** High-performance JSON endpoint supporting conversation history context.
- **Input Validation & Sanitization:** Validates request shape, types, message length (max 3,000 characters), and trims history to prevent token exhaustion.
- **Modular Clinical Service (`medical_service.py`):** Separates clinical prompts, domain guardrails, and validation logic from HTTP routes.
- **Smart Fallback Demo Mode:** Provides instant, structured medical responses for common health inquiries even before an OpenRouter API key is supplied.
- **Dual Framework Support:** Primary Flask implementation in `app.py` plus an ASGI FastAPI implementation in `fastapi_app.py`.

### 🎨 Frontend (HTML, CSS, JavaScript)
- **Responsive Hospital Layout:** Pixel-perfect on mobile phones (320px+), tablets, laptops, and ultra-wide desktop monitors.
- **Sticky Glassmorphism Header:** Features the ChatCure medical badge, pulse status indicator, quick modals, and theme switcher.
- **Emergency Notification Ribbon:** Persistent banner linking directly to emergency contacts.
- **Interactive Hero Section:** Domain headline, medical disclaimer banner, and interactive suggestion chips:
  - 🌿 *Seasonal Allergies*
  - 💊 *Ibuprofen vs. Acetaminophen*
  - 🫀 *Blood Pressure Management*
  - 🩹 *Burn First Aid*
  - 🧠 *Headache Causes*
  - 🧬 *Type 1 vs Type 2 Diabetes*
- **Clinical Chat Interface:**
  - Distinct patient and AI avatars with verified medical badge.
  - Formatted Markdown rendering (headings, bullet points, warning callouts) sanitized with `DOMPurify`.
  - **Copy Response Button:** One-click copy with animated checkmark and toast confirmation.
  - **Live Typing Animation:** Smooth pulsing dots indicator while awaiting AI clinical reasoning.
  - **Loading Spinner:** Embedded inside the Send button during request execution.
  - **Human-Readable Timestamps:** E.g., `05:42 PM` displayed on each message.
  - **Auto-Scroll & Scroll-to-Bottom Button:** Automatically scrolls down and displays a floating return button when scrolled up.
  - **Keyboard Support:** Press `Enter` to send, `Shift + Enter` for multi-line input, and `Escape` to close modals.
  - **Clear Chat with Safety Dialog:** Resets conversation history and restores the welcome card.
  - **Export Conversation:** Downloads the entire medical consultation as a `.md` Markdown file.
  - **Light & Dark Theme:** Persistent theme switching via CSS variables and `localStorage`.

---

## 📁 Project Architecture & Folder Structure

```
chat-cure/
│── app.py                 # Primary Flask backend with async /chat endpoint
│── medical_service.py     # Modular clinical prompt, domain guardrails & validation
│── fastapi_app.py         # Optional FastAPI backend implementation
│── templates/
│     └── index.html       # Semantic HTML5 clinical UI
│── static/
│     ├── style.css        # Hospital-grade CSS with responsive grid and light/dark theme
│     └── script.js        # Frontend client engine (AJAX, markdown, history, modals)
│── .env                   # Environment secrets (API key & configuration)
│── .env.example           # Version-controlled configuration template
│── requirements.txt       # Essential Python dependencies
│── test_app.py            # Unit test suite verifying domain guardrails & logic
└── README.md              # Comprehensive documentation
```

---

## 📦 Prerequisites

- **Python:** 3.10 or higher
- **OpenRouter API Key:** Free or paid key from [openrouter.ai/keys](https://openrouter.ai/keys) *(optional for initial local testing due to built-in Demo Mode)*.

---

## 🚀 Quick Start Guide

### 1. Environment Setup

Open your terminal and navigate to the project directory:

```bash
cd /Users/chethanreddythummala/Documents/chat-cure
```

Create and activate a Python virtual environment:

```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows (Command Prompt)
# .venv\Scripts\activate.bat
```

### 2. Install Dependencies

Install the essential requirements:

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create or update your `.env` file (copied from `.env.example`):

```bash
cp .env.example .env
```

Edit `.env` and paste your OpenRouter API key:

```ini
# OpenRouter API Key - https://openrouter.ai/keys
OPENROUTER_API_KEY=sk-or-v1-your-actual-api-key-here

# Preferred Model (Default: Llama 3.3 70B Instruct)
OPENROUTER_MODEL=meta-llama/llama-3.3-70b-instruct

# Server Port & Host
FLASK_PORT=5000
FASTAPI_PORT=8000
HOST=127.0.0.1
DEBUG=True
```

> **Note:** If you don't have an API key yet, ChatCure AI will automatically start in **Demo Fallback Mode**, allowing you to test the full UI and common medical prompts immediately.

### 4. Run the Application

Start the Flask server:

```bash
python app.py
```

You will see:

```
=================================================================
 🏥  ChatCure AI - Medical Chatbot Platform (Flask)
 🌐  Server running at: http://127.0.0.1:5000/
 🤖  Active Model: meta-llama/llama-3.3-70b-instruct
 🔑  OpenRouter API Key: Configured ✅
=================================================================
```

Open your browser and navigate to:

👉 **[http://127.0.0.1:5000/](http://127.0.0.1:5000/)**

---

## ⚡ Running with FastAPI (Alternative)

If you prefer using **FastAPI** with ASGI performance and Pydantic validation:

```bash
# Run with Uvicorn
uvicorn fastapi_app:app --reload --port 8000
```

Open your browser at:

👉 **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

FastAPI interactive Swagger documentation is available at:
👉 **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

---

## 📡 API Reference

### `POST /chat`

Submits a medical inquiry to the AI assistant.

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "message": "What is the difference between Ibuprofen and Acetaminophen?",
  "history": [
    {
      "role": "user",
      "content": "Can I take pain relievers for headache?"
    },
    {
      "role": "assistant",
      "content": "Common OTC options include acetaminophen or NSAIDs like ibuprofen..."
    }
  ]
}
```

**Success Response (`200 OK`):**
```json
{
  "success": true,
  "response": "### 💊 Ibuprofen vs. Acetaminophen\n\nBoth medications relieve pain...",
  "model": "meta-llama/llama-3.3-70b-instruct",
  "timestamp": "2026-09-30T17:45:00.123456+00:00"
}
```

**Guardrail Interception Response (`200 OK`):**
```json
{
  "success": true,
  "response": "### ⚕️ Medical Domain Specialty Notice\n\nI am Dr. ChatCure AI...",
  "model": "chatcure-guardrail",
  "timestamp": "2026-09-30T17:45:00.123456+00:00"
}
```

**Validation Error Response (`400 Bad Request`):**
```json
{
  "success": false,
  "error": "Message cannot be empty or whitespace only."
}
```

### `GET /health`

Returns application health status and API configuration state.

**Response (`200 OK`):**
```json
{
  "status": "healthy",
  "service": "ChatCure Medical AI (Flask)",
  "timestamp": "2026-09-30T17:45:00.123456+00:00",
  "model": "meta-llama/llama-3.3-70b-instruct",
  "api_configured": true
}
```

---

## 🛡️ Chatbot Behavior & Clinical Guardrails

ChatCure AI implements multi-tiered medical boundaries:

1. **Medical Domain Exclusivity:** The system prompt strictly limits conversation to human anatomy, physiology, symptoms, pharmacology, first aid, pathology, and wellness.
2. **Polite Out-of-Domain Refusal:** Inquiries about programming, mechanics, crypto, general trivia, or sports are politely refused with a redirection to health topics.
3. **Trauma & Accident Awareness:** The guardrails distinguish between non-medical mentions (e.g., "car repair") and medical contexts (e.g., "car accident with chest injury").
4. **Emergency Escalation:** Symptoms of acute myocardial infarction (heart attack), stroke, respiratory distress, severe burns, or poisoning trigger bold emergency service alerts.
5. **No Prescriptions / Definitive Diagnosis:** Reminds users to consult licensed healthcare providers.

---

## 🧪 Testing

The repository includes a comprehensive unit test suite in `test_app.py`:

```bash
python3 test_app.py
```

Test coverage includes:
- Non-medical query detection (coding, finance, sports, vehicle mechanics)
- Legitimate medical query pass-through
- Medical trauma context override
- Demo fallback responses for allergies, ibuprofen, blood pressure, etc.
- Request payload input validation
- Conversation history truncation and limits
- Medical system prompt safety rule verification

---

## ⚠️ Medical Disclaimer

**ChatCure AI is an educational technology demonstration.**

- It **does not** provide formal medical diagnoses, clinical evaluations, or prescription services.
- It **does not** establish a physician-patient relationship.
- Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition.
- **In an emergency, immediately call 911 (US/Canada), 112 (Europe/India), 999 (UK), or your local emergency response service.**
