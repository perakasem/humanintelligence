import json
import anthropic
from ..config import get_settings

settings = get_settings()

# Profile fields (collected once, stored in user profile)
PROFILE_FIELDS = ["age", "gender", "year_in_school", "major", "preferred_payment_method"]

# Financial fields (collected every check-in)
FINANCIAL_FIELDS = [
    "monthly_income", "financial_aid", "tuition", "housing", "food", "transportation",
    "books_supplies", "entertainment", "personal_care", "technology", "health_wellness", "miscellaneous"
]

# All required fields for the ML model
REQUIRED_FIELDS = PROFILE_FIELDS + FINANCIAL_FIELDS


class ClaudeSurveyService:
    """
    Service for generating adaptive survey questions using Claude.
    Creates a conversational flow that feels natural while collecting required data.
    """

    def __init__(self):
        self.api_key = settings.anthropic_api_key
        self.client = anthropic.Anthropic(api_key=self.api_key) if self.api_key else None

    async def generate_next_question(
        self,
        conversation_history: list[dict],
        collected_fields: list[str],
        has_profile: bool = False
    ) -> dict:
        """
        Generate the next survey question based on conversation history.

        Args:
            conversation_history: Previous messages in the conversation
            collected_fields: Fields already collected in this session
            has_profile: If True, skip profile fields (user is doing a check-in)

        Returns:
            {
                "question": str,
                "context": str (optional helper text),
                "is_complete": bool,
                "suggested_type": str (text, number, select, etc.)
            }
        """
        # Determine which fields to collect
        if has_profile:
            required = FINANCIAL_FIELDS
        else:
            required = REQUIRED_FIELDS

        missing_fields = [f for f in required if f not in collected_fields]

        if not missing_fields:
            return {
                "question": None,
                "context": None,
                "is_complete": True,
                "suggested_type": None,
                "field": None,
                "options": None,
                "progress": 1.0
            }

        # If no API key, fall back to mock questions
        if not self.client:
            return self._generate_mock_question(conversation_history, collected_fields, has_profile)

        # Generate question using Claude API
        try:
            return await self._generate_claude_question(
                conversation_history, collected_fields, missing_fields, required
            )
        except Exception as e:
            print(f"Claude API error: {e}, falling back to mock questions")
            return self._generate_mock_question(conversation_history, collected_fields, has_profile)

    async def _generate_claude_question(
        self,
        conversation_history: list[dict],
        collected_fields: list[str],
        missing_fields: list[str],
        required: list[str]
    ) -> dict:
        """Generate the next question using Claude API."""

        system_prompt = self._get_survey_prompt()

        # Build context about what's been collected
        context = f"""
Fields already collected: {', '.join(collected_fields) if collected_fields else 'None yet'}
Fields still needed: {', '.join(missing_fields)}
Next field to collect: {missing_fields[0]}

Conversation so far:
"""
        for msg in conversation_history:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            context += f"\n{role}: {content}"

        if not conversation_history:
            context += "\n(This is the start of the conversation)"

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            system=system_prompt,
            messages=[
                {"role": "user", "content": context}
            ]
        )

        # Parse the response
        response_text = response.content[0].text.strip()

        # Handle markdown code blocks
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.strip()

        try:
            result = json.loads(response_text)
            return {
                "field": result.get("field", missing_fields[0]),
                "question": result.get("question"),
                "context": result.get("context"),
                "is_complete": False,
                "suggested_type": result.get("suggested_type", "text"),
                "options": result.get("options"),
                "progress": len(collected_fields) / len(required)
            }
        except json.JSONDecodeError:
            # If parsing fails, fall back to mock
            return self._generate_mock_question(conversation_history, collected_fields, len(required) != len(REQUIRED_FIELDS))

    def _generate_mock_question(
        self,
        collected_fields: list[str],
        has_profile: bool = False
    ) -> dict:
        """Generate questions based on what's still needed."""

        # Determine which fields to collect
        if has_profile:
            # Check-in: only collect financial fields
            required = FINANCIAL_FIELDS
        else:
            # Initial onboarding: collect all fields
            required = REQUIRED_FIELDS

        missing_fields = [f for f in required if f not in collected_fields]

        if not missing_fields:
            return {
                "question": None,
                "context": None,
                "is_complete": True,
                "suggested_type": None,
                "field": None,
                "options": None,
                "progress": 1.0
            }

        # Get the next field to ask about
        next_field = missing_fields[0]

        # Generate conversational questions based on field
        questions = {
            "age": {
                "question": "Let's start with the basics! How old are you?",
                "context": "This helps me tailor advice to your life stage.",
                "suggested_type": "number"
            },
            "gender": {
                "question": "How do you identify?",
                "context": "This helps personalize your experience.",
                "suggested_type": "select",
                "options": ["Male", "Female", "Non-binary", "Prefer not to say"]
            },
            "year_in_school": {
                "question": "What year are you in school?",
                "context": "Different years come with different financial challenges.",
                "suggested_type": "select",
                "options": ["Freshman", "Sophomore", "Junior", "Senior", "Graduate"]
            },
            "major": {
                "question": "What are you studying?",
                "context": "Your major can affect both expenses and future income.",
                "suggested_type": "text"
            },
            "monthly_income": {
                "question": "How much money do you bring in each month?",
                "context": "Include jobs, allowances, gig work—everything that comes in regularly.",
                "suggested_type": "number"
            },
            "financial_aid": {
                "question": "Do you receive any financial aid? How much per month?",
                "context": "Include scholarships, grants, and any loan money you use for living expenses.",
                "suggested_type": "number"
            },
            "tuition": {
                "question": "What's your monthly tuition cost?",
                "context": "If you pay per semester, just divide by the number of months.",
                "suggested_type": "number"
            },
            "housing": {
                "question": "How much do you spend on housing each month?",
                "context": "Include rent, utilities, internet—the whole package.",
                "suggested_type": "number"
            },
            "food": {
                "question": "What about food? How much do you typically spend monthly?",
                "context": "Groceries, meal plans, dining out, coffee runs—all of it counts!",
                "suggested_type": "number"
            },
            "transportation": {
                "question": "How much do you spend getting around?",
                "context": "Gas, public transit, rideshares, bike maintenance—whatever you use.",
                "suggested_type": "number"
            },
            "books_supplies": {
                "question": "What do books and supplies cost you monthly?",
                "context": "Textbooks, lab materials, school supplies. If it varies, give me an average.",
                "suggested_type": "number"
            },
            "entertainment": {
                "question": "Now for the fun stuff—how much goes to entertainment?",
                "context": "Streaming, games, concerts, nights out with friends.",
                "suggested_type": "number"
            },
            "personal_care": {
                "question": "What about personal care and self-maintenance?",
                "context": "Haircuts, skincare, gym, clothes—taking care of yourself.",
                "suggested_type": "number"
            },
            "technology": {
                "question": "Any regular technology expenses?",
                "context": "Phone plan, app subscriptions, software you need.",
                "suggested_type": "number"
            },
            "health_wellness": {
                "question": "What do you spend on health and wellness?",
                "context": "Insurance, medications, therapy, doctor visits.",
                "suggested_type": "number"
            },
            "miscellaneous": {
                "question": "Anything else we haven't covered?",
                "context": "Gifts, random purchases, unexpected expenses—the stuff that doesn't fit elsewhere.",
                "suggested_type": "number"
            },
            "preferred_payment_method": {
                "question": "Last one! How do you usually pay for things?",
                "context": "This tells me a bit about your spending habits.",
                "suggested_type": "select",
                "options": ["Cash", "Credit Card", "Debit Card", "Mobile Payment (Venmo, Apple Pay, etc.)"]
            }
        }

        q = questions.get(next_field, {
            "question": f"Tell me about your {next_field.replace('_', ' ')}",
            "context": None,
            "suggested_type": "text"
        })

        return {
            "field": next_field,
            "question": q["question"],
            "context": q.get("context"),
            "is_complete": False,
            "suggested_type": q["suggested_type"],
            "options": q.get("options"),
            "progress": len(collected_fields) / len(required)
        }

    def _get_survey_prompt(self) -> str:
        """Get the system prompt for generating survey questions."""
        return """You are a friendly financial coach collecting information from a college student. Your goal is to gather their financial data through a natural, conversational flow.
                    
                    Based on the conversation so far, generate the next question to ask. Be:
                    - Warm and conversational, not robotic
                    - Brief but clear
                    - Encouraging when appropriate
                    
                    You need to collect these fields (mark which ones you've already gotten):
                    - age, gender, year_in_school, major
                    - monthly_income, financial_aid
                    - tuition, housing, food, transportation
                    - books_supplies, entertainment, personal_care
                    - technology, health_wellness, miscellaneous
                    - preferred_payment_method
                    
                    Return JSON with:
                    {
                      "field": "the_field_being_asked",
                      "question": "Your conversational question",
                      "context": "Optional helper text",
                      "suggested_type": "number|text|select",
                      "options": ["only", "for", "select", "types"]
                    }"""
