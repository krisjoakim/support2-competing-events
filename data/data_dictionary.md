# SUPPORT2 data dictionary

This reference covers all 48 variables returned by `fetch_ucirepo(id=880)`. Definitions draw on the [UCI SUPPORT2 record](https://archive.ics.uci.edu/dataset/880/support2), the [Vanderbilt SUPPORT description](https://hbiostat.org/data/repo/supportdesc), and the [Vanderbilt variable labels](https://hbiostat.org/data/repo/csupport2). Source-level missingness is calculated from all 9,105 records retrieved on 13 September 2026. Where the source does not document a unit or exact timing, that limitation is stated rather than inferred.

The candidate pool contains 20 numeric and 8 categorical variables. Race, years of education, and income category are included as baseline sociodemographic candidates by project design; their exact collection timing is not stated in the available source metadata. Outcomes, follow-up fields, post-prediction resource use, care-process fields with problematic timing, existing prognostic estimates, and two deliberately excluded constructed or derived fields remain outside the pool.

`SUPPORT2 variable` is the authoritative UCI source identifier. `Project name` is the one-to-one snake-case name used in notebook working data frames. This pairing provides bidirectional traceability without changing source values.

## Identifiers and outcomes

| SUPPORT2 variable | Project name | Meaning | Type / unit | Timing | Missingness | Candidate predictor? | Project role / exclusion |
| --- | --- | --- | --- | --- | ---: | --- | --- |
| `id` | `patient_id` | Record identifier | Integer | Not specified | 0 (0.0%) | No | Deterministic split and record checks |
| `death` | `death_during_follow_up` | Death during available National Death Index follow-up | Binary | Follow-up | 0 (0.0%) | No | Later-mortality outcome |
| `hospdead` | `in_hospital_death` | Death during hospital stay | Binary | Hospital exit | 0 (0.0%) | No | Defines competing exit type |
| `slos` | `days_to_hospital_exit` | Days from study entry to hospital exit | Days | Study entry to exit | 0 (0.0%) | No | Defines exit time |
| `d.time` | `follow_up_days` | Follow-up time | Days | Follow-up | 0 (0.0%) | No | Endpoint investigation only |

## Demographics and socioeconomic fields

| SUPPORT2 variable | Project name | Meaning | Type / unit | Timing | Missingness | Candidate predictor? | Project role / exclusion |
| --- | --- | --- | --- | --- | ---: | --- | --- |
| `age` | `age` | Patient age | Continuous; years | Study entry | 0 (0.0%) | Eligible | Patient context |
| `sex` | `sex` | Recorded sex | Categorical | Study entry | 0 (0.0%) | Eligible | Patient context |
| `race` | `race` | Recorded race | Categorical | Not specified | 42 (0.5%) | Eligible | Baseline sociodemographic candidate; exact collection timing is not documented |
| `edu` | `years_of_education` | Years of education | Continuous; years | Not specified | 1,634 (17.9%) | Eligible | Baseline sociodemographic candidate; exact collection timing is not documented |
| `income` | `income_category` | Recorded income category | Categorical; period not specified | Not specified | 2,982 (32.8%) | Eligible | Baseline sociodemographic candidate; exact collection timing is not documented |

## Diagnosis and comorbidity

| SUPPORT2 variable | Project name | Meaning | Type / unit | Timing | Missingness | Candidate predictor? | Project role / exclusion |
| --- | --- | --- | --- | --- | ---: | --- | --- |
| `dzgroup` | `diagnosis_group` | Disease subgroup | Categorical | Study entry | 0 (0.0%) | Eligible | Diagnosis context |
| `dzclass` | `diagnosis_class` | Broad disease class | Categorical | Study entry | 0 (0.0%) | Eligible | Diagnosis context |
| `num.co` | `number_of_comorbidities` | Number of simultaneous diseases or comorbidities | Count | Study entry | 0 (0.0%) | Eligible | Comorbidity burden |
| `diabetes` | `diabetes` | Diabetes comorbidity | Binary | Study entry | 0 (0.0%) | Eligible | Comorbidity |
| `dementia` | `dementia` | Dementia comorbidity | Binary | Study entry | 0 (0.0%) | Eligible | Comorbidity |
| `ca` | `cancer_status` | Cancer status, including metastatic status | Categorical | Study entry | 0 (0.0%) | Eligible | Cancer context |

## Hospital and study timing

| SUPPORT2 variable | Project name | Meaning | Type / unit | Timing | Missingness | Candidate predictor? | Project role / exclusion |
| --- | --- | --- | --- | --- | ---: | --- | --- |
| `hday` | `hospital_day_at_study_entry` | Hospital day at SUPPORT study entry | Days | Study entry | 0 (0.0%) | Eligible | Hospital context |

## Physiological and laboratory measurements

These measurements are recorded around SUPPORT day 3 according to the Vanderbilt labels. Units appear only where source documentation states them.

| SUPPORT2 variable | Project name | Meaning | Type / unit | Timing | Missingness | Candidate predictor? | Project role / exclusion |
| --- | --- | --- | --- | --- | ---: | --- | --- |
| `scoma` | `support_coma_score` | SUPPORT coma score based on Glasgow assessment | Score; scale not specified | Day 3 | 1 (0.0%) | No | Constructed clinical score excluded by project scope in favour of more direct patient measurements; not outcome leakage |
| `meanbp` | `mean_arterial_pressure` | Mean arterial blood pressure | Continuous; unit not specified | Day 3 | 1 (0.0%) | Eligible | Physiological measurement |
| `wblc` | `white_blood_cell_count` | White blood cell count | Continuous; thousands in source | Day 3 | 212 (2.3%) | Eligible | Laboratory measurement |
| `hrt` | `heart_rate` | Heart rate | Continuous; unit not specified | Day 3 | 1 (0.0%) | Eligible | Physiological measurement |
| `resp` | `respiratory_rate` | Respiratory rate | Continuous; unit not specified | Day 3 | 1 (0.0%) | Eligible | Physiological measurement |
| `temp` | `temperature` | Temperature | Continuous; degrees Celsius | Day 3 | 1 (0.0%) | Eligible | Physiological measurement |
| `pafi` | `pao2_fio2_ratio` | PaO2 divided by 0.01 × FiO2 | Continuous ratio | Day 3 | 2,325 (25.5%) | Eligible | Physiological measurement |
| `alb` | `albumin` | Serum albumin | Continuous; unit not specified | Day 3 | 3,372 (37.0%) | Eligible | Laboratory measurement |
| `bili` | `bilirubin` | Bilirubin | Continuous; unit not specified | Day 3 | 2,601 (28.6%) | Eligible | Laboratory measurement |
| `crea` | `creatinine` | Serum creatinine | Continuous; unit not specified | Day 3 | 67 (0.7%) | Eligible | Laboratory measurement |
| `sod` | `sodium` | Serum sodium | Continuous; unit not specified | Day 3 | 1 (0.0%) | Eligible | Laboratory measurement |
| `ph` | `arterial_ph` | Arterial serum pH | Continuous pH scale | Day 3 | 2,284 (25.1%) | Eligible | Laboratory measurement |
| `glucose` | `glucose` | Glucose | Continuous; unit not specified | Day 3 | 4,500 (49.4%) | Eligible | Laboratory measurement |
| `bun` | `blood_urea_nitrogen` | Blood urea nitrogen | Continuous; unit not specified | Day 3 | 4,352 (47.8%) | Eligible | Laboratory measurement |
| `urine` | `urine_output` | Urine output | Continuous; unit and interval not specified | Day 3 | 4,862 (53.4%) | Eligible | Clinical measurement |

## Functional status

| SUPPORT2 variable | Project name | Meaning | Type / unit | Timing | Missingness | Candidate predictor? | Project role / exclusion |
| --- | --- | --- | --- | --- | ---: | --- | --- |
| `adlp` | `adl_patient_reported` | Patient-reported activities-of-daily-living measure | Score; scale not specified | Day 3 | 5,641 (62.0%) | Eligible | Functional status |
| `adls` | `adl_surrogate_reported` | Surrogate-reported activities-of-daily-living measure | Score; scale not specified | Day 3 | 2,867 (31.5%) | Eligible | Functional status |
| `sfdm2` | `two_month_functional_disability` | Two-month functional-disability outcome | Ordinal; 5 levels | Two months after study entry | 1,400 (15.4%) | No | Follow-up outcome |
| `adlsc` | `imputed_adl_score` | ADL measure calibrated to surrogate information | Score; scale not specified | Not specified | 0 (0.0%) | No | Derived/imputed ADL representation excluded by project scope while direct patient- and surrogate-reported ADL measures are retained; not outcome leakage |

## Costs and resource use

| SUPPORT2 variable | Project name | Meaning | Type / unit | Timing | Missingness | Candidate predictor? | Project role / exclusion |
| --- | --- | --- | --- | --- | ---: | --- | --- |
| `charges` | `hospital_charges` | Hospital charges | Continuous; currency not specified | Hospital stay | 172 (1.9%) | No | Post-outcome resource use |
| `totcst` | `total_rcc_cost` | Total RCC cost | Continuous; currency not specified | Hospital stay | 888 (9.8%) | No | Post-outcome resource use |
| `totmcst` | `total_micro_cost` | Total micro-cost | Continuous; currency not specified | Hospital stay | 3,475 (38.2%) | No | Post-outcome resource use |
| `avtisst` | `average_tiss_score` | Average Therapeutic Intervention Scoring System | Score | Days 3–25 | 82 (0.9%) | No | Includes post-prediction information |

## Existing scores and survival estimates

| SUPPORT2 variable | Project name | Meaning | Type / unit | Timing | Missingness | Candidate predictor? | Project role / exclusion |
| --- | --- | --- | --- | --- | ---: | --- | --- |
| `sps` | `support_physiology_score` | SUPPORT day-3 physiology score | Score | Day 3 | 1 (0.0%) | No | Existing prognostic score |
| `aps` | `apache_iii_physiology_score` | APACHE III day-3 physiology score | Score | Day 3 | 1 (0.0%) | No | Existing prognostic score |
| `surv2m` | `support_2_month_survival_estimate` | SUPPORT two-month survival estimate | Probability; scale not specified | Day 3 | 1 (0.0%) | No | Existing model estimate |
| `surv6m` | `support_6_month_survival_estimate` | SUPPORT six-month survival estimate | Probability; scale not specified | Day 3 | 1 (0.0%) | No | Existing model estimate |
| `prg2m` | `physician_2_month_survival_estimate` | Physician two-month survival estimate | Probability; scale not specified | Not specified | 1,649 (18.1%) | No | Physician prediction |
| `prg6m` | `physician_6_month_survival_estimate` | Physician six-month survival estimate | Probability; scale not specified | Not specified | 1,633 (17.9%) | No | Physician prediction |

## Care process and DNR fields

| SUPPORT2 variable | Project name | Meaning | Type / unit | Timing | Missingness | Candidate predictor? | Project role / exclusion |
| --- | --- | --- | --- | --- | ---: | --- | --- |
| `dnr` | `dnr_status` | DNR status | Categorical | Relative to study admission | 30 (0.3%) | No | Care-process information |
| `dnrday` | `days_to_dnr_order` | Days to DNR order; negative indicates before study | Days | Relative to study entry | 30 (0.3%) | No | Care-process information |

## Documentation notes

The UCI record presents `id` plus 47 non-identifier variables. Missingness is descriptive source-level information, not a criterion for automatic deletion. The current published files omit source-data tables and patient identifiers; illustrative individual prediction curves are retained. Notebook 05’s patient-context table is omitted from saved outputs but reappears when its final plotting cell is run. See [data publication notes](README.md) for handling outputs and earlier Git history. Source documentation remains authoritative for field definitions and collection details.
