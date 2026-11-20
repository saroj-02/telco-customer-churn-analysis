# Cleaning Log

1. Renamed all columns to snake_case
2. Converted total_charges to numeric; blanks became NaN
3. Filled 11 missing total_charges with 0 (tenure = 0)
4. Removed 0 duplicate rows
5. Converted categorical columns to category dtype; added churn_flag (1/0)
6. IQR check on tenure: 0 outliers outside [-60.0, 124.0] - kept (valid customers)
7. IQR check on monthly_charges: 0 outliers outside [-46.0, 171.4] - kept (valid customers)
8. IQR check on total_charges: 0 outliers outside [-4683.5, 8868.7] - kept (valid customers)
9. Saved cleaned data: 7043 rows x 22 columns