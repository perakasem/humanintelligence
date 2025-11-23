from enum import IntEnum


class Gender(IntEnum):
    """Gender encoding for ML model."""
    MALE = 0
    FEMALE = 1
    NON_BINARY = 2
    PREFER_NOT_TO_SAY = 3


class YearInSchool(IntEnum):
    """Year in school encoding for ML model."""
    FRESHMAN = 0
    SOPHOMORE = 1
    JUNIOR = 2
    SENIOR = 3
    GRADUATE = 4


class Major(IntEnum):
    """Major category encoding for ML model."""
    STEM = 0
    BUSINESS = 1
    HUMANITIES = 2
    SOCIAL_SCIENCES = 3
    ARTS = 4
    HEALTH_SCIENCES = 5
    EDUCATION = 6
    LAW = 7
    OTHER = 8


class PaymentMethod(IntEnum):
    """Preferred payment method encoding for ML model."""
    CASH = 0
    CREDIT_CARD = 1
    DEBIT_CARD = 2
    MOBILE_PAYMENT = 3


# Mapping dictionaries for display purposes
GENDER_LABELS = {
    Gender.MALE: "Male",
    Gender.FEMALE: "Female",
    Gender.NON_BINARY: "Non-binary",
    Gender.PREFER_NOT_TO_SAY: "Prefer not to say",
}

YEAR_LABELS = {
    YearInSchool.FRESHMAN: "Freshman",
    YearInSchool.SOPHOMORE: "Sophomore",
    YearInSchool.JUNIOR: "Junior",
    YearInSchool.SENIOR: "Senior",
    YearInSchool.GRADUATE: "Graduate",
}

MAJOR_LABELS = {
    Major.STEM: "STEM (Science, Technology, Engineering, Math)",
    Major.BUSINESS: "Business",
    Major.HUMANITIES: "Humanities",
    Major.SOCIAL_SCIENCES: "Social Sciences",
    Major.ARTS: "Arts",
    Major.HEALTH_SCIENCES: "Health Sciences",
    Major.EDUCATION: "Education",
    Major.LAW: "Law",
    Major.OTHER: "Other",
}

PAYMENT_METHOD_LABELS = {
    PaymentMethod.CASH: "Cash",
    PaymentMethod.CREDIT_CARD: "Credit Card",
    PaymentMethod.DEBIT_CARD: "Debit Card",
    PaymentMethod.MOBILE_PAYMENT: "Mobile Payment (Venmo, Cash App, etc.)",
}
