"""Discrete-time model fitting and patient-level cross-validation."""

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression

from .config import CANDIDATE_NUMERIC_FEATURES, SEED
from .evaluation import score_exit_probabilities
from .patient_day import expand_to_patient_days, predict_exit_probabilities
from .preprocessing import build_preprocessor


def default_indicator_features(features: list[str]) -> list[str]:
    """Return eligible numeric inputs present in a feature set."""
    return [name for name in CANDIDATE_NUMERIC_FEATURES if name in features]


def transform_patient_features(
    preprocessor: object,
    patients: pd.DataFrame,
    features: list[str],
) -> pd.DataFrame:
    """Transform patients with preprocessing fitted on training patients."""
    transformed = preprocessor.transform(patients[features])
    return pd.DataFrame(
        transformed,
        index=patients.index,
        columns=preprocessor.get_feature_names_out(),
    ).astype(float)


def fit_candidate(
    fit_patients: pd.DataFrame,
    features: list[str],
    family: str,
    parameters: dict[str, object],
    *,
    indicator_features: list[str] | None = None,
) -> tuple[object, object]:
    """Fit one complete candidate pipeline on fit patients only."""
    preprocessor = build_preprocessor(
        features, family, indicator_features=indicator_features,
    )
    encoded = pd.DataFrame(
        preprocessor.fit_transform(fit_patients[features]),
        index=fit_patients.index,
        columns=preprocessor.get_feature_names_out(),
    ).astype(float)

    if family == 'Multinomial logistic regression':
        patient_day_x, patient_day_y = expand_to_patient_days(encoded, fit_patients)
        model = LogisticRegression(
            C=float(parameters['C']), solver='lbfgs', max_iter=2_000,
            random_state=SEED,
        ).fit(patient_day_x, patient_day_y)
    elif family == 'Histogram gradient boosting':
        patient_day_x, patient_day_y = expand_to_patient_days(encoded, fit_patients)
        model = HistGradientBoostingClassifier(
            learning_rate=float(parameters['learning_rate']),
            max_leaf_nodes=int(parameters['max_leaf_nodes']),
            max_iter=int(parameters['max_iter']),
            l2_regularization=float(parameters['l2_regularization']),
            min_samples_leaf=int(parameters['min_samples_leaf']),
            early_stopping=False, random_state=SEED,
        ).fit(patient_day_x, patient_day_y)
    else:
        raise ValueError(f'Unknown model family: {family}')
    return preprocessor, model


def predict_candidate(
    preprocessor: object,
    model: object,
    patients: pd.DataFrame,
    features: list[str],
    family: str,
) -> np.ndarray:
    """Return cumulative event probabilities on the common daily grid."""
    encoded = transform_patient_features(preprocessor, patients, features)
    return predict_exit_probabilities(model, encoded)[1]


def cross_validate_candidate(
    patients: pd.DataFrame,
    features: list[str],
    family: str,
    parameters: dict[str, object],
    folds: list[tuple[np.ndarray, np.ndarray]],
    *,
    indicator_features: list[str] | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Evaluate one candidate in fixed patient-level folds."""
    metric_frames = []
    fold_rows = []
    for fold_number, (fit_positions, assess_positions) in enumerate(folds, start=1):
        fit_patients = patients.iloc[fit_positions]
        assess_patients = patients.iloc[assess_positions]
        preprocessor, model = fit_candidate(
            fit_patients, features, family, parameters,
            indicator_features=indicator_features,
        )
        probabilities = predict_candidate(
            preprocessor, model, assess_patients, features, family,
        )
        metrics, mean_daily_brier = score_exit_probabilities(
            probabilities, assess_patients,
        )
        metrics['fold'] = fold_number
        metric_frames.append(metrics)
        fold_rows.append({'fold': fold_number, 'mean_daily_brier': mean_daily_brier})
    return pd.concat(metric_frames, ignore_index=True), pd.DataFrame(fold_rows)
