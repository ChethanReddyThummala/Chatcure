"""
Unit Tests for ChatCure AI Medical Service
==========================================
Verifies domain guardrails, demo response generation, input validation,
and system prompt requirements without external network or server dependencies.
"""

import unittest
from medical_service import (
    is_non_medical_query,
    get_demo_response,
    get_domain_refusal_message,
    validate_chat_input,
    MEDICAL_SYSTEM_PROMPT
)


class TestChatCureMedicalLogic(unittest.TestCase):

    def test_non_medical_queries_detected(self):
        """Verify that non-medical queries are flagged by domain guardrails."""
        non_medical_queries = [
            "Write python code for a binary search tree",
            "Can you debug code in javascript for me?",
            "What is the stock price of Tesla today?",
            "How do I invest in stocks on wall street?",
            "How to change transmission fluid in my car engine?",
            "Who won the super bowl last year?",
            "Write a poem about outer space and aliens",
            "What is the capital of france?"
        ]
        for query in non_medical_queries:
            with self.subTest(query=query):
                self.assertTrue(
                    is_non_medical_query(query),
                    f"Expected '{query}' to be flagged as non-medical."
                )

    def test_medical_queries_allowed(self):
        """Verify that legitimate medical and health inquiries are NOT blocked."""
        medical_queries = [
            "What are the symptoms of seasonal allergies?",
            "How does ibuprofen compare to acetaminophen?",
            "What are normal blood pressure ranges?",
            "What first aid should I use for a minor burn?",
            "Why do I get frequent tension headaches?",
            "What is the difference between Type 1 and Type 2 diabetes?",
            "Is it safe to exercise with mild asthma?",
            "What does an elevated white blood cell count indicate?",
            "How does the immune system produce antibodies?"
        ]
        for query in medical_queries:
            with self.subTest(query=query):
                self.assertFalse(
                    is_non_medical_query(query),
                    f"Expected '{query}' to be accepted as a medical inquiry."
                )

    def test_demo_response_allergy(self):
        """Verify demo response returns relevant clinical information."""
        response = get_demo_response("Explain seasonal allergies")
        self.assertIn("Seasonal Allergies", response)
        self.assertIn("Antihistamines", response)
        self.assertIn("Disclaimer", response)

    def test_demo_response_ibuprofen(self):
        """Verify demo response for medication questions."""
        response = get_demo_response("Difference between ibuprofen and acetaminophen")
        self.assertIn("Ibuprofen", response)
        self.assertIn("Acetaminophen", response)
        self.assertIn("NSAID", response)

    def test_demo_response_general(self):
        """Verify generic demo response provides setup instructions."""
        response = get_demo_response("Tell me about cardiac arrhythmias")
        self.assertIn("ChatCure Clinical AI Assistant", response)
        self.assertIn("OPENROUTER_API_KEY", response)

    def test_domain_refusal_message(self):
        """Verify polite refusal message mentions medical domain."""
        refusal = get_domain_refusal_message()
        self.assertIn("Dr. ChatCure AI", refusal)
        self.assertIn("Medical Domain Specialty Notice", refusal)
        self.assertIn("symptom", refusal.lower())

    def test_input_validation(self):
        """Verify input validation handles various payloads."""
        # Valid payload
        valid, msg, err, hist = validate_chat_input({"message": "What is hypertension?"})
        self.assertTrue(valid)
        self.assertEqual(msg, "What is hypertension?")
        self.assertIsNone(err)

        # Empty payload
        valid, msg, err, hist = validate_chat_input({"message": "   "})
        self.assertFalse(valid)
        self.assertIn("empty", err.lower())

        # Non-dict payload
        valid, msg, err, hist = validate_chat_input(["not a dict"])
        self.assertFalse(valid)

        # Excessive length
        valid, msg, err, hist = validate_chat_input({"message": "a" * 3500})
        self.assertFalse(valid)
        self.assertIn("exceeds", err.lower())

    def test_system_prompt_contains_safety_rules(self):
        """Verify system prompt contains essential clinical guidelines."""
        self.assertIn("Dr. ChatCure AI", MEDICAL_SYSTEM_PROMPT)
        self.assertIn("STRICT DOMAIN BOUNDARY", MEDICAL_SYSTEM_PROMPT)
        self.assertIn("EMERGENCY TRIAGE", MEDICAL_SYSTEM_PROMPT)
        self.assertIn("MEDICAL DISCLAIMER", MEDICAL_SYSTEM_PROMPT)


    def test_medical_context_override(self):
        """Ensure queries mentioning vehicles or other concepts in a medical trauma context are NOT blocked."""
        trauma_queries = [
            "I had a car accident and have severe chest pain and bleeding",
            "My friend fell off a car and has a head injury",
            "I feel pain in my foot after changing a car tire"
        ]
        for query in trauma_queries:
            with self.subTest(query=query):
                self.assertFalse(
                    is_non_medical_query(query),
                    f"Expected trauma query '{query}' to be allowed."
                )

    def test_history_length_enforcement(self):
        """Verify that conversation history is truncated to at most 8 items."""
        large_history = [{"role": "user" if i % 2 == 0 else "assistant", "content": f"msg {i}"} for i in range(20)]
        valid, msg, err, hist = validate_chat_input({"message": "test", "history": large_history})
        self.assertTrue(valid)
        self.assertEqual(len(hist), 8)
        self.assertEqual(hist[-1]["content"], "msg 19")


if __name__ == "__main__":
    unittest.main()
