"""SUPPORT2 retrieval, descriptive naming, and deterministic splitting."""

import json
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split
from ucimlrepo import fetch_ucirepo

from .config import SEED


EXPECTED_SOURCE_COLUMNS = [
    'id', 'age', 'death', 'sex', 'hospdead', 'slos', 'd.time', 'dzgroup',
    'dzclass', 'num.co', 'edu', 'income', 'scoma', 'charges', 'totcst',
    'totmcst', 'avtisst', 'race', 'sps', 'aps', 'surv2m', 'surv6m', 'hday',
    'diabetes', 'dementia', 'ca', 'prg2m', 'prg6m', 'dnr', 'dnrday',
    'meanbp', 'wblc', 'hrt', 'resp', 'temp', 'pafi', 'alb', 'bili', 'crea',
    'sod', 'ph', 'glucose', 'bun', 'urine', 'adlp', 'adls', 'sfdm2', 'adlsc',
]


def load_support2() -> pd.DataFrame:
    """Retrieve, validate, and descriptively rename the official SUPPORT2 data.

    The data are obtained through ``fetch_ucirepo(id=880)``; no local CSV or
    manual download is used.  Validation occurs on the original source names
    before the documented descriptive project names are applied.  The returned
    frame has 9,105 unique patients and uses ``patient_id`` as its identifier.
    """
    source = fetch_ucirepo(id=880)
    frame = source.data.original
    if source.metadata.get('uci_id') != 880 or source.metadata.get('name') != 'SUPPORT2':
        raise ValueError('UCI retrieval did not return the expected SUPPORT2 dataset.')
    if frame.shape != (9_105, 48) or frame.columns.tolist() != EXPECTED_SOURCE_COLUMNS:
        raise ValueError('SUPPORT2 structure does not match the expected 9,105 by 48 source table.')
    if not frame['id'].is_unique or not frame['slos'].between(3, 343).all():
        raise ValueError('SUPPORT2 identifier or hospital-exit-time checks failed.')

    path = Path(__file__).resolve().parents[1] / 'data' / 'column_names.json'
    with path.open(encoding='utf-8') as file:
        column_names = json.load(file)
    return frame.rename(columns=column_names)


def create_fixed_split(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Create the fixed 70/15/15 patient split used throughout the analysis.

    The operation is a simple seeded random split of unique SUPPORT2 patients.
    It does not use outcomes for stratification.  Returned frames are sorted by
    ``patient_id`` and retain that column for notebook-level indexing.
    """
    train, remaining = train_test_split(frame, test_size=0.30, random_state=SEED, shuffle=True)
    validation, test = train_test_split(remaining, test_size=0.50, random_state=SEED, shuffle=True)
    split = tuple(part.sort_values('patient_id').reset_index(drop=True) for part in (train, validation, test))
    identifiers = [set(part['patient_id']) for part in split]
    if identifiers[0] & identifiers[1] or identifiers[0] & identifiers[2] or identifiers[1] & identifiers[2]:
        raise ValueError('Patient overlap was found between fixed splits.')
    return split
