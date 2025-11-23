# 📊 Student Financial Advisor  
### Overspending Regression + Financial Stress Classification

This repository contains two machine learning models designed to analyze and predict student financial behavior using expense and demographic data. The project includes:

- **Overspending Regression Model** – Predicts how much a student will overspend.  
- **Financial Stress Classification Model** – Predicts whether a student is financially stressed.  
- Full **data preprocessing**, **feature engineering**, **model evaluation**, and **hyperparameter tuning** scripts.

---

## 📁 Project Structure
├── data/
│ └── student_finances.csv
├── models/
│ ├── overspending_model.pkl
│ ├── financial_stress_model.pkl
│ └── scalers/
├── src/
│ ├── preprocess.py
│ ├── train_overspending.py
│ ├── train_financial_stress.py
│ ├── tune_overspending.py
│ ├── tune_financial_stress.py
│ └── evaluate.py
├── notebooks/
│ └── EDA.ipynb
└── README.md


---

## 📦 Installation

```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
pip install -r requirements.txt


## 📘 Dataset Description

The dataset includes student spending categories and demographic information:

| Field | Description |
|-------|-------------|
| age | Student's age |
| gender | Male/Female/Other |
| year_in_school | First–Fourth year |
| major | Student's academic major |
| preferred_payment_method | Cash, debit, credit, digital wallet |
| monthly_income | Monthly income from work |
| financial_aid | Grants or scholarships received |
| tuition, housing, food, etc. | Full spending breakdown |
| total_spending | Sum of all expenses |
| total_income | income + financial_aid |
| adjusted_spending | Spending adjusted relative to income |
| overspending | Target variable for regression |
| savings_rate | Savings ratio |
| financial_stress | Target variable for classification |

The numeric variables represent monthly spending or income amounts.  
Categorical variables represent demographic and behavioral characteristics.

---

## 🧼 Preprocessing Steps

Preprocessing is applied automatically before training:

### **Numerical preprocessing**
- StandardScaler normalization  
- Optional outlier clipping using IQR  
- Optional log-transform for skewed features  
- Remove synthetic or redundant leakage features for classification  
  (e.g., overspending, savings_rate, adjusted_spending)

### **Categorical preprocessing**
- OneHotEncoder for:
  - gender  
  - year_in_school  
  - major  
  - preferred_payment_method  
- Drop first category to avoid multicollinearity (optional)

### **Train/test split**
- 80/20 split  
- Stratified for the classification model

Preprocessing logic lives in:  
`src/preprocess.py`

---

## 🤖 Models

### **1️⃣ Overspending Regression Model**
Predicts the overspending amount in dollars.

Baseline model:  
`RandomForestRegressor(n_estimators=300, max_depth=12)`

**Performance (baseline):**

| Metric | Score |
|--------|--------|
| MAE | 3.68 |
| RMSE | 46.07 |
| R² | 0.843 |

---

### **2️⃣ Financial Stress Classification Model**
Predicts whether the student is financially stressed (True/False).

Baseline model:  
`RandomForestClassifier(n_estimators=300, max_depth=10)`

**Performance (baseline):**

| Metric | Score |
|--------|--------|
| Accuracy | 1.00 |
| Precision | 1.00 |
| Recall | 1.00 |
| F1 Score | 1.00 |
| ROC-AUC | 1.00 |

> ⚠️ These perfect scores are likely due to target leakage in the synthetic dataset.  
> Hyperparameter tuning + leakage removal recommended.

---

## 🧪 Training the Models

### Train Overspending Regression
```bash
python src/train_overspending.py

## 🛠 Technologies Used

- **Python 3.11**
- **Scikit-Learn** — machine learning models & evaluation
- **Pandas** — data loading and preprocessing
- **NumPy** — numerical computations
- **Matplotlib / Seaborn** — visualizations
- **Joblib / Pickle** — model serialization
- **Jupyter Notebook** — exploratory data analysis
- **GridSearchCV / RandomizedSearchCV** — hyperparameter tuning
- **Streamlit (optional)** — interactive model demo UI
- **Git & GitHub** — version control
