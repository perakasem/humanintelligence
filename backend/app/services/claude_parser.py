import json
import anthropic
from ..schemas.intake import RawAnswer, SnapshotData
from ..models.user import User
from ..config import get_settings

settings = get_settings()


class ClaudeParserService:
    """
    Service for parsing conversational form answers into structured ML input.
    Uses Claude to understand and extract structured data from natural language.
    """

    def __init__(self):
        self.api_key = settings.anthropic_api_key
        self.client = anthropic.Anthropic(api_key=self.api_key) if self.api_key else None

    async def parse(self, raw_answers: list[RawAnswer], user: User | None = None) -> SnapshotData:
        """
        Parse raw conversational answers into structured snapshot data.
        Uses Claude API for intelligent parsing.
        """

        if not (self.client and self.api_key):
            raise RuntimeError("ClaudeParserService is not configured: missing API key or client.")

        parsed = self._parse_with_claude(raw_answers)

        if parsed is None:
            raise ValueError("Failed to parse answers with Claude.")

        # If user has profile, override parsed fields
        if user and user.has_profile:
            parsed["age"] = user.age
            parsed["gender"] = user.gender
            parsed["year_in_school"] = user.year_in_school
            parsed["major"] = user.major
            parsed["preferred_payment_method"] = user.preferred_payment_method

        # If this is initial onboarding, save profile fields to user
        if user and not user.has_profile:
            user.age = parsed["age"]
            user.gender = parsed["gender"]
            user.year_in_school = parsed["year_in_school"]
            user.major = parsed["major"]
            user.preferred_payment_method = parsed["preferred_payment_method"]

        try:
            return SnapshotData(**parsed)
        except Exception as e:
            raise ValueError(
                f"Validation failed: {str(e)}. "
                f"Parsed data: {json.dumps(parsed, indent=2)}"
            )

    def _parse_with_claude(self, raw_answers: list[RawAnswer]) -> dict:
        """Use Claude to parse raw answers into structured data."""
        # Format the answers for Claude
        answers_text = "\n".join([
            f"- {a.question_id}: {a.answer}" for a in raw_answers
        ])

        prompt = f"""Parse the following survey answers into structured financial data. Extract the values and convert them to the specified formats.

                    Survey Answers:
                    {answers_text}
                    
                    Return a JSON object with these exact fields (use the integer codes specified):
                    
                    - age: integer (16-100)
                    - gender: integer (0=Male, 1=Female, 2=Non-binary, 3=Prefer not to say)
                    - year_in_school: integer (0=Freshman, 1=Sophomore, 2=Junior, 3=Senior, 4=Graduate)
                    - major: integer - Map the field of study to one of these categories:
                      0=STEM (includes CS, computer science, engineering, math, physics, chemistry, biology, data science, etc.)
                      1=Business (includes finance, accounting, marketing, economics, MBA, etc.)
                      2=Humanities (includes english, history, philosophy, languages, literature, etc.)
                      3=Social Sciences (includes psychology, sociology, political science, anthropology, etc.)
                      4=Arts (includes art, music, theater, design, film, etc.)
                      5=Health Sciences (includes nursing, pre-med, public health, kinesiology, etc.)
                      6=Education
                      7=Law/Pre-Law
                      8=Other
                    - monthly_income: integer in dollars (extract number, default 0)
                    - financial_aid: integer in dollars (extract number, default 0)
                    - tuition: integer in dollars (extract number, default 0)
                    - housing: integer in dollars (extract number, default 0)
                    - food: integer in dollars (extract number, default 0)
                    - transportation: integer in dollars (extract number, default 0)
                    - books_supplies: integer in dollars (extract number, default 0)
                    - entertainment: integer in dollars (extract number, default 0)
                    - personal_care: integer in dollars (extract number, default 0)
                    - technology: integer in dollars (extract number, default 0)
                    - health_wellness: integer in dollars (extract number, default 0)
                    - miscellaneous: integer in dollars (extract number, default 0)
                    - preferred_payment_method: integer (0=Cash, 1=Credit Card, 2=Debit Card, 3=Mobile Payment)
                    
                    Important:
                    - For major, understand common abbreviations: "CS" = Computer Science = STEM (0), "econ" = Economics = Business 
                    (1), "psych" = Psychology = Social Sciences (3), etc.
                    - Extract just the numeric value from money amounts (e.g., "$500" -> 500, "about 300" -> 300)
                    - If a value is unclear or missing, use reasonable defaults
                    
                    Return ONLY the JSON object, no other text or markdown."""

        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Extract JSON from response
        response_text = message.content[0].text.strip()

        # Try to parse as JSON
        try:
            # Handle case where response might have markdown code blocks
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
                response_text = response_text.strip()

            parsed = json.loads(response_text)
            return parsed
        except json.JSONDecodeError as e:
            print(f"Failed to parse Claude response as JSON: {e}")
            print(f"Response was: {response_text}")
            raise ValueError("Claude response was not valid JSON.")

    def _extract_number(self, text: str, default: int) -> int:
        """Extract a number from text."""
        import re
        numbers = re.findall(r'\d+', text.replace(',', ''))
        if numbers:
            return int(numbers[0])
        return default

    def _extract_gender(self, text: str) -> int:
        """Extract gender encoding."""
        if "female" in text or "woman" in text:
            return 1
        elif "non-binary" in text or "nonbinary" in text:
            return 2
        elif "prefer not" in text:
            return 3
        return 0  # male/man default

    def _extract_year(self, text: str) -> int:
        """Extract year in school encoding."""
        if "fresh" in text or "first" in text:
            return 0
        elif "soph" in text or "second" in text:
            return 1
        elif "junior" in text or "third" in text:
            return 2
        elif "senior" in text or "fourth" in text:
            return 3
        elif "grad" in text or "master" in text or "phd" in text:
            return 4
        return 1  # default sophomore

    def _extract_major(self, text: str) -> int:
        """Extract major category encoding."""
        if any(w in text for w in ["stem", "science", "engineering", "computer", "math", "physics"]):
            return 0
        elif any(w in text for w in ["business", "finance", "accounting", "marketing"]):
            return 1
        elif any(w in text for w in ["humanities", "english", "history", "philosophy"]):
            return 2
        elif any(w in text for w in ["social", "psychology", "sociology", "political"]):
            return 3
        elif any(w in text for w in ["art", "music", "theater", "design"]):
            return 4
        elif any(w in text for w in ["health", "nursing", "medical", "pre-med"]):
            return 5
        elif any(w in text for w in ["education", "teaching"]):
            return 6
        elif any(w in text for w in ["law", "legal"]):
            return 7
        return 8  # other

    def _extract_payment(self, text: str) -> int:
        """Extract payment method encoding."""
        if "cash" in text:
            return 0
        elif "credit" in text:
            return 1
        elif "debit" in text:
            return 2
        elif any(w in text for w in ["mobile", "venmo", "cash app", "apple pay"]):
            return 3
        return 2  # default debit

    def _get_parser_prompt(self) -> str:
        """Get the system prompt for the parser agent."""
        return """You are a financial data parser. Your job is to extract structured financial information from conversational answers.

                Given a list of question-answer pairs, extract the following fields as integers:
                - age (16-100)
                - gender (0=Male, 1=Female, 2=Non-binary, 3=Prefer not to say)
                - year_in_school (0=Freshman, 1=Sophomore, 2=Junior, 3=Senior, 4=Graduate)
                - major (0=STEM, 1=Business, 2=Humanities, 3=Social Sciences, 4=Arts, 5=Health Sciences, 6=Education, 7=Law, 8=Other)
                - monthly_income (total monthly income in dollars)
                - financial_aid (monthly financial aid amount)
                - tuition (monthly tuition cost)
                - housing (monthly housing cost)
                - food (monthly food spending)
                - transportation (monthly transportation cost)
                - books_supplies (monthly books and supplies cost)
                - entertainment (monthly entertainment spending)
                - personal_care (monthly personal care spending)
                - technology (monthly technology spending)
                - health_wellness (monthly health and wellness spending)
                - miscellaneous (monthly miscellaneous spending)
                - preferred_payment_method (0=Cash, 1=Credit Card, 2=Debit Card, 3=Mobile Payment)
                
                Return ONLY a valid JSON object with these fields. Make reasonable inferences when information is ambiguous."""
