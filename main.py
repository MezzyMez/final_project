import argparse
from src.data.contact_api import fetch_stats_can_tables
from src.data.get_table_csv import download_table_csv
from src.data.explore import load_and_prepare_data, export_processed_data, describe_data
from src.data.refine import process_cpi_data
from src.models.cpi_drivers_analysis import run_cpi_drivers_analysis
import os

def main(skip_download=False):
    # 1. Data Acquisition
    if not skip_download:
        print("\n--- Fetching available tables from Statistics Canada API ---")
        fetch_stats_can_tables('data/raw/stats_can_available_tables.csv')

        print("\n--- Downloading main CPI table ---")
        # You may need to update this product_id to match the correct CPI table
        cpi_product_id = "18100004"
        cpi_csv_path = download_table_csv(cpi_product_id, output_dir='data/raw')
        if cpi_csv_path is None:
            print("Failed to download CPI data. Exiting.")
            return
    else:
        print("\n--- Skipping data download. Using existing data. ---")
        cpi_csv_path = 'data/raw/consumer_price_index_monthly_not_seasonally_adjusted.csv'
        if not os.path.exists(cpi_csv_path):
            print(f"CPI data file {cpi_csv_path} does not exist. Cannot proceed.")
            return

    # 2. Data Cleaning & Processing
    print("\n--- Cleaning and preparing CPI data ---")
    processed_df = load_and_prepare_data(cpi_csv_path)
    processed_path = 'data/processed/cpi_processed.csv'
    export_processed_data(processed_df, processed_path)
    describe_data(processed_df)

    # 3. Feature Engineering
    print("\n--- Pivoting data to wide format ---")
    wide_path = 'data/processed/cpi_wide_format.csv'
    process_cpi_data(processed_path, wide_path)

    # 4. Modeling & Evaluation
    print("\n--- Running CPI drivers analysis ---")
    run_cpi_drivers_analysis(wide_path)

    # 5. Additional Analyses & Visualizations
    print("\n--- Running anomaly detection analysis ---")
    from src.visualization.anomaly_detection import detect_anomalies
    detect_anomalies(
        processed_path=processed_path,
        output_path='reports/figures/anomalous_groups.png',
        z_thresh=3,
        top_n=10
    )

    print("\n--- Running inverse correlation analysis ---")
    from src.visualization.inverse_correlation_chart import plot_inverse_correlations
    plot_inverse_correlations(
        processed_path=processed_path,
        output_path='reports/figures/inverse_correlation_groups.png',
        top_n=10
    )

    print("\n--- Plotting CPI level time series ---")
    from src.visualization.time_series_cpi_level import plot_cpi_level
    plot_cpi_level(
        processed_path=processed_path,
        output_path='reports/figures/time_series_cpi_level.png'
    )

    print("\n--- Plotting time series comparison ---")
    from src.visualization.time_series_comparison import plot_time_series_comparison
    plot_time_series_comparison(
        processed_path=processed_path,
        output_path='reports/figures/time_series_recreational_vs_cpi.png',
        group_name='Purchase of recreational vehicles and outboard motors'
    )

    print("\nPipeline complete! Check the reports/figures directory for results.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the CPI analysis pipeline.")
    parser.add_argument('--skip-download', action='store_true', help='Skip data download and use existing data')
    args = parser.parse_args()
    main(skip_download=args.skip_download) 
