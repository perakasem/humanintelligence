"""
Script to train and save models. Run to generate model files.
"""

import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
import os

# Create models directory
os.makedirs("app/ml_models", exist_ok=True)

# Load data
df = pd.read_csv("data/preprocessed_student_spending.csv")

# Feature definitions

categorical = ["gender", "year_in_school", "major", "preferred_payment_method"]
numerical = [
    "age", "monthly_income", "financial_aid", "tuition", "housing",
    "food", "transportation", "books_supplies", "entertainment",
    "personal_care", "technology", "health_wellness", "miscellaneous"
]

X = df[categorical + numerical]

# =====================
# FINANCIAL STRESS MODEL (Classification)
# =====================
print("Training Financial Stress Classification Model...")

y_stress = df["financial_stress"]

preprocess_clf = ColumnTransformer([
    ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
    ("num", "passthrough", numerical)
])

stress_model = Pipeline([
    ("prep", preprocess_clf),
    ("clf", RandomForestClassifier(
        n_estimators=400,
        class_weight="balanced",
        random_state=42
    ))
])

X_train, X_test, y_train, y_test = train_test_split(
    X, y_stress, test_size=0.2, random_state=42, stratify=y_stress
)

stress_model.fit(X_train, y_train)

# Save the model
joblib.dump(stress_model, "app/ml_models/financial_stress_model.joblib")
print("Financial Stress model saved to app/ml_models/financial_stress_model.joblib")

# =====================
# OVERSPENDING MODEL (Regression)
# =====================
print("\nTraining Overspending Regression Model...")

y_overspending = df["overspending"]

preprocess_reg = ColumnTransformer([
    ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
    ("num", "passthrough", numerical)
])

overspending_model = Pipeline([
    ("prep", preprocess_reg),
    ("rf", RandomForestRegressor(
        n_estimators=935,
        random_state=42,
        max_depth=18,
        max_features='sqrt',
        min_samples_leaf=2,
        min_samples_split=6
    ))
])

X_train, X_test, y_train, y_test = train_test_split(
    X, y_overspending, test_size=0.2, random_state=42
)

overspending_model.fit(X_train, y_train)

# Save the model
joblib.dump(overspending_model, "app/ml_models/overspending_model.joblib")
print("Overspending model saved to app/ml_models/overspending_model.joblib")

# Save feature names for reference
feature_info = {
    "categorical": categorical,
    "numerical": numerical
}
joblib.dump(feature_info, "app/ml_models/feature_info.joblib")
print("Feature info saved to app/ml_models/feature_info.joblib")

print("\nAll models trained and saved successfully!")
