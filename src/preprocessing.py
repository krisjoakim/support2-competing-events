"""Leakage-safe, model-specific preprocessing for SUPPORT2 predictors."""

from sklearn.compose import ColumnTransformer
from sklearn.impute import MissingIndicator, SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .config import CANDIDATE_CATEGORICAL_FEATURES, CANDIDATE_NUMERIC_FEATURES


LINEAR_FAMILIES = {'Multinomial logistic regression'}


def build_preprocessor(
    features: list[str],
    family: str,
    *,
    indicator_features: list[str] | None = None,
) -> ColumnTransformer:
    """Return an unfitted preprocessor tailored to one model family.

    Linear models standardise median-imputed numeric measurements. Tree models
    retain the original numeric scale. Missingness indicators form a separate
    controllable block, categorical variables receive an explicit missing
    level, and non-candidate analysis flags pass through unchanged.
    """
    numeric = [name for name in CANDIDATE_NUMERIC_FEATURES if name in features]
    categorical = [name for name in CANDIDATE_CATEGORICAL_FEATURES if name in features]
    derived_binary = [
        name for name in features
        if name not in CANDIDATE_NUMERIC_FEATURES
        and name not in CANDIDATE_CATEGORICAL_FEATURES
    ]
    indicator_features = [] if indicator_features is None else [
        name for name in indicator_features if name in numeric
    ]

    numeric_steps = [('impute', SimpleImputer(strategy='median'))]
    if family in LINEAR_FAMILIES:
        numeric_steps.append(('scale', StandardScaler()))

    transformers = []
    if numeric:
        transformers.append(('numeric', Pipeline(numeric_steps), numeric))
    if indicator_features:
        transformers.append((
            'missing', MissingIndicator(features='all'), indicator_features,
        ))
    if categorical:
        transformers.append((
            'categorical',
            Pipeline([
                ('impute', SimpleImputer(strategy='constant', fill_value='Missing')),
                ('one_hot', OneHotEncoder(handle_unknown='ignore', sparse_output=False)),
            ]),
            categorical,
        ))
    if derived_binary:
        transformers.append(('derived', 'passthrough', derived_binary))

    return ColumnTransformer(
        transformers,
        sparse_threshold=0.0,
        verbose_feature_names_out=False,
    )
