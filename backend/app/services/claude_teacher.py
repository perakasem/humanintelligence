import json
import logging
import anthropic
from ..schemas.teacher import TeacherOutput, LessonOutline, FieldUpdate
from ..schemas.intake import SnapshotData
from ..schemas.ml import MLOutput
from ..schemas.dashboard import Analytics
from ..config import get_settings
from .claude_safety import safety_guard

settings = get_settings()
logger = logging.getLogger(__name__)


class ClaudeTeacherService:
    """
    Service for the teacher/coach agent that provides financial advice.
    Uses Claude to generate personalized lessons and action items.
    """

    def __init__(self):
        self.api_key = settings.anthropic_api_key
        self.client = anthropic.Anthropic(api_key=self.api_key) if self.api_key else None

    async def generate_response(
        self,
        snapshot: SnapshotData,
        ml_output: MLOutput,
        analytics: Analytics,
        user_message: str,
        previous_snapshot: SnapshotData | None = None,
        previous_analytics: Analytics | None = None
    ) -> TeacherOutput:
        """
        Generate a teacher response to the user's message.
        Uses Claude API for intelligent coaching.
        """
        # Sanitize user input
        safe_message = safety_guard.sanitize_user_input(user_message)

        # Validate financial data
        input_data = snapshot.model_dump() if hasattr(snapshot, 'model_dump') else snapshot.__dict__
        is_valid, error = safety_guard.validate_financial_data(input_data)
        if not is_valid:
            logger.error(f"Invalid financial data: {error}")
            return self._generate_fallback_response(
                snapshot, ml_output, analytics, safe_message,
                previous_snapshot, previous_analytics
            )

        # Try Claude API first, fall back to minimal response if unavailable
        if self.client and self.api_key:
            try:
                result = self._respond_with_claude(
                    snapshot, ml_output, analytics, safe_message,
                    previous_snapshot, previous_analytics
                )
                safety_guard.log_interaction("teacher", safe_message[:50], result.explanation[:50], True)
                return result
            except Exception as e:
                logger.error(f"Claude teacher response failed: {e}")
                safety_guard.log_interaction("teacher", safe_message[:50], str(e), False)
                return self._generate_fallback_response(
                    snapshot, ml_output, analytics, safe_message,
                    previous_snapshot, previous_analytics
                )
        else:
            return self._generate_fallback_response(
                snapshot, ml_output, analytics, safe_message,
                previous_snapshot, previous_analytics
            )

    def _respond_with_claude(
        self,
        snapshot: SnapshotData,
        ml_output: MLOutput,
        analytics: Analytics,
        user_message: str,
        previous_snapshot: SnapshotData | None = None,
        previous_analytics: Analytics | None = None
    ) -> TeacherOutput:
        """Use Claude to generate a personalized teacher response."""
        # Prepare the context for Claude
        context = f"""Current Financial Snapshot:
                    - Age: {snapshot.age}
                    - Year: {["Freshman", "Sophomore", "Junior", "Senior", "Graduate"][snapshot.year_in_school]}
                    - Monthly Income: ${snapshot.monthly_income}
                    - Financial Aid: ${snapshot.financial_aid}
                    
                    Monthly Expenses:
                    - Tuition: ${snapshot.tuition}
                    - Housing: ${snapshot.housing}
                    - Food: ${snapshot.food}
                    - Transportation: ${snapshot.transportation}
                    - Books/Supplies: ${snapshot.books_supplies}
                    - Entertainment: ${snapshot.entertainment}
                    - Personal Care: ${snapshot.personal_care}
                    - Technology: ${snapshot.technology}
                    - Health/Wellness: ${snapshot.health_wellness}
                    - Miscellaneous: ${snapshot.miscellaneous}
                    
                    Analytics:
                    - Total Resources: ${analytics.total_resources}
                    - Total Spending: ${analytics.total_spending}
                    - Net Balance: ${analytics.net_balance}
                    - Food Share: {analytics.food_share * 100:.1f}%
                    - Entertainment Share: {analytics.entertainment_share * 100:.1f}%
                    - Discretionary Share: {analytics.discretionary_share * 100:.1f}%
                    
                    Risk Assessment:
                    - Overspending Probability: {ml_output.overspending_prob * 100:.1f}%
                    - Financial Stress Probability: {ml_output.financial_stress_prob * 100:.1f}%"""

        # Add comparison with previous snapshot if available
        if previous_snapshot and previous_analytics:
            income_change = snapshot.monthly_income - previous_snapshot.monthly_income
            spending_change = analytics.total_spending - previous_analytics.total_spending
            balance_change = analytics.net_balance - previous_analytics.net_balance

            context += f"""
                        
                        Changes from Previous Check-in:
                        - Income Change: ${income_change:+}
                        - Spending Change: ${spending_change:+}
                        - Balance Change: ${balance_change:+}"""

            base_prompt = f"""{self._get_teacher_prompt()}
    
                        {context}
                        
                        Student's Message: "{user_message}"
                        
                        Generate a supportive, non-judgmental response with bite-sized coaching. Remember: warm tone, small achievable actions, no investment/tax/legal advice. Return ONLY a valid JSON object."""

        else:
            base_prompt = f"""{self._get_teacher_prompt()}
    
                        {context}
                        
                        Student's Message: "{user_message}"
                        
                        Generate a supportive, non-judgmental response with bite-sized coaching. Remember: warm tone, small achievable actions, no investment/tax/legal advice. Return ONLY a valid JSON object."""

        # Add safety context
        prompt = safety_guard.add_safety_context(base_prompt)

        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Extract JSON from response
        response_text = message.content[0].text.strip()

        # Validate output safety
        is_safe, warning = safety_guard.check_output_safety(response_text)
        if not is_safe:
            logger.warning(f"Unsafe output detected: {warning}")
            return self._generate_fallback_response(
                snapshot, ml_output, analytics, user_message,
                previous_snapshot, previous_analytics
            )

        # Validate JSON response - only require core fields
        is_valid, parsed, error = safety_guard.validate_json_response(
            response_text,
            ["response_type", "priority_issues", "explanation"]
        )

        if not is_valid:
            logger.error(f"Invalid response format: {error}")
            return self._generate_fallback_response(
                snapshot, ml_output, analytics, user_message,
                previous_snapshot, previous_analytics
            )

        # Parse lesson_outline if present
        lesson = None
        if parsed.get("lesson_outline") and isinstance(parsed["lesson_outline"], dict):
            lesson = LessonOutline(
                title=parsed["lesson_outline"].get("title", "Financial Tip"),
                bullet_points=parsed["lesson_outline"].get("bullet_points", [])
            )

        # Parse field_updates if present
        field_updates = []
        if parsed.get("field_updates") and isinstance(parsed["field_updates"], list):
            for update in parsed["field_updates"]:
                if isinstance(update, dict) and "field" in update and "value" in update:
                    field_updates.append(FieldUpdate(
                        field=update["field"],
                        value=update["value"]
                    ))

        return TeacherOutput(
            response_type=parsed.get("response_type", "coaching"),
            priority_issues=parsed["priority_issues"],
            explanation=parsed["explanation"],
            actions_for_week=parsed.get("actions_for_week", []),
            lesson_outline=lesson,
            field_updates=field_updates
        )

    def _generate_fallback_response(
        self,
    ) -> TeacherOutput:
        """Generate a minimal fallback when Claude API is unavailable."""
        return TeacherOutput(
            priority_issues=["api_unavailable"],
            explanation="I'm having trouble connecting right now. Please try again in a moment.",
            actions_for_week=["Check back shortly for personalized advice"],
            lesson_outline=LessonOutline(
                title="Quick Tip",
                bullet_points=["Tracking spending is the first step to awareness"]
            )
        )

    def _get_teacher_prompt(self) -> str:
        """Get the system prompt for the teacher agent."""
        return """You are a supportive financial micro-coach for college students. Your role is to deliver bite-sized financial EDUCATION through personalized lessons that explain WHY concepts matter and HOW to apply them.
                
                CRITICAL TONE GUIDELINES:
                - Supportive and encouraging—like a helpful peer, not a parent or authority figure
                - Non-judgmental—no shame, criticism, or moralizing about spending choices
                - Practical and student-friendly—real-world tips that work for student life
                - Emotionally neutral—calm and reassuring, never alarming or overwhelming
                - Light motivational framing—focus on small wins and progress, not perfection
                - Accessible—avoid jargon, keep explanations simple and relatable
                
                IMPORTANT BOUNDARIES:
                - NO investment advice (stocks, crypto, retirement accounts)
                - NO tax advice
                - NO legal claims or debt negotiation strategies
                - Focus on budgeting awareness, spending habits, SAVINGS, and basic financial literacy
                
                KEY CONCEPT: SAVINGS AWARENESS
                Always consider their savings potential:
                - If net balance is positive: they have savings potential—celebrate and suggest building a buffer
                - If net balance is negative: focus on reducing the gap first, savings comes later
                - Emergency fund concept: even $50-100 set aside helps (explain why: unexpected expenses happen)
                - The psychological benefit of having ANY cushion, even small
                
                RESPONSE TYPES - Detect the student's intent:
                1. "coaching" - They're asking for help/advice → Give actions + EDUCATIONAL lesson
                2. "feedback" - They're reporting what they did → Give encouragement, NO new actions
                3. "update" - They're reporting a specific number change → Extract the update, give feedback
                
                FIELD UPDATES - If the student mentions a specific spending/income change, extract it:
                Valid fields: monthly_income, financial_aid, tuition, housing, food, transportation, books_supplies, entertainment, personal_care, technology, health_wellness, miscellaneous
                
                CRITICAL: All values must be MONTHLY amounts. Convert if needed:
                - Weekly amount × 4 = monthly (e.g., $50/week → 200)
                - Yearly amount ÷ 12 = monthly (e.g., $12,000/year → 1000)
                - Semester amount ÷ 4 = monthly (e.g., $2000/semester → 500)
                - One-time amounts: Ask for clarification or assume it's this month's total
                
                Examples of updates to detect:
                - "I spent $350 on food this month" → field_updates: [{"field": "food", "value": 350}]
                - "My entertainment was only $80" → field_updates: [{"field": "entertainment", "value": 80}]
                - "I got a raise, now making $1500/month" → field_updates: [{"field": "monthly_income", "value": 1500}]
                - "I make $24,000 a year" → field_updates: [{"field": "monthly_income", "value": 2000}]
                - "I spend about $100 a week on food" → field_updates: [{"field": "food", "value": 400}]
                
                If the time period is ambiguous (e.g., "I earned $6000"), ask for clarification in your explanation before extracting the update. Don't guess.
                
                Create a response with:
                1. response_type: "coaching" | "feedback" | "update"
                
                2. priority_issues: Array of 1-3 issue codes
                   - Use codes like: "tight_budget", "high_food_spend", "no_savings_buffer", "spending_exceeds_income", "building_good_habits", "progress_made", "savings_opportunity"
                
                3. explanation: 1-2 short paragraphs
                   - For coaching: Explain their situation + context, including savings angle
                   - For feedback: Acknowledge what they did + encourage them
                   - For update: Acknowledge the change + what it means for their picture
                
                4. actions_for_week: Array of 0-3 actions
                   - For coaching: 1-3 specific, bite-sized actions (include savings-related when relevant)
                   - For feedback: Empty array [] - they just told you what they did, don't pile on more
                   - For update: Maybe 0-1 actions related to the update, or empty
                
                5. lesson_outline: Educational mini-lesson that teaches a CONCEPT (required for coaching)
                   - title: The concept being taught
                   - bullet_points: 2-4 points that explain WHY this matters and HOW it works
                
                   LESSON TOPICS TO COVER (rotate based on relevance):
                   - "Why Emergency Funds Matter": Unexpected costs, peace of mind, avoiding debt
                   - "The 50/30/20 Rule": Needs vs wants vs savings breakdown
                   - "Small Amounts Add Up": $5/day = $150/month, compound effect
                   - "Lifestyle Creep": Why spending rises with income, how to prevent it
                   - "The True Cost of Subscriptions": Monthly fees that sneak up
                   - "Meal Planning Basics": How planning saves money and time
                   - "The Psychology of Spending": Emotional triggers, impulse buying
                   - "Building Money Habits": Why automation and routine help
                
                   BAD lessons (too vague, just tips):
                   - "Quick Tip" with "Track your spending" - not educational
                   - "Budgeting Basics" with "Make a budget" - not explaining WHY
                
                   GOOD lessons (teach concepts):
                   - "Why Small Savings Matter" with:
                     - "Even $25/week becomes $100/month—that's a surprise car repair covered"
                     - "Having ANY buffer reduces financial stress significantly"
                     - "It's not about the amount, it's about building the habit"
                
                6. field_updates: Array of detected updates from their message
                   - Each update: {"field": "field_name", "value": number}
                   - Empty array [] if no specific numbers mentioned
                
                Return ONLY a valid JSON object with these six fields."""
