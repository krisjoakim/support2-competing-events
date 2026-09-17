# Hospital Outcome Prediction with SUPPORT2

Read the [technical report (PDF)](report/project_report.pdf) or its
[Markdown source](report/project_report.md) for the complete analysis.

## Research question

Given patient information available around the third SUPPORT study day, how
accurately can the cumulative probability of live discharge or in-hospital death
be estimated over the following 90 days?

Live discharge and in-hospital death are mutually exclusive competing events.
The remaining probability represents continued hospitalisation. The project is
an internally validated analysis of historical data, not a clinical decision tool.

## Data

The official SUPPORT2 dataset is retrieved directly from the UCI Machine Learning
Repository with fetch_ucirepo(id=880). Validation checks confirm UCI ID 880,
the SUPPORT2 name, 9,105 patients, 48 source variables, unique identifiers, the
expected source columns, and the documented hospital-exit-time range. No copied
patient-level CSV is stored in the repository.

The [data dictionary](data/data_dictionary.md) documents source variables,
descriptive project names, missingness, timing where available, and project roles.
The machine-readable rename map is [data/column_names.json](data/column_names.json).

Twenty non-predictor fields are excluded by endpoint, timing, resource-use,
existing-score, or project-scope criteria. The development pool contains 28
eligible candidates: 20 numeric and 8 categorical.

## Statistical design

- Day-3 landmark with patients still hospitalised after assessment.
- Fixed patient-level 70/15/15 training, validation, and held-out test split.
- Five patient-level training folds.
- Live discharge and in-hospital death predicted as competing events.
- Common probability grid covering days 1–90 after assessment.
- Mean daily Brier over all 90 days as the primary probability metric.
- Horizon-specific Brier and AUC at 7, 14, 30, 60, and 90 days.
- Direct discrete-time Aalen–Johansen population reference.
- Model-specific preprocessing fitted only within the relevant training data.

Two model families are compared in the same discrete-time formulation:

1. Multinomial logistic regression on patient-day outcomes.
2. Histogram gradient boosting on patient-day outcomes.

Both models estimate the conditional probabilities of continued
hospitalisation, live discharge, and in-hospital death on each day. A common
recursion converts those daily predictions into coherent cumulative patient-level
probabilities.

## Notebook workflow

1. [Data exploration](notebooks/01_data_exploration.ipynb)
2. [Problem definition and preprocessing](notebooks/02_problem_and_preprocessing.ipynb)
3. [Model development](notebooks/03_model_development.ipynb)
4. [Feature simplification and model selection](notebooks/04_feature_simplification_and_model_selection.ipynb)
5. [Final evaluation](notebooks/05_final_evaluation.ipynb)

Notebook 03 establishes all-28-feature benchmarks and performs moderate
model-specific tuning. Notebook 04 uses light cross-fitted grouped permutation
importance, verifies feature-count simplification, performs the ADL ablation, and
uses validation for family-neutral model selection. Notebook 05 refits the locked
pipeline on training plus validation and evaluates the held-out test set.

## Selected pipeline

Histogram gradient boosting obtains validation mean daily Brier 0.13142,
compared with 0.13419 for multinomial logistic regression. The improvement of
0.00277 exceeds the prespecified practical margin of 0.002, so HGB is selected.

The locked HGB model uses:

- learning rate: 0.05
- maximum leaf nodes: 15
- iterations: 200
- L2 regularisation: 10.0
- minimum samples per leaf: 50

Its 15 original predictors are patient-reported ADL, diagnosis group, hospital
day at study entry, diagnosis class, surrogate-reported ADL, bilirubin, age, mean
arterial pressure, creatinine, blood urea nitrogen, heart rate, PaO2/FiO2 ratio,
urine output, glucose, and arterial pH.

## Held-out test results

| Outcome | Final mean daily Brier | Population reference | Paired absolute improvement | Relative reduction |
| --- | ---: | ---: | ---: | ---: |
| Live discharge | 0.1503 | 0.2160 | 0.0657 (95% CI 0.0570–0.0747) | 30.4% |
| In-hospital death | 0.1343 | 0.1730 | 0.0387 (95% CI 0.0299–0.0477) | 22.3% |

Across the five reported horizons, AUC ranges from 0.827 to 0.848 for live
discharge and from 0.814 to 0.823 for in-hospital death. All 2,000 paired
patient-level bootstrap replicates produce valid AUC estimates.

At 30 days, calibration slope is 1.02 for live discharge and 0.98 for
in-hospital death. Calibration-in-the-large is −0.29 for discharge and 0.09 for
death, indicating average overprediction of discharge probability but little
systematic mortality miscalibration.

## ADL ablation

| Patient-reported ADL input | Mean daily Brier |
| --- | ---: |
| Value and explicit missingness indicator | 0.13658 |
| Missingness indicator only | 0.13690 |
| Value only | 0.14191 |
| Neither | 0.14419 |

The explicit missingness indicator accounts for most of the predictive gain
associated with this field under the chosen median-imputation scheme. The
value-only condition still median-imputes absent observations, so the ablation is
not a pure decomposition of value and missingness information. Possible workflow
explanations remain hypotheses rather than causal conclusions.

## Code structure

    src/
    ├── config.py              # Study settings, feature pool, and compact grids
    ├── data.py                # UCI retrieval, validation, naming, and fixed split
    ├── preprocessing.py       # Leakage-safe model-specific transformations
    ├── patient_day.py         # Discrete-time expansion and probability recursion
    ├── modelling.py           # Discrete-time fitting and patient-level CV
    ├── evaluation.py          # Metrics, baseline, bootstrap, and calibration
    └── feature_selection.py   # Light cross-fitted grouped feature simplification

Machine-readable tables, locked specifications, and bootstrap distributions are
stored under results/.

## Reproduce

The saved notebooks record Python 3.11.11. Direct analysis dependencies are
pinned in [requirements.txt](requirements.txt). Use a fresh Python 3.11
environment; an existing environment may contain different package versions.

    python3.11 -m venv .venv-reproduce
    source .venv-reproduce/bin/activate
    python -m pip install -r requirements.txt
    python -m pip check
    python -m jupyterlab

Run notebooks 01 through 05 in order. Notebook 05 reads the locked specification
written by notebook 04. Internet access is required to retrieve SUPPORT2.
The saved public version of notebook 05 omits its patient-context table; rerunning
the final plotting cell displays that table again. Clear that table output before
sharing or committing the notebook. See the [data documentation](data/README.md)
for the distinction between current files and earlier Git history.

## Limitations

SUPPORT2 is historical, and the test cohort comes from the same source population
rather than an external contemporary cohort. Prediction starts after day 3 and
does not address admission-time prediction. Missingness indicators do not explain
the missing-data mechanism. The models use daily time resolution. Subgroup and
individual trajectories describe model behaviour rather than causal effects or
treatment recommendations.

Code and documentation are released under the [MIT License](LICENSE). The license
does not apply to SUPPORT2 data; see the [data attribution and source terms](data/README.md#data-attribution-and-terms).
