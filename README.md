# Unemployment Analysis in India — CodeAlpha Task 2

Professional exploratory data analysis completed as part of the CodeAlpha Data Science Internship. The project examines monthly unemployment, labour participation, regional variation, rural/urban differences, and the initial COVID-19 shock using the supplied India unemployment dataset.

## Key findings

The average unemployment rate increased from **9.51% before COVID-19** to **17.77% during March–June 2020**, an **86.9% increase**. The national monthly average peaked at **24.88% in May 2020**. Rural unemployment rose by approximately **99.9%** relative to its pre-COVID baseline, compared with **77.8%** in urban areas.

## Contents

- `src/analyze_unemployment.py`: reproducible cleaning, aggregation, analysis, and chart pipeline.
- `notebooks/unemployment_analysis.ipynb`: self-contained Kaggle-compatible notebook.
- `figures/`: professional trend, COVID comparison, regional ranking, regional change, and participation charts.
- `docs/ANALYSIS_REPORT.md`: executive analysis and policy implications.
- `docs/LINKEDIN_POST.md`: ready-to-publish LinkedIn post.
- `deck/Unemployment_Analysis_Project_Deck.pdf`: 8-slide presentation deck.
- `data_clean/`: cleaned CSV and summary metrics.

## Reproduce locally

```bash
python3 src/analyze_unemployment.py
```

The notebook expects the dataset to be attached in Kaggle or available in `data_raw/`. The uploaded source is CSV-formatted data with an `.xls` filename, so the pipeline reads it as UTF-8 CSV.

## Kaggle

Published notebook: https://www.kaggle.com/code/donblaze/unemployment-analysis-in-india-codealpha-task-2

The notebook was saved as a successful **Quick Save** version. Attach the supplied unemployment CSV/XLS dataset before running the code cell so its automatic `/kaggle/input` discovery can execute.

## Scope and limitations

This is descriptive analysis, not a causal estimate. The source ends in June 2020, which captures the initial COVID shock but not the full recovery. A stronger follow-up would extend the series, add sector-level GDP and wage data, and evaluate post-shock persistence.
