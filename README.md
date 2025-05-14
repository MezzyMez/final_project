# Data Science Bootcamp Final Project: Canadian CPI Analysis

## Project Overview
This project analyzes the drivers of the Canadian Consumer Price Index (CPI) using data from Statistics Canada. It includes data acquisition, cleaning, exploratory analysis, feature engineering, machine learning modeling, and visualization of key findings.

## Folder Structure
```
data/
    raw/           # Unmodified, original data downloads
    interim/       # Data after initial cleaning/processing
    processed/     # Final, analysis-ready datasets
    external/      # Any external datasets (macroeconomic, etc.)

notebooks/         # Jupyter/Colab notebooks for EDA, prototyping

src/               # All reusable code modules/scripts
    data/          # Data loading, cleaning, feature engineering
    models/        # Modeling, training, evaluation scripts
    visualization/ # Plotting and dashboard code
    utils.py       # Utility functions (to be added)

reports/           # Final reports, presentations, exported plots
    figures/       # All generated figures and plots

requirements.txt
README.md
.gitignore
main.py
```

## Workflow Steps
1. **Data Acquisition**
   - Scripts: `src/data/get_table_csv.py`, `src/data/contact_api.py`
   - Output: Raw data in `data/raw/`

2. **Data Cleaning & Processing**
   - Scripts: `src/data/explore.py`, `src/data/refine.py`
   - Output: Cleaned/interim data in `data/interim/`, final in `data/processed/`

3. **Exploratory Data Analysis (EDA)**
   - Notebooks: `notebooks/eda.ipynb`
   - Output: Insights, figures in `reports/figures/`

4. **Feature Engineering**
   - Scripts: `src/data/feature_engineering.py` (to be added)
   - Output: Feature datasets in `data/processed/`

5. **Modeling & Evaluation**
   - Scripts: `src/models/cpi_drivers_analysis.py`
   - Output: Model artifacts, evaluation metrics, plots in `reports/`

6. **Visualization & Communication**
   - Scripts: `src/visualization/` (to be added)
   - Output: Plots, dashboards in `reports/`

7. **Reporting**
   - Reports: `reports/final_report.pdf`, `reports/presentation.pptx` (to be added)

## Getting Started
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run data acquisition and processing scripts as needed.
3. Explore the data and results in notebooks and reports.

---

*Update this README as you add new analyses, models, or reports!*
