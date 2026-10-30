# Unemployment Analysis in India — CodeAlpha Task 2

## Executive summary

This analysis covers 740 cleaned monthly observations across 28 Indian regions from 2019-05-31 to 2020-06-30. The dataset shows a clear COVID-period labour-market shock: the mean estimated unemployment rate increased from **9.51%** before March 2020 to **17.77%** during March–June 2020, an increase of **86.9%**.

The highest national monthly average occurred in **2020-05**, at **24.88%**. **Tripura** had the highest average regional unemployment rate across the study period at **28.35%**.

## Data preparation

The uploaded file was labelled `.xls` but contains UTF-8 CSV data. It was read using `utf-8-sig`, stripped of the 28 blank records, parsed with day-first dates, and converted to a clean CSV. Numeric columns were explicitly coerced to numeric types. The resulting dataset has no blank rows and is saved at `data_clean/unemployment_clean.csv`.

## COVID-19 impact

The analysis defines the pre-COVID baseline as May 2019–February 2020 and the COVID shock window as March–June 2020. This is a descriptive before/after comparison, not a causal estimate: the dataset ends in June 2020 and does not control for region-specific economic structure, measurement changes, or other simultaneous shocks.

Urban unemployment increased from **10.84%** to **19.28%** (**77.8%**), while rural unemployment increased from **8.09%** to **16.18%** (**99.9%**). The monthly pattern shows the sharpest national stress in April and May 2020, followed by partial easing in June.

## Patterns and seasonality

- The series is monthly and short, so seasonal claims should be treated cautiously.
- The largest signal is a structural shock in spring 2020 rather than a stable recurring seasonal pattern.
- Regional dispersion is substantial: national averages conceal very different local labour-market outcomes.
- Rural and urban rates move together during the shock, but their levels and magnitude of change differ.
- Labour participation should be monitored alongside unemployment: a lower unemployment rate can coexist with weaker labour-market engagement if people leave the labour force.

## Policy implications

1. **Target emergency employment support geographically.** High-average and high-increase regions should receive priority for public works, wage support, and local job matching.
2. **Track rural and urban markets separately.** A single national rate can hide different transmission channels and recovery speeds.
3. **Pair unemployment with participation.** Monitoring both indicators helps distinguish job creation from labour-force withdrawal.
4. **Use high-frequency dashboards.** Monthly regional monitoring can identify renewed shocks earlier than annual statistics.
5. **Treat the results as descriptive evidence.** A causal policy evaluation would require longer pre-periods, post-period observations, controls, and a transparent identification strategy.

## Reproducibility

Run:

```bash
python src/analyze_unemployment.py
```

Charts are saved in `figures/`, cleaned data in `data_clean/`, and the notebook is in `notebooks/unemployment_analysis.ipynb`.
