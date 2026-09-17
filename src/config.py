"""Stable study settings shared by the SUPPORT2 notebooks."""

import numpy as np


SEED = 20_260_912
LANDMARK = 3
DAYS_AFTER = np.array([7, 14, 30, 60, 90])
DAILY_DAYS = np.arange(LANDMARK + 1, LANDMARK + 91)
FOLLOWUP_DAYS = DAILY_DAYS - LANDMARK
ABSOLUTE_HORIZONS = LANDMARK + DAYS_AFTER
PRACTICAL_MARGIN = 0.002
N_BOOTSTRAP = 2_000

CANDIDATE_NUMERIC_FEATURES = [
    'age', 'years_of_education', 'number_of_comorbidities',
    'hospital_day_at_study_entry', 'mean_arterial_pressure',
    'white_blood_cell_count', 'heart_rate', 'respiratory_rate', 'temperature',
    'pao2_fio2_ratio', 'albumin', 'bilirubin', 'creatinine', 'sodium',
    'arterial_ph', 'glucose', 'blood_urea_nitrogen', 'urine_output',
    'adl_patient_reported', 'adl_surrogate_reported',
]
CANDIDATE_CATEGORICAL_FEATURES = [
    'sex', 'race', 'income_category', 'diagnosis_group', 'diagnosis_class',
    'diabetes', 'dementia', 'cancer_status',
]
CANDIDATE_FEATURES = CANDIDATE_NUMERIC_FEATURES + CANDIDATE_CATEGORICAL_FEATURES

MODEL_FAMILIES = [
    'Multinomial logistic regression',
    'Histogram gradient boosting',
]
MODEL_COMPLEXITY_ORDER = {
    'Multinomial logistic regression': 0,
    'Histogram gradient boosting': 1,
}

DEFAULT_MODEL_PARAMETERS = {
    'Multinomial logistic regression': {'C': 1.0},
    'Histogram gradient boosting': {
        'learning_rate': 0.05, 'max_leaf_nodes': 31, 'max_iter': 200,
        'l2_regularization': 1.0, 'min_samples_leaf': 20,
    },
}

# Small, explicit spaces avoid a large brute-force search.
TUNING_GRIDS = {
    'Multinomial logistic regression': [
        {'C': value} for value in (0.001, 0.01, 0.1, 1.0, 10.0, 100.0)
    ],
    'Histogram gradient boosting': [
        {'learning_rate': lr, 'max_leaf_nodes': leaves, 'max_iter': iterations,
         'l2_regularization': l2, 'min_samples_leaf': minimum}
        for lr, leaves, iterations, l2, minimum in [
            (0.10, 15, 100, 0.0, 20), (0.10, 31, 100, 1.0, 20),
            (0.10, 63, 100, 10.0, 10), (0.05, 15, 200, 0.1, 20),
            (0.05, 31, 200, 1.0, 20), (0.05, 63, 200, 10.0, 10),
            (0.05, 15, 200, 10.0, 50), (0.025, 15, 400, 0.1, 20),
            (0.025, 31, 400, 1.0, 20), (0.025, 63, 400, 10.0, 10),
            (0.05, 7, 200, 1.0, 50), (0.05, 31, 200, 10.0, 100),
        ]
    ],
}

SUBSET_SIZES = [5, 10, 15, 20, len(CANDIDATE_FEATURES)]

FEATURE_DISPLAY_NAMES = {
    'age': 'Age', 'years_of_education': 'Years of education',
    'number_of_comorbidities': 'Number of comorbidities',
    'hospital_day_at_study_entry': 'Hospital day at study entry',
    'mean_arterial_pressure': 'Mean arterial pressure',
    'white_blood_cell_count': 'White blood cell count',
    'heart_rate': 'Heart rate', 'respiratory_rate': 'Respiratory rate',
    'temperature': 'Temperature', 'pao2_fio2_ratio': 'PaO2/FiO2 ratio',
    'albumin': 'Albumin', 'bilirubin': 'Bilirubin',
    'creatinine': 'Creatinine', 'sodium': 'Sodium',
    'arterial_ph': 'Arterial pH', 'glucose': 'Glucose',
    'blood_urea_nitrogen': 'Blood urea nitrogen',
    'urine_output': 'Urine output',
    'adl_patient_reported': 'Patient-reported ADL',
    'adl_surrogate_reported': 'Surrogate-reported ADL',
    'sex': 'Sex', 'race': 'Race', 'income_category': 'Income category',
    'diagnosis_group': 'Diagnosis group', 'diagnosis_class': 'Diagnosis class',
    'diabetes': 'Diabetes', 'dementia': 'Dementia',
    'cancer_status': 'Cancer status', 'support_coma_score': 'SUPPORT coma score',
    'imputed_adl_score': 'Imputed ADL score',
    'adl_patient_reported_missing': 'Patient-reported ADL missing',
}
