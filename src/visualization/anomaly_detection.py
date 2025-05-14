import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

def detect_anomalies(processed_path, output_path, z_thresh=3, top_n=10):
    # Load processed data
    df = pd.read_csv(processed_path)
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    # Calculate z-scores for each product group
    anomaly_counts = {}
    for group, group_df in df.groupby('Products and product groups'):
        # Drop NaNs for rate of change
        roc = group_df['Rate_of_Change'].dropna()
        if len(roc) < 2:
            continue
        z_scores = (roc - roc.mean()) / roc.std()
        n_anomalies = (np.abs(z_scores) > z_thresh).sum()
        anomaly_counts[group] = n_anomalies
    # Convert to DataFrame
    anomaly_df = pd.DataFrame(list(anomaly_counts.items()), columns=['Product Group', 'Anomaly Count'])
    anomaly_df = anomaly_df.sort_values('Anomaly Count', ascending=False).head(top_n)
    # Plot
    plt.figure(figsize=(12, 6))
    plt.barh(anomaly_df['Product Group'], anomaly_df['Anomaly Count'], color='tomato')
    plt.xlabel('Number of Anomalies (|z| > %d)' % z_thresh)
    plt.title(f'Top {top_n} Most Anomalous Product Groups')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"Anomaly chart saved to {output_path}")

if __name__ == "__main__":
    detect_anomalies(
        processed_path='data/processed/cpi_processed.csv',
        output_path='reports/figures/anomalous_groups.png',
        z_thresh=3,
        top_n=10
    ) 
