"""
AI Safety and Alignment Guardrails for Claude API calls.

This module provides preventative safety measures including:
- Input sanitization
- Output validation
- Content safety checks
- Response format validation
"""

import re
import json
import logging

# Set up logging for audit trail
logger = logging.getLogger(__name__)

# Maximum lengths for inputs
MAX_USER_MESSAGE_LENGTH = 2000
MAX_FIELD_VALUE = 1_000_000  # Max dollar amount

# Patterns that should never appear in outputs
HARMFUL_PATTERNS = [
    r'\b(kill|suicide|self-harm|hurt yourself)\b',
    r'\b(illegal|fraud|scam|steal)\b',
    r'\b(guaranteed returns|get rich quick|insider)\b',
]

# Financial advice boundaries - topics we should NOT give advice on
RESTRICTED_TOPICS = [
    'investment',
    'stock',
    'crypto',
    'bitcoin',
    'tax',
    'legal',
    'lawsuit',
    'bankruptcy',
]


class ClaudeSafetyGuard:
    """Safety guardrails for Claude API interactions."""

    @staticmethod
    def sanitize_user_input(message: str) -> str:
        """
        Sanitize user input before sending to Claude.

        - Truncates overly long messages
        - Removes potential injection attempts
        - Strips dangerous characters
        """
        if not message:
            return ""

        # Truncate to max length
        if len(message) > MAX_USER_MESSAGE_LENGTH:
            message = message[:MAX_USER_MESSAGE_LENGTH] + "..."
            logger.warning(f"User message truncated from {len(message)} chars")

        # Remove potential prompt injection patterns
        injection_patterns = [
            r'ignore previous instructions',
            r'disregard all prior',
            r'forget everything',
            r'you are now',
            r'new instructions:',
            r'system prompt:',
        ]

        for pattern in injection_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                logger.warning(f"Potential prompt injection detected: {pattern}")
                message = re.sub(pattern, '[removed]', message, flags=re.IGNORECASE)

        return message.strip()

    @staticmethod
    def validate_financial_data(data: dict) -> tuple[bool, str]:
        """
        Validate financial input data is within reasonable bounds.

        Returns (is_valid, error_message)
        """
        numeric_fields = [
            'monthly_income', 'financial_aid', 'tuition', 'housing', 'food',
            'transportation', 'books_supplies', 'entertainment', 'personal_care',
            'technology', 'health_wellness', 'miscellaneous'
        ]

        for field in numeric_fields:
            if field in data:
                value = data[field]
                if not isinstance(value, (int, float)):
                    return False, f"{field} must be a number"
                if value < 0:
                    return False, f"{field} cannot be negative"
                if value > MAX_FIELD_VALUE:
                    return False, f"{field} exceeds maximum allowed value"

        # Validate age
        if 'age' in data:
            age = data['age']
            if not isinstance(age, int) or age < 16 or age > 100:
                return False, "Age must be between 16 and 100"

        return True, ""

    @staticmethod
    def check_output_safety(response_text: str) -> tuple[bool, str]:
        """
        Check Claude's output for harmful content.

        Returns (is_safe, warning_message)
        """
        response_lower = response_text.lower()

        # Check for harmful patterns
        for pattern in HARMFUL_PATTERNS:
            if re.search(pattern, response_lower):
                logger.warning(f"Harmful pattern detected in output: {pattern}")
                return False, f"Response contained potentially harmful content"

        # Check for restricted financial advice topics
        for topic in RESTRICTED_TOPICS:
            # Only flag if it looks like advice, not just mentioning
            advice_patterns = [
                f"you should.*{topic}",
                f"i recommend.*{topic}",
                f"invest in.*{topic}",
                f"buy.*{topic}",
            ]
            for pattern in advice_patterns:
                if re.search(pattern, response_lower):
                    logger.warning(f"Restricted financial advice detected: {topic}")
                    return False, f"Response contained advice on restricted topic: {topic}"

        return True, ""

    @staticmethod
    def validate_json_response(response_text: str, required_fields: list[str]) -> tuple[bool, dict | None, str]:
        """
        Validate that Claude's response is valid JSON with required fields.

        Returns (is_valid, parsed_data, error_message)
        """
        # Handle markdown code blocks
        text = response_text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.strip()

        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response: {e}")
            return False, None, f"Invalid JSON: {str(e)}"

        # Check required fields
        missing = [f for f in required_fields if f not in parsed]
        if missing:
            logger.error(f"Missing required fields: {missing}")
            return False, None, f"Missing fields: {', '.join(missing)}"

        return True, parsed, ""

    @staticmethod
    def add_safety_context(prompt: str) -> str:
        """
        Add safety reminders to the prompt.
        """
        safety_footer = """

            SAFETY REMINDERS:
            - Never provide specific investment, tax, or legal advice
            - Do not make claims about guaranteed outcomes
            - Keep tone supportive and non-judgmental
            - If unsure, err on the side of caution
            - Focus only on general budgeting awareness and financial literacy"""

        return prompt + safety_footer

    @staticmethod
    def log_interaction(service_name: str, input_summary: str, output_summary: str, success: bool):
        """
        Log Claude API interactions for audit trail.
        """
        status = "SUCCESS" if success else "FAILURE"
        logger.info(f"[{service_name}] {status} - Input: {input_summary[:100]}... Output: {output_summary[:100]}...")


# Singleton instance for easy import
safety_guard = ClaudeSafetyGuard()
