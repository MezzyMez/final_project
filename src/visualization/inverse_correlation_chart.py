import pandas as pd
import matplotlib.pyplot as plt
import os

def plot_inverse_correlations(processed_path, output_path, top_n=10):
    df = pd.read_csv(processed_path)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    pivot = df.pivot(index='REF_DATE', columns='Products and product groups', values='Rate_of_Change')
    pivot = pivot.dropna(axis=1, how='all')
    correlations = pivot.corr()['All-items'].sort_values()
    # Exclude 'All-items' itself
    correlations = correlations[correlations.index != 'All-items']
    top_inverse = correlations.head(top_n)
    plt.figure(figsize=(10, 6))
    plt.barh(top_inverse.index, top_inverse.values, color='seagreen')
    plt.xlabel('Correlation with All-items (CPI)')
    plt.title(f'Top {top_n} Product Groups Most Inversely Correlated with Inflation')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"Inverse correlation chart saved to {output_path}")

if __name__ == "__main__":
    plot_inverse_correlations(
        processed_path='data/processed/cpi_processed.csv',
        output_path='reports/figures/inverse_correlation_groups.png',
        top_n=10
    ) 
