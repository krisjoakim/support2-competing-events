"""Patient-level scoring, reference predictions, bootstrap, and calibration."""

import numpy as np
import pandas as pd
from scipy.optimize import brentq, minimize
from scipy.special import expit
from sklearn.metrics import roc_auc_score

from .config import ABSOLUTE_HORIZONS, DAILY_DAYS, LANDMARK, SEED


EVENT_NAMES = ('Live discharge', 'In-hospital death')


def build_observed_event_matrix(events: pd.DataFrame) -> np.ndarray:
    """Return cumulative binary indicators for both hospital-exit events."""
    observed = np.zeros((len(events), len(DAILY_DAYS), 2))
    exit_days = events['days_to_hospital_exit'].to_numpy()[:, None]
    event_types = events['event'].to_numpy()[:, None]
    for event in (1, 2):
        observed[:, :, event - 1] = (event_types == event) & (exit_days <= DAILY_DAYS)
    return observed


def validate_probabilities(probabilities: np.ndarray) -> None:
    """Check coherence of patient-level cumulative incidence predictions."""
    if probabilities.ndim != 3 or probabilities.shape[1:] != (90, 2):
        raise ValueError('Expected patient by 90 days by 2 events probabilities.')
    if np.nanmin(probabilities) < -1e-8 or np.nanmax(probabilities) > 1 + 1e-8:
        raise ValueError('Predicted probabilities fall outside [0, 1].')
    if np.nanmin(np.diff(probabilities, axis=1)) < -1e-8:
        raise ValueError('Cumulative incidence must be non-decreasing.')
    if np.nanmax(probabilities.sum(axis=2)) > 1 + 1e-8:
        raise ValueError('Competing cumulative incidences sum above one.')


def score_exit_probabilities(
    probabilities: np.ndarray,
    events: pd.DataFrame,
) -> tuple[pd.DataFrame, float]:
    """Score cumulative incidence with daily Brier and horizon-specific AUC.

    The primary score is the arithmetic mean of the 90 daily patient-level
    Brier scores, first within each event and then across the two events.
    """
    validate_probabilities(probabilities)
    observed = build_observed_event_matrix(events)
    rows = []
    mean_scores = []
    for event_index, event_name in enumerate(EVENT_NAMES):
        daily_brier = np.mean(
            (probabilities[:, :, event_index] - observed[:, :, event_index]) ** 2,
            axis=0,
        )
        mean_daily = float(daily_brier.mean())
        mean_scores.append(mean_daily)
        rows.append({
            'event': event_name, 'metric': 'Mean daily Brier',
            'horizon': '1-90', 'value': mean_daily,
        })
        for absolute_day in ABSOLUTE_HORIZONS:
            day_index = int(absolute_day - DAILY_DAYS[0])
            labels = observed[:, day_index, event_index]
            auc = np.nan
            if np.unique(labels).size == 2:
                auc = float(roc_auc_score(
                    labels, probabilities[:, day_index, event_index],
                ))
            rows.extend([
                {
                    'event': event_name, 'metric': 'Brier',
                    'horizon': int(absolute_day - LANDMARK),
                    'value': float(daily_brier[day_index]),
                },
                {
                    'event': event_name, 'metric': 'AUC',
                    'horizon': int(absolute_day - LANDMARK), 'value': auc,
                },
            ])
    return pd.DataFrame(rows), float(np.mean(mean_scores))


def population_baseline(fit_events: pd.DataFrame, n_patients: int) -> np.ndarray:
    """Return the direct discrete-time Aalen-Johansen population reference."""
    exit_days = fit_events['days_to_hospital_exit'].to_numpy()
    event_types = fit_events['event'].to_numpy()
    survival = 1.0
    cumulative = np.zeros(2)
    curve = np.zeros((len(DAILY_DAYS), 2))
    for position, day in enumerate(DAILY_DAYS):
        at_risk = np.sum(exit_days >= day)
        if at_risk:
            counts = np.array([
                np.sum((exit_days == day) & (event_types == cause))
                for cause in (1, 2)
            ], dtype=float)
            cumulative = cumulative + survival * counts / at_risk
            survival = survival * (1.0 - counts.sum() / at_risk)
        curve[position] = cumulative
    return np.broadcast_to(curve, (n_patients, *curve.shape)).copy()


def bootstrap_metrics(
    model_probabilities: np.ndarray,
    baseline_probabilities: np.ndarray,
    events: pd.DataFrame,
    *,
    n_bootstrap: int,
    seed: int = SEED,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Paired patient bootstrap for model and population-reference metrics."""
    generator = np.random.default_rng(seed)
    metric_frames = []
    comparison_rows = []
    for replicate in range(1, n_bootstrap + 1):
        positions = generator.integers(0, len(events), len(events))
        sampled_events = events.iloc[positions]
        replicate_metrics = {}
        for name, probabilities in (
            ('Final model', model_probabilities),
            ('Population baseline', baseline_probabilities),
        ):
            metrics, _ = score_exit_probabilities(
                probabilities[positions], sampled_events,
            )
            metrics['model'] = name
            metrics['replicate'] = replicate
            metric_frames.append(metrics)
            replicate_metrics[name] = metrics
        for event_name in EVENT_NAMES:
            model_value = replicate_metrics['Final model'].loc[
                lambda frame: frame['event'].eq(event_name)
                & frame['metric'].eq('Mean daily Brier'), 'value'
            ].iloc[0]
            baseline_value = replicate_metrics['Population baseline'].loc[
                lambda frame: frame['event'].eq(event_name)
                & frame['metric'].eq('Mean daily Brier'), 'value'
            ].iloc[0]
            comparison_rows.append({
                'replicate': replicate,
                'event': event_name,
                'absolute_difference': model_value - baseline_value,
                'relative_reduction': (baseline_value - model_value) / baseline_value,
            })
    return pd.concat(metric_frames, ignore_index=True), pd.DataFrame(comparison_rows)


def calibration_parameters(
    predicted: np.ndarray,
    observed: np.ndarray,
) -> tuple[float, float, float]:
    """Estimate calibration-in-the-large and logistic intercept and slope."""
    if np.unique(observed).size < 2:
        return np.nan, np.nan, np.nan
    logits = np.log(np.clip(predicted, 1e-6, 1 - 1e-6) /
                    np.clip(1 - predicted, 1e-6, 1 - 1e-6))
    target_mean = observed.mean()
    intercept_in_large = brentq(
        lambda value: expit(value + logits).mean() - target_mean,
        -30, 30,
    )

    def loss(values: np.ndarray) -> float:
        fitted = expit(values[0] + values[1] * logits)
        return float(-np.sum(
            observed * np.log(np.clip(fitted, 1e-12, 1))
            + (1 - observed) * np.log(np.clip(1 - fitted, 1e-12, 1))
        ))

    fitted = minimize(loss, np.array([0.0, 1.0]), method='BFGS')
    return float(intercept_in_large), float(fitted.x[0]), float(fitted.x[1])


def smooth_calibration(
    predicted: np.ndarray,
    observed: np.ndarray,
    grid: np.ndarray,
    *,
    bandwidth: float = 0.08,
) -> np.ndarray:
    """Return a simple Gaussian-kernel calibration smoother."""
    weights = np.exp(-0.5 * ((predicted[:, None] - grid[None, :]) / bandwidth) ** 2)
    return np.divide(
        (weights * observed[:, None]).sum(axis=0),
        weights.sum(axis=0),
        out=np.full(len(grid), np.nan),
        where=weights.sum(axis=0) > 1e-8,
    )
