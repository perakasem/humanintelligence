import json
import logging
import anthropic
from ..schemas.intake import SnapshotData
from ..schemas.dashboard import SummaryOutput, Analytics
from ..schemas.ml import MLOutput
from ..config import get_settings
from .claude_safety import safety_guard

settings = get_settings()
logger = logging.getLogger(__name__)


class ClaudeSummarizerService:
    """
    Service for generating human-readable summaries of financial data.
    Uses Claude to create personalized, empathetic summaries.
    """

    def __init__(self):
        self.api_key = settings.anthropic_api_key
        self.client = anthropic.Anthropic(api_key=self.api_key) if self.api_key else None

    async def summarize(
        self,
        snapshot: SnapshotData,
        ml_output: MLOutput,
        analytics: Analytics
    ) -> SummaryOutput:
        """
        Generate a summary of the user's financial situation.
        Uses Claude API for intelligent summarization.
        """
        # Validate input data
        input_data = snapshot.model_dump() if hasattr(snapshot, 'model_dump') else snapshot.__dict__
        is_valid, error = safety_guard.validate_financial_data(input_data)
        if not is_valid:
            logger.error(f"Invalid financial data: {error}")
            return self._generate_fallback_summary(snapshot, ml_output, analytics)

        # Try Claude API first, fall back to minimal response if unavailable
        if self.client and self.api_key:
            try:
                result = self._summarize_with_claude(snapshot, ml_output, analytics)
                safety_guard.log_interaction("summarizer", "financial_snapshot", result.summary_paragraph[:50], True)
                return result
            except Exception as e:
                logger.error(f"Claude summarization failed: {e}")
                safety_guard.log_interaction("summarizer", "financial_snapshot", str(e), False)
                return self._generate_fallback_summary(snapshot, ml_output, analytics)
        else:
            return self._generate_fallback_summary(snapshot, ml_output, analytics)

    def _summarize_with_claude(
        self,
        snapshot: SnapshotData,
        ml_output: MLOutput,
        analytics: Analytics
    ) -> SummaryOutput:
        """Use Claude to generate a personalized summary."""
        # Prepare the context for Claude
        context = f"""Student Financial Data:
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

        base_prompt = f"""{self._get_summarizer_prompt()}
                            
                            {context}
                            
                            Generate a quick, glanceable summary. Return ONLY a valid JSON object with "summary_paragraph" (1 sentence max, like a headline) and "key_points" (array of 3-4 short facts). Remember: interpret data only, no advice."""

        # Add safety context
        prompt = safety_guard.add_safety_context(base_prompt)

        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
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
            return self._generate_fallback_summary(snapshot, ml_output, analytics)

        # Validate JSON response
        is_valid, parsed, error = safety_guard.validate_json_response(
            response_text,
            ["summary_paragraph", "key_points"]
        )

        if not is_valid:
            logger.error(f"Invalid response format: {error}")
            return self._generate_fallback_summary(snapshot, ml_output, analytics)

        return SummaryOutput(
            summary_paragraph=parsed["summary_paragraph"],
            key_points=parsed["key_points"]
        )

    def _generate_fallback_summary(
        self,
        snapshot: SnapshotData,
        ml_output: MLOutput,
        analytics: Analytics
    ) -> SummaryOutput:
        """Generate a minimal fallback when Claude API is unavailable."""
        # Simple factual summary without AI interpretation
        if analytics.net_balance < 0:
            summary = f"You're spending ${abs(analytics.net_balance)} more than you're bringing in."
        else:
            summary = f"You have a ${analytics.net_balance} monthly surplus."

        return SummaryOutput(
            summary_paragraph=summary,
            key_points=[
                f"Total income: ${analytics.total_resources}/month",
                f"Total spending: ${analytics.total_spending}/month",
                f"Net balance: ${analytics.net_balance}/month"
            ]
        )

    def _get_summarizer_prompt(self) -> str:
        """Get the system prompt for the summarizer agent."""
        return """You are a friendly financial summarizer for college students. Your role is to give them a quick, warm snapshot of their situation—like a supportive friend who's good with numbers.
                
                FORMAT: "Glance and Go"
                - summary_paragraph: ONE sentence, casual and warm—like texting a friend
                - key_points: 3-4 quick facts for context
                
                CRITICAL TONE GUIDELINES:
                - Warm and personal—speak directly to them ("you're", "your")
                - Casual but clear—like a friend explaining, not a report
                - Ultra-concise—keep it scannable
                - Non-judgmental—neutral observations, no criticism
                - Interpretation only—NO advice (that's the teacher's job)
                
                This is a SUPPORT tool, not an analytics tool. Make students feel seen and understood, not analyzed.
                
                Given:
                - Their spending snapshot (income, expenses by category)
                - ML model outputs (overspending probability, financial stress probability)
                - Computed analytics (shares, totals, ratios)
                
                Create a response with:
                1. summary_paragraph: ONE warm, casual sentence that:
                   - Speaks directly to them in second person
                   - Feels personal, not clinical
                   - Under 15 words
                   - Example good: "You're spending about $715 more than you're bringing in each month."
                   - Example good: "You've got a nice $200 cushion each month—solid!"
                   - Example bad: "Your monthly expenses of $3,015 are exceeding your combined income and financial aid of $2,300 by approximately $715." (too formal, too long)
                   - Example bad: "This gap represents a common challenge many students face..." (impersonal, sounds like a report)
                
                2. key_points: 3-4 INSIGHTFUL observations that:
                   - Reveal patterns or context they might not have noticed
                   - Transform raw numbers into meaningful insights
                   - Use percentages, daily amounts, or comparisons—not just raw totals
                   - Be striking and evocative—make them think "oh, I didn't realize that"
                   - 8-12 words each, casual tone
                
                   GOOD examples (provide insight):
                   - "Food is eating up 35% of everything you spend"
                   - "That's about $14/day on food alone"
                   - "Entertainment + food = half your monthly spending"
                   - "You're $715 short each month—about $24/day"
                
                   BAD examples (just repeating inputs):
                   - "Your biggest expense is food at $420/month" (they already know this)
                   - "You're bringing in $2,300 total each month" (they entered this)
                   - "Your housing costs $800/month" (no insight, just echo)
                
                Return ONLY a valid JSON object with "summary_paragraph" (string) and "key_points" (array of strings)."""
