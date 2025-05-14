import pandas as pd
import matplotlib.pyplot as plt
import os

def plot_time_series_comparison(processed_path, output_path, group_name):
    df = pd.read_csv(processed_path)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    # Filter for the two groups
    df_cpi = df[df['Products and product groups'] == 'All-items']
    df_group = df[df['Products and product groups'] == group_name]
    # Merge on REF_DATE
    merged = pd.merge(df_cpi[['REF_DATE', 'Rate_of_Change']],
                      df_group[['REF_DATE', 'Rate_of_Change']],
                      on='REF_DATE',
                      suffixes=('_CPI', '_Group'))
    # Plot
    plt.figure(figsize=(14, 6))
    plt.plot(pd.to_datetime(merged['REF_DATE']), merged['Rate_of_Change_CPI'], label='All-items (CPI)', color='black')
    plt.plot(pd.to_datetime(merged['REF_DATE']), merged['Rate_of_Change_Group'], label=group_name, color='seagreen')
    plt.axhline(0, color='gray', linestyle='--', linewidth=1)
    plt.xlabel('Date')
    plt.ylabel('Monthly Rate of Change (%)')
    plt.title(f"Rate of Change: All-items (CPI) vs. {group_name}")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"Time series comparison chart saved to {output_path}")

if __name__ == "__main__":
    plot_time_series_comparison(
        processed_path='data/processed/cpi_processed.csv',
        output_path='reports/figures/time_series_recreational_vs_cpi.png',
        group_name='Purchase of recreational vehicles and outboard motors'
    ) 
