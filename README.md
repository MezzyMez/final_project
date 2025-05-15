# Canadian CPI Analysis

## Project Overview
This project analyzes the drivers of the Canadian Consumer Price Index (CPI) using data from Statistics Canada. The workflow includes data acquisition, cleaning, exploratory analysis, feature engineering, machine learning modeling, and visualization of key findings.

## Folder Structure
```
data/
    raw/           # Unmodified, original data downloads
    processed/     # Final, analysis-ready datasets

notebooks/         # (Reserved for EDA or prototyping)

src/
    data/          # Data loading, cleaning, feature engineering scripts
    models/        # Modeling and analysis scripts
    visualization/ # Additional plotting and analysis scripts

reports/
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
   - Output: Cleaned and processed data in `data/processed/`

3. **Feature Engineering**
   - Script: `src/data/refine.py`
   - Output: Wide-format dataset in `data/processed/`

4. **Modeling, Evaluation & Visualization**
   - Scripts: `src/models/cpi_drivers_analysis.py` and all scripts in `src/visualization/` (all called by `main.py`)
   - Output: Model metrics, feature importances, anomaly detection, inverse correlation, and time series plots in `reports/figures/`

## Getting Started
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the full pipeline (all analyses and visualizations):
   ```bash
   python main.py
   ```
   - To skip data download and use existing data, add `--skip-download`:
     ```bash
     python main.py --skip-download
     ```
3. Review results in the `reports/figures/` directory.

---

This project and all analyses were completed by James McCulloch as part of Lighthouse Labs Data Science Bootcamp final project. All code, analysis, and documentation reflect my own work and learning.
