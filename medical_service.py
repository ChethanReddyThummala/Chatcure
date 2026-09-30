"""
ChatCure AI - Medical Intelligence & Clinical Domain Service
=============================================================
Modular clinical logic engine containing domain guardrails,
prompt engineering, emergency triage detection, and demo fallbacks.
"""

import re
from typing import Dict, List, Tuple, Optional, Any

# ---------------------------------------------------------------------------
# Medical Expert System Prompt
# ---------------------------------------------------------------------------
MEDICAL_SYSTEM_PROMPT = """You are Dr. ChatCure AI, a compassionate, highly knowledgeable, and board-certified medical AI health advisor.

YOUR CORE OBJECTIVE:
Provide accurate, evidence-based, empathetic, and beginner-friendly information about human health, medicine, biology, wellness, pharmacology, anatomy, first aid, pathology, and healthcare procedures.

STRICT DOMAIN BOUNDARY (CRITICAL RULE):
- You ONLY answer questions related to medicine, human health, diseases, symptoms, anatomy, pharmacology, wellness, lifestyle medicine, clinical tests, first aid, and healthcare systems.
- If a user asks ANY question outside this domain (e.g., coding, mathematics, politics, history, vehicle repair, video games, pop culture, cryptocurrency, financial advice, or general chat unrelated to health), you MUST politely refuse.
- Example polite refusal:
  "I am Dr. ChatCure AI, a dedicated medical and healthcare assistant. I specialize exclusively in health and medical topics. I cannot assist with [topic], but I would be glad to help you with any questions regarding symptoms, medications, healthy lifestyle choices, or medical terms."

SAFETY & EMERGENCY PROTOCOLS:
1. EMERGENCY TRIAGE: If the user describes symptoms of an acute emergency (e.g., severe crushing chest pain, difficulty breathing, sudden slurred speech, facial drooping, uncontrollable bleeding, suicidal thoughts, or acute poisoning), immediately begin your response with a bold Emergency Alert warning them to dial their local emergency services (911 in US/Canada, 112 in Europe/India, 999 in UK) or visit the nearest emergency room.
2. MEDICAL DISCLAIMER: Always emphasize that your guidance is educational and does not constitute a definitive medical diagnosis, prescription, or direct clinical relationship. Advise consulting a licensed healthcare provider for personal medical decisions.
3. FORMATTING: Use structured markdown with clear headings, bullet points for readability, bold key terms, and concise paragraphs so patients and beginners can digest the information comfortably.
"""

# ---------------------------------------------------------------------------
# Offline Demonstration Knowledge Base
# ---------------------------------------------------------------------------
DEMO_RESPONSES = {
    "allergy": (
        "### 🌿 Understanding Seasonal Allergies (Allergic Rhinitis)\n\n"
        "Seasonal allergies occur when your immune system overreacts to airborne environmental allergens such as tree, grass, or weed pollen.\n\n"
        "**Common Symptoms:**\n"
        "- Sneezing and itchy, runny, or congested nose\n"
        "- Watery, itchy, or red eyes (allergic conjunctivitis)\n"
        "- Postnasal drip leading to mild throat tickle or coughing\n"
        "- Mild daytime fatigue from disturbed sleep\n\n"
        "**Management & Relief Options:**\n"
        "1. **Non-Drowsy Antihistamines:** Cetirizine, Loratadine, or Fexofenadine help control histamine reactions.\n"
        "2. **Nasal Corticosteroid Sprays:** Fluticasone or Triamcinolone reduce nasal inflammation.\n"
        "3. **Saline Nasal Rinses:** Clear pollen residues from nasal passages.\n"
        "4. **Environmental Measures:** Keep windows closed during high pollen counts and shower before bed.\n\n"
        "⚠️ *Disclaimer: If you experience wheezing, shortness of breath, or facial swelling, consult a doctor immediately.*"
    ),
    "ibuprofen": (
        "### 💊 Ibuprofen vs. Acetaminophen (Paracetamol)\n\n"
        "Both medications relieve pain and reduce fever, but they work through distinct biochemical mechanisms in your body.\n\n"
        "**1. Ibuprofen (NSAID):**\n"
        "- **Mechanism:** Non-Steroidal Anti-Inflammatory Drug that blocks COX-1 and COX-2 enzymes.\n"
        "- **Best For:** Inflammatory pain such as arthritis, muscle sprains, menstrual cramps, toothaches, and joint swelling.\n"
        "- **Precautions:** Take with food or milk to protect your stomach lining. Avoid if you have active stomach ulcers, severe kidney disease, or are on blood thinners.\n\n"
        "**2. Acetaminophen / Paracetamol (Analgesic & Antipyretic):**\n"
        "- **Mechanism:** Works primarily in the central nervous system to inhibit pain signals.\n"
        "- **Best For:** Headaches, general fevers, sore throats, and aches without significant inflammation.\n"
        "- **Precautions:** Metabolized by the liver. Never exceed 3,000–4,000 mg in 24 hours to prevent hepatotoxicity. Avoid alcohol.\n\n"
        "⚠️ *Always check package directions and consult a physician or pharmacist before combining medications.*"
    ),
    "blood pressure": (
        "### 🫀 Understanding Healthy Blood Pressure Management\n\n"
        "Blood pressure is measured in millimeters of mercury (mmHg) and represented as **Systolic** (pressure when the heart beats) over **Diastolic** (pressure when the heart rests between beats).\n\n"
        "**Clinical Blood Pressure Categories (AHA Guidelines):**\n"
        "- **Normal:** Less than 120 / 80 mmHg\n"
        "- **Elevated:** 120–129 / <80 mmHg\n"
        "- **Hypertension Stage 1:** 130–139 or 80–89 mmHg\n"
        "- **Hypertension Stage 2:** 140+ or 90+ mmHg\n"
        "- **Hypertensive Crisis:** Higher than 180 and/or higher than 120 mmHg (Requires immediate emergency care!)\n\n"
        "**Evidence-Based Lifestyle Strategies:**\n"
        "- **DASH Diet:** Focus on leafy vegetables, fruits, whole grains, and lean proteins while restricting sodium to <2,300 mg/day.\n"
        "- **Regular Aerobic Activity:** 150 minutes of moderate exercise (brisk walking, cycling) per week.\n"
        "- **Stress Reduction:** Deep diaphragmatic breathing, adequate sleep (7–9 hours), and mindfulness meditation.\n"
        "- **Hydration & Moderation:** Limit alcohol consumption and completely avoid tobacco."
    ),
    "burn": (
        "### 🩹 First Aid for Minor (First-Degree) Thermal Burns\n\n"
        "Minor burns affect only the outer layer of skin (epidermis), causing redness, mild swelling, and localized pain without open blisters.\n\n"
        "**Immediate First Aid Steps:**\n"
        "1. **Cool the Burn Immediately:** Hold the affected area under cool, gently running tap water for 10 to 15 minutes. *Never use ice or ice water, as extreme cold damages delicate burned tissue.*\n"
        "2. **Remove Tight Items:** Gently remove rings or tight clothing before swelling occurs.\n"
        "3. **Moisturize & Protect:** Apply pure aloe vera gel or a thin layer of petroleum jelly. *Avoid butter, grease, or toothpaste, which trap heat and cause infection.*\n"
        "4. **Cover Loosely:** Apply a sterile, non-stick gauze bandage.\n"
        "5. **Over-The-Counter Pain Relief:** Acetaminophen or Ibuprofen can assist with discomfort.\n\n"
        "🚨 **Seek Emergency Medical Attention If:** The burn is larger than 3 inches, located on the face, hands, feet, groin, or major joints, or if white, charred skin appears (third-degree burn)."
    ),
    "headache": (
        "### 🧠 Causes & Classification of Headaches\n\n"
        "Headaches are among the most common neurological symptoms and are generally classified into primary and secondary categories:\n\n"
        "**Common Primary Headaches:**\n"
        "- **Tension Headaches:** Felt as a dull, aching band of tightness around the forehead, scalp, or back of the neck. Often triggered by stress, eye strain, or poor posture.\n"
        "- **Migraines:** Characterized by throbbing, unilateral pain, frequently accompanied by sensitivity to light/sound, nausea, and visual auras.\n"
        "- **Cluster Headaches:** Severe, piercing pain around one eye occurring in cycles or clusters, often with nasal congestion or eye tearing.\n\n"
        "**Symptom Relief:**\n"
        "- Rest in a quiet, dark room with a cool or warm compress.\n"
        "- Maintain optimal hydration (dehydration is a frequent headache trigger).\n"
        "- OTC analgesics used prudently under medical direction.\n\n"
        "🚨 **Red Flag Warning (Seek Immediate Care):** Sudden 'thunderclap' headache reaching maximum intensity in seconds, stiff neck with high fever, confusion, seizure, or headache following a head injury."
    ),
    "diabetes": (
        "### 🧬 Type 1 vs. Type 2 Diabetes: Clinical Differences\n\n"
        "Diabetes mellitus is a metabolic disorder characterized by elevated levels of blood glucose.\n\n"
        "**Type 1 Diabetes:**\n"
        "- **Etiology:** Autoimmune destruction of pancreatic beta cells that produce insulin.\n"
        "- **Onset:** Usually diagnosed in children, teens, and young adults, though it can occur at any age.\n"
        "- **Treatment:** Requires lifelong daily exogenous insulin therapy (injections or insulin pump) and continuous glucose monitoring.\n\n"
        "**Type 2 Diabetes:**\n"
        "- **Etiology:** Progressive insulin resistance paired with relative insulin deficiency.\n"
        "- **Onset:** Most common in adults, strongly linked with genetics, weight, and sedentary lifestyle.\n"
        "- **Treatment:** Lifestyle interventions (dietary changes, exercise), oral medications (like Metformin), GLP-1 receptor agonists, and insulin when needed.\n\n"
        "⚠️ *Regular HbA1c testing and comprehensive physician follow-up are critical for long-term health.*"
    )
}


def is_non_medical_query(text: str) -> bool:
    """
    Lightweight heuristic filter to detect blatantly non-medical topics
    and enforce strict domain boundaries.
    """
    text_lower = text.lower().strip()
    
    unrelated_patterns = [
        r"\b(python|javascript|c\+\+|html|css|sql|write code|debug code|algorithm|leetcode)\b",
        r"\b(stock price|bitcoin|cryptocurrency|forex|invest in stocks|wall street)\b",
        r"\b(car engine|transmission fluid|oil change|brake pads|tire pressure)\b",
        r"\b(who won the|fifa|super bowl|ipl|cricket score|nba finals)\b",
        r"\b(write a poem about|write a story about aliens|lyrics for a song)\b",
        r"\b(capital of france|who is the president of|tallest mountain in)\b"
    ]
    
    for pattern in unrelated_patterns:
        if re.search(pattern, text_lower):
            # Check for overlapping medical terms that may be legitimate
            medical_context = [
                "pain", "health", "doctor", "medicine", "pill", "symptom", 
                "disease", "treatment", "injury", "bleeding", "wound", 
                "hospital", "patient", "clinic", "fever", "infection", 
                "emergency", "accident", "trauma", "breath", "heart"
            ]
            if not any(med in text_lower for med in medical_context):
                return True
                
    return False


def get_domain_refusal_message() -> str:
    """
    Standard polite refusal when user inquires about out-of-domain topics.
    """
    return (
        "### ⚕️ Medical Domain Specialty Notice\n\n"
        "I am **Dr. ChatCure AI**, a specialized medical and health assistant. "
        "I focus exclusively on human health, medical conditions, symptoms, medications, "
        "wellness, and anatomy.\n\n"
        "Your question appears to be outside the medical domain. "
        "Please ask a health-related question, such as:\n"
        "- Inquiring about a symptom or clinical sign\n"
        "- Learning about medication uses, dosages, and interactions\n"
        "- Seeking lifestyle and nutritional wellness advice\n"
        "- Understanding medical terminology or lab test results\n\n"
        "How can I assist your health or wellness today?"
    )


# Keyword aliases mapped to demo responses
DEMO_KEYWORD_MAP = {
    ("allerg", "pollen", "hay fever", "rhinitis"): DEMO_RESPONSES["allergy"],
    ("ibuprofen", "acetaminophen", "paracetamol", "advil", "tylenol", "nsaid"): DEMO_RESPONSES["ibuprofen"],
    ("blood pressure", "hypertension", "systolic", "diastolic", "bp"): DEMO_RESPONSES["blood pressure"],
    ("burn", "scald", "blister from heat"): DEMO_RESPONSES["burn"],
    ("headache", "migraine", "head pain"): DEMO_RESPONSES["headache"],
    ("diabet", "blood sugar", "glucose", "insulin", "hba1c"): DEMO_RESPONSES["diabetes"],
}


def get_demo_response(query: str) -> str:
    """
    Generate an intelligent medical fallback response when no live API key is present.
    """
    q = query.lower()
    for keywords, response in DEMO_KEYWORD_MAP.items():
        if any(kw in q for kw in keywords):
            return (
                f"{response}\n\n"
                "---\n"
                "*💡 [Demo Mode Notice]: Running offline medical preview. "
                "To unlock live OpenRouter AI reasoning for all inquiries, "
                "insert your `OPENROUTER_API_KEY` into the `.env` file.*"
            )

    return (
        "### 🩺 ChatCure Clinical AI Assistant (Demo Mode)\n\n"
        f"Thank you for your inquiry: **\"{query}\"**.\n\n"
        "**Clinical Guidance:**\n"
        "- For detailed symptom reviews, pharmacology, and medical diagnoses, "
        "ChatCure AI connects directly to OpenRouter's advanced clinical language models.\n"
        "- Currently, no live API key has been detected in your `.env` configuration file.\n\n"
        "**How to Enable Full Live AI Responses:**\n"
        "1. Open the project's `.env` file.\n"
        "2. Add your OpenRouter API key: `OPENROUTER_API_KEY=sk-or-v1-...`\n"
        "3. Restart the server (`python app.py`).\n\n"
        "**Try these preloaded medical topics in demo mode:**\n"
        "- *'Explain seasonal allergies'* 🌿\n"
        "- *'Difference between ibuprofen and acetaminophen'* 💊\n"
        "- *'How to manage high blood pressure'* 🫀\n"
        "- *'First aid for minor burns'* 🩹\n"
        "- *'Causes of headaches'* 🧠\n"
        "- *'Type 1 vs Type 2 diabetes'* 🧬\n\n"
        "⚠️ *Medical Disclaimer: Informational guidance only. Consult a licensed physician for professional medical care.*"
    )


def validate_chat_input(data: Any) -> Tuple[bool, Optional[str], Optional[str], List[Dict[str, str]]]:
    """
    Validates the incoming JSON request payload.
    Returns: (is_valid, user_message, error_message, validated_history)
    """
    if not isinstance(data, dict):
        return False, None, "Request body must be a valid JSON object.", []

    user_message = data.get("message", "")
    if not isinstance(user_message, str):
        return False, None, "The 'message' field must be a string.", []

    user_message = user_message.strip()
    if not user_message:
        return False, None, "Message cannot be empty or whitespace only.", []

    if len(user_message) > 3000:
        return False, None, "Message exceeds maximum permitted length of 3000 characters.", []

    history = data.get("history", [])
    valid_history: List[Dict[str, str]] = []
    if isinstance(history, list):
        for item in history:
            if isinstance(item, dict) and "role" in item and "content" in item:
                if item["role"] in ("user", "assistant") and isinstance(item["content"], str):
                    valid_history.append({
                        "role": item["role"],
                        "content": item["content"][:2000]
                    })
    valid_history = valid_history[-8:]

    return True, user_message, None, valid_history
