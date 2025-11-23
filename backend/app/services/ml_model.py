import os
import random
import math
import joblib
import pandas as pd
from pathlib import Path
from ..schemas.ml import MLInput, MLOutput
from ..config import get_settings

settings = get_settings()

# Model paths
MODEL_DIR = Path(__file__).parent.parent / "ml_models"
STRESS_MODEL_PATH = MODEL_DIR / "financial_stress_model.joblib"
OVERSPENDING_MODEL_PATH = MODEL_DIR / "overspending_model.joblib"

# Mappings from integer codes to string values expected by the model
GENDER_MAP = {0: "Male", 1: "Female", 2: "Non-binary", 3: "Non-binary"}
YEAR_MAP = {0: "Freshman", 1: "Sophomore", 2: "Junior", 3: "Senior", 4: "Graduate"}
MAJOR_MAP = {
    0: "Computer Science", 1: "Business", 2: "English", 3: "Psychology",
    4: "Art", 5: "Biology", 6: "Education", 7: "Law", 8: "Economics"
}
PAYMENT_MAP = {0: "Cash", 1: "Credit/Debit Card", 2: "Credit/Debit Card", 3: "Mobile Payment App"}


class SpendingRiskModelService:
    """
    Service for calling the ML model to predict spending risks.
    Uses trained scikit-learn models for predictions.
    """

    def __init__(self):
        self.endpoint = settings.ml_model_endpoint
        self._stress_model = None
        self._overspending_model = None
        self._models_loaded = False

    def _load_models(self):
        """Load the trained models from disk."""
        if self._models_loaded:
            return

        if STRESS_MODEL_PATH.exists() and OVERSPENDING_MODEL_PATH.exists():
            try:
                self._stress_model = joblib.load(STRESS_MODEL_PATH)
                self._overspending_model = joblib.load(OVERSPENDING_MODEL_PATH)
                self._models_loaded = True
                print("ML models loaded successfully")
            except Exception as e:
                print(f"Error loading models: {e}")
                self._models_loaded = False
        else:
            print(f"Model files not found. Run 'python train_models.py' first.")
            self._models_loaded = False

    async def predict(self, ml_input: MLInput) -> MLOutput:
        """
        Get risk predictions from the ML models.
        """
        # Try to load models
        self._load_models()

        if self._models_loaded:
            return self._predict_with_models(ml_input)
        else:
            # Fall back to mock predictions if models aren't available
            return self._mock_predict(ml_input)

    def _predict_with_models(self, ml_input: MLInput) -> MLOutput:
        """Use trained models for prediction."""
        # Prepare input data as DataFrame
        # Convert integer codes to string values expected by the model
        data = {
            "gender": [GENDER_MAP.get(ml_input.gender, "Male")],
            "year_in_school": [YEAR_MAP.get(ml_input.year_in_school, "Freshman")],
            "major": [MAJOR_MAP.get(ml_input.major, "Economics")],
            "preferred_payment_method": [PAYMENT_MAP.get(ml_input.preferred_payment_method, "Credit/Debit Card")],
            "age": [ml_input.age],
            "monthly_income": [ml_input.monthly_income],
            "financial_aid": [ml_input.financial_aid],
            "tuition": [ml_input.tuition],
            "housing": [ml_input.housing],
            "food": [ml_input.food],
            "transportation": [ml_input.transportation],
            "books_supplies": [ml_input.books_supplies],
            "entertainment": [ml_input.entertainment],
            "personal_care": [ml_input.personal_care],
            "technology": [ml_input.technology],
            "health_wellness": [ml_input.health_wellness],
            "miscellaneous": [ml_input.miscellaneous],
        }

        df = pd.DataFrame(data)

        # Financial stress prediction (classification)
        # Get probability of stress (class 1)
        stress_proba = self._stress_model.predict_proba(df)[0]
        # Index 1 is probability of True (stressed)
        financial_stress_prob = float(stress_proba[1]) if len(stress_proba) > 1 else float(stress_proba[0])

        # Overspending prediction (regression)
        # The model outputs a dollar amount (not a percentage)
        overspending_raw = self._overspending_model.predict(df)[0]

        # Convert dollar amount to probability using logistic sigmoid
        # Scale factor of 400 means more conservative estimates:
        # - $0 overspending → ~50% probability
        # - $200 overspending → ~62% probability
        # - $400 overspending → ~73% probability
        # - $800 overspending → ~88% probability
        # - Negative values (underspending) → lower probabilities
        scale_factor = 400.0
        overspending_prob = 1 / (1 + math.exp(-overspending_raw / scale_factor))

        # Clamp to reasonable bounds - cap at 85% to avoid overstating
        overspending_prob = min(0.85, max(0.05, overspending_prob))

        return MLOutput(
            overspending_prob=round(overspending_prob, 3),
            financial_stress_prob=round(financial_stress_prob, 3)
        )

    def _mock_predict(self, ml_input: MLInput) -> MLOutput:
        """
        Generate mock predictions based on simple rules.
        Replace with actual ML model in production.
        """
        # Calculate total income and spending
        total_income = ml_input.monthly_income + ml_input.financial_aid
        total_spending = (
            ml_input.tuition + ml_input.housing + ml_input.food +
            ml_input.transportation + ml_input.books_supplies +
            ml_input.entertainment + ml_input.personal_care +
            ml_input.technology + ml_input.health_wellness +
            ml_input.miscellaneous
        )

        # Calculate discretionary spending
        discretionary = (
            ml_input.entertainment + ml_input.personal_care +
            ml_input.miscellaneous
        )

        # Base overspending probability on spending vs income ratio
        if total_income == 0:
            spending_ratio = 2.0
        else:
            spending_ratio = total_spending / total_income

        # Overspending probability - more conservative estimates
        if spending_ratio >= 1.3:
            overspending_base = 0.7
        elif spending_ratio >= 1.1:
            overspending_base = 0.5
        elif spending_ratio >= 1.0:
            overspending_base = 0.35
        elif spending_ratio >= 0.9:
            overspending_base = 0.2
        else:
            overspending_base = 0.1

        # Adjust for discretionary spending ratio
        if total_income > 0:
            discretionary_ratio = discretionary / total_income
            if discretionary_ratio > 0.3:
                overspending_base = min(0.85, overspending_base + 0.1)
            elif discretionary_ratio > 0.2:
                overspending_base = min(0.85, overspending_base + 0.05)

        # Financial stress probability
        # Based on income level, year in school, and spending patterns
        if total_income < 800:
            stress_base = 0.7
        elif total_income < 1200:
            stress_base = 0.5
        elif total_income < 1800:
            stress_base = 0.35
        else:
            stress_base = 0.2

        # Adjust for spending ratio
        if spending_ratio > 1.0:
            stress_base = min(0.95, stress_base + 0.2)
        elif spending_ratio > 0.95:
            stress_base = min(0.95, stress_base + 0.1)

        # Adjust for year in school (seniors/grad students often more stressed)
        if ml_input.year_in_school >= 3:
            stress_base = min(0.95, stress_base + 0.05)

        # Add small random variation
        overspending_prob = max(0.05, min(0.95,
            overspending_base + random.uniform(-0.05, 0.05)
        ))
        financial_stress_prob = max(0.05, min(0.95,
            stress_base + random.uniform(-0.05, 0.05)
        ))

        return MLOutput(
            overspending_prob=round(overspending_prob, 3),
            financial_stress_prob=round(financial_stress_prob, 3)
        )
