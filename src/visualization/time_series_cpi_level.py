import pandas as pd
import matplotlib.pyplot as plt
import os

def plot_cpi_level(processed_path, output_path):
    df = pd.read_csv(processed_path)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df_cpi = df[df['Products and product groups'] == 'All-items']
    plt.figure(figsize=(14, 6))
    plt.plot(pd.to_datetime(df_cpi['REF_DATE']), df_cpi['VALUE'], color='black', label='All-items (CPI)')
    plt.xlabel('Date')
    plt.ylabel('CPI Level')
    plt.title('Consumer Price Index (CPI) Level for All-items Over Time')
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"CPI level time series chart saved to {output_path}")

if __name__ == "__main__":
    plot_cpi_level(
        processed_path='data/processed/cpi_processed.csv',
        output_path='reports/figures/time_series_cpi_level.png'
    ) 
