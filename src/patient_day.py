"""Patient-day outcome representation and probability accumulation."""

import numpy as np
import pandas as pd

from .config import DAILY_DAYS, LANDMARK


def expand_to_patient_days(
    encoded_features: pd.DataFrame,
    events: pd.DataFrame,
) -> tuple[np.ndarray, np.ndarray]:
    """Expand fit patients into at-risk patient-day rows and daily targets.

    One patient row becomes one row for every day at risk after the landmark.
    The target is 0 while hospitalised, 1 on live discharge, and 2 on
    in-hospital death.  No rows are created after the terminal hospital exit.
    Scaled day and scaled day squared are appended to every encoded feature row
    so the classifier can model time-varying exit probabilities.
    """
    aligned_events = events.loc[encoded_features.index]
    rows: list[np.ndarray] = []
    targets: list[int] = []
    for position, (_, patient) in enumerate(aligned_events.iterrows()):
        last_day = min(int(patient['days_to_hospital_exit']), int(DAILY_DAYS[-1]))
        for day in range(LANDMARK + 1, last_day + 1):
            scaled_day = (day - LANDMARK) / len(DAILY_DAYS)
            rows.append(np.r_[encoded_features.iloc[position].to_numpy(float), scaled_day, scaled_day ** 2])
            targets.append(int(patient['event']) if day == int(patient['days_to_hospital_exit']) else 0)
    return np.asarray(rows), np.asarray(targets)


def predict_exit_probabilities(
    model: object,
    encoded_features: pd.DataFrame,
) -> tuple[np.ndarray, np.ndarray]:
    """Predict conditional daily and cumulative competing hospital-exit risks.

    The classifier predicts conditional daily probabilities for stay (0), live
    discharge (1), and in-hospital death (2).  A later event requires the
    patient to have remained hospitalised on every earlier day.  The function
    therefore recursively multiplies daily risks by the probability of still
    being in hospital and returns ``(daily, cumulative)`` arrays.  The last
    array has event channels in the order live discharge, in-hospital death.
    """
    repeated = np.repeat(encoded_features.to_numpy(float), len(DAILY_DAYS), axis=0)
    scaled_day = np.tile((DAILY_DAYS - LANDMARK) / len(DAILY_DAYS), len(encoded_features))
    patient_days = np.column_stack([repeated, scaled_day, scaled_day ** 2])
    predicted = model.predict_proba(patient_days)
    daily = np.zeros((len(encoded_features), len(DAILY_DAYS), 3))
    daily[:, :, np.asarray(model.classes_, dtype=int)] = predicted.reshape(
        len(encoded_features), len(DAILY_DAYS), -1
    )
    cumulative = np.zeros((len(encoded_features), len(DAILY_DAYS), 2))
    still_in_hospital = np.ones(len(encoded_features))
    for day_index in range(len(DAILY_DAYS)):
        if day_index:
            cumulative[:, day_index] = cumulative[:, day_index - 1]
        cumulative[:, day_index, 0] += still_in_hospital * daily[:, day_index, 1]
        cumulative[:, day_index, 1] += still_in_hospital * daily[:, day_index, 2]
        still_in_hospital *= daily[:, day_index, 0]
    return daily, cumulative
