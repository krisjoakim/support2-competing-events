# Original reported results

These results are transcribed from the preserved notebook outputs and the original 2024 report. The 2026 repository revisit did not retrain, retune, or replace any model.

## Validation comparison

| Model | Original training data RMSE | Outlier-handled training data RMSE |
| --- | ---: | ---: |
| Dummy Regressor | 19.65 | 19.65 |
| Decision Tree Regressor | 18.45 | 18.45 |
| Lasso | 18.17 | 18.16 |
| Gradient Boosting Regressor | 17.83 | **17.59** |

The selected model was a `GradientBoostingRegressor` with 300 estimators, maximum depth 3, minimum samples per split 5, minimum samples per leaf 4, subsample 0.8, early stopping, and `random_state=42`.

## Held-out evaluation

After selection, the final model achieved a held-out test RMSE of **16.5715 days**, reported as approximately **16.57 days**.

## Error analysis

For test predictions with an absolute error above 30 days:

- median actual length of stay: 69 days;
- median predicted length of stay: 23.85329 days; and
- median signed error: -45.14671 days.

For predictions with an absolute error of at most three days, the median actual and predicted stays were 12 and 11.86691 days respectively. The contrast shows that the model handled typical stays much better than unusually long stays, which it often underestimated substantially.
