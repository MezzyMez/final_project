import pandas as pd
import matplotlib.pyplot as plt
import os

def plot_time_series_comparison(processed_path, output_path, group_name, start_year=None, end_year=None):
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
    # Optionally filter by year range
    if start_year is not None:
        merged = merged[merged['REF_DATE'] >= f'{start_year}-01-01']
    if end_year is not None:
        merged = merged[merged['REF_DATE'] <= f'{end_year}-12-31']
    # Plot
    plt.figure(figsize=(14, 6))
    dates = pd.to_datetime(merged['REF_DATE'])
    diff = merged['Rate_of_Change_Group'] - merged['Rate_of_Change_CPI']
    # Bar plot for the difference (drawn first, with a more visible color and width)
    highlight_thresh = 2  # percent
    highlight_pos = (diff > highlight_thresh)
    highlight_neg = (diff < -highlight_thresh)
    # Default bars
    plt.bar(
        dates[~(highlight_pos | highlight_neg)], diff[~(highlight_pos | highlight_neg)],
        color='orange', alpha=0.8, width=20, zorder=1, label=f'Difference ({group_name} - All-items)'
    )
    # Highlight positive differences
    plt.bar(
        dates[highlight_pos], diff[highlight_pos],
        color='red', alpha=0.8, width=20, zorder=1, label='Diff > +2%'
    )
    # Highlight negative differences
    plt.bar(
        dates[highlight_neg], diff[highlight_neg],
        color='blue', alpha=0.8, width=20, zorder=1, label='Diff < -2%'
    )
    # Line plots (drawn on top)
    plt.plot(dates, merged['Rate_of_Change_CPI'], label='All-items (CPI)', color='black', zorder=2)
    plt.plot(dates, merged['Rate_of_Change_Group'], label=group_name, color='seagreen', zorder=2)
    plt.axhline(0, color='gray', linestyle='--', linewidth=1)
    plt.xlabel('Date')
    plt.ylabel('Monthly Rate of Change (%)')
    plt.title(f"Rate of Change: All-items (CPI) vs. {group_name}")
    plt.legend()
    # Annotate largest positive/negative difference
    if len(diff) > 0:
        max_idx = diff.idxmax()
        min_idx = diff.idxmin()
        plt.annotate(f"{diff[max_idx]:.1f}%", (dates[max_idx], diff[max_idx]),
                     textcoords="offset points", xytext=(0,10), ha='center', color='red', fontsize=9, fontweight='bold')
        plt.annotate(f"{diff[min_idx]:.1f}%", (dates[min_idx], diff[min_idx]),
                     textcoords="offset points", xytext=(0,-15), ha='center', color='blue', fontsize=9, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"Time series comparison chart saved to {output_path}")

if __name__ == "__main__":
    # Example: plot the last 10 years
    plot_time_series_comparison(
        processed_path='data/processed/cpi_processed.csv',
        output_path='reports/figures/time_series_recreational_vs_cpi.png',
        group_name='Purchase of recreational vehicles and outboard motors',
        start_year=2014,
        end_year=2023
    ) 
