"""Light cross-fitted grouped feature ranking and subset assessment."""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from .config import SEED
from .evaluation import score_exit_probabilities
from .modelling import (
    default_indicator_features,
    fit_candidate,
    predict_candidate,
)


def grouped_importance_on_split(
    fit_patients: pd.DataFrame,
    assess_patients: pd.DataFrame,
    features: list[str],
    family: str,
    parameters: dict[str, object],
    *,
    repeats: int = 2,
    seed: int = SEED,
) -> pd.DataFrame:
    """Permute original variables in patients not used for model fitting."""
    preprocessor, model = fit_candidate(
        fit_patients, features, family, parameters,
        indicator_features=default_indicator_features(features),
    )
    baseline = predict_candidate(
        preprocessor, model, assess_patients, features, family,
    )
    _, baseline_score = score_exit_probabilities(baseline, assess_patients)
    generator = np.random.default_rng(seed)
    rows = []
    for feature in features:
        for repeat in range(1, repeats + 1):
            permuted = assess_patients.copy()
            permuted[feature] = generator.permutation(permuted[feature].to_numpy())
            probabilities = predict_candidate(
                preprocessor, model, permuted, features, family,
            )
            _, score = score_exit_probabilities(probabilities, permuted)
            rows.append({
                'feature': feature, 'repeat': repeat,
                'importance': score - baseline_score,
            })
    return pd.DataFrame(rows)


def cross_fitted_feature_simplification(
    patients: pd.DataFrame,
    features: list[str],
    family: str,
    parameters: dict[str, object],
    folds: list[tuple[np.ndarray, np.ndarray]],
    subset_sizes: list[int],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Rank within outer training data and score subsets on outer held-out data.

    Each outer training portion receives one deterministic 80/20 internal split
    used only to rank original variables. Hyperparameters remain fixed. The
    resulting fold-specific ranking is then assessed on the held-out outer
    fold, avoiding a full nested model search.
    """
    importance_frames = []
    subset_rows = []
    for fold_number, (outer_fit_positions, outer_assess_positions) in enumerate(
        folds, start=1,
    ):
        outer_fit = patients.iloc[outer_fit_positions]
        outer_assess = patients.iloc[outer_assess_positions]
        stratify = outer_fit['event'].astype(str) + '_' + pd.qcut(
            outer_fit['days_to_hospital_exit'], q=4, duplicates='drop',
        ).astype(str)
        inner_fit_positions, inner_rank_positions = train_test_split(
            np.arange(len(outer_fit)), test_size=0.20,
            random_state=SEED + fold_number, stratify=stratify,
        )
        importance = grouped_importance_on_split(
            outer_fit.iloc[inner_fit_positions],
            outer_fit.iloc[inner_rank_positions],
            features, family, parameters,
            repeats=2, seed=SEED + fold_number,
        )
        importance['fold'] = fold_number
        importance['model'] = family
        importance_frames.append(importance)
        ranking = (
            importance.groupby('feature')['importance'].mean()
            .sort_values(ascending=False).index.tolist()
        )
        for subset_size in subset_sizes:
            selected = ranking[:subset_size]
            preprocessor, model = fit_candidate(
                outer_fit, selected, family, parameters,
                indicator_features=default_indicator_features(selected),
            )
            probabilities = predict_candidate(
                preprocessor, model, outer_assess, selected, family,
            )
            _, score = score_exit_probabilities(probabilities, outer_assess)
            subset_rows.append({
                'model': family, 'fold': fold_number,
                'n_features': subset_size, 'mean_daily_brier': score,
            })
    return pd.concat(importance_frames, ignore_index=True), pd.DataFrame(subset_rows)
