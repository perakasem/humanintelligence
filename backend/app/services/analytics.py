from ..schemas.intake import SnapshotData
from ..schemas.dashboard import Analytics
from ..models.snapshot import SpendingSnapshot


class AnalyticsService:
    """Service for computing analytics from spending snapshots."""

    def compute(self, snapshot: SnapshotData | SpendingSnapshot) -> Analytics:
        """Compute analytics from a snapshot."""
        # Handle both Pydantic model and SQLAlchemy model
        if isinstance(snapshot, SpendingSnapshot):
            data = {
                "monthly_income": snapshot.monthly_income,
                "financial_aid": snapshot.financial_aid,
                "tuition": snapshot.tuition,
                "housing": snapshot.housing,
                "food": snapshot.food,
                "transportation": snapshot.transportation,
                "books_supplies": snapshot.books_supplies,
                "entertainment": snapshot.entertainment,
                "personal_care": snapshot.personal_care,
                "technology": snapshot.technology,
                "health_wellness": snapshot.health_wellness,
                "miscellaneous": snapshot.miscellaneous,
            }
        else:
            data = snapshot.model_dump()

        total_resources = data["monthly_income"] + data["financial_aid"]
        total_spending = (
            data["tuition"] + data["housing"] + data["food"] +
            data["transportation"] + data["books_supplies"] +
            data["entertainment"] + data["personal_care"] +
            data["technology"] + data["health_wellness"] +
            data["miscellaneous"]
        )

        discretionary = (
            data["entertainment"] + data["personal_care"] +
            data["miscellaneous"]
        )

        # Calculate shares (avoid division by zero)
        if total_resources > 0:
            food_share = round(data["food"] / total_resources, 3)
            housing_share = round(data["housing"] / total_resources, 3)
            entertainment_share = round(data["entertainment"] / total_resources, 3)
            discretionary_share = round(discretionary / total_resources, 3)
            tuition_share = round(data["tuition"] / total_resources, 3)
        else:
            food_share = 0.0
            housing_share = 0.0
            entertainment_share = 0.0
            discretionary_share = 0.0
            tuition_share = 0.0

        net_balance = total_resources - total_spending
        is_overspending = net_balance < 0
        overspending_amount = abs(net_balance) if is_overspending else 0
        savings_potential = net_balance if net_balance > 0 else 0

        return Analytics(
            total_resources=total_resources,
            total_spending=total_spending,
            net_balance=net_balance,
            is_overspending=is_overspending,
            overspending_amount=overspending_amount,
            savings_potential=savings_potential,
            food_share=food_share,
            housing_share=housing_share,
            entertainment_share=entertainment_share,
            discretionary_share=discretionary_share,
            tuition_share=tuition_share
        )

    def compute_deltas(
        self,
        current: Analytics,
        previous: Analytics
    ) -> dict:
        """Compute changes between two analytics snapshots."""
        return {
            "total_spending_delta": current.total_spending - previous.total_spending,
            "net_balance_delta": current.net_balance - previous.net_balance,
            "food_share_delta": round(current.food_share - previous.food_share, 3),
            "entertainment_share_delta": round(
                current.entertainment_share - previous.entertainment_share, 3
            ),
            "discretionary_share_delta": round(
                current.discretionary_share - previous.discretionary_share, 3
            ),
        }
