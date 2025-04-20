import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

def load_and_prepare_data(file_path):
    """
    Load and prepare CPI data for analysis.
    Returns the filtered and processed DataFrame.
    """
    # Read the CSV file
    df = pd.read_csv(file_path)

    # Read the edited product groups and filter for valid products
    edited_products = pd.read_csv('data/processed/products_and_product_groups_edited.csv')
    valid_products = edited_products['Product Group'].tolist()
    df_filtered = df[df['Products and product groups'].isin(valid_products)]


    # Filter for desired columns values
    df_filtered = df_filtered[
        (df_filtered['UOM_ID'] == 17) 
        & (df_filtered['GEO'] == 'Canada') 
        & (df_filtered['Products and product groups'].isin(valid_products))
        & (df_filtered['SCALAR_ID'] == 0)
        & (df_filtered['REF_DATE'] >= '1949-01-01')
        ]
    

    # Drop undesired columns
    df_filtered = df_filtered.drop(columns=['DGUID', 'UOM', 'UOM_ID', 'STATUS', 'SYMBOL', 'TERMINATED', 'DECIMALS', 'VECTOR', 'COORDINATE', 'SCALAR_FACTOR', 'SCALAR_ID'])

    # Convert REF_DATE to datetime and sort
    df_filtered['REF_DATE'] = pd.to_datetime(df_filtered['REF_DATE'])
    df_filtered = df_filtered.sort_values('REF_DATE')

    # Calculate rate of change
    df_filtered['Rate_of_Change'] = df_filtered['VALUE'].pct_change() * 100

    return df_filtered

def export_processed_data(df, output_path):
    """
    Export the processed DataFrame to a CSV file.
    Creates the output directory if it doesn't exist.
    
    Args:
        df: Processed DataFrame to export
        output_path: Path where the CSV file will be saved
    """
    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Export to CSV with consistent quoting
    df.to_csv(output_path, index=False, quoting=0)
    print(f"\nProcessed data exported to: {output_path}")

def describe_data(df):
    """
    Print descriptive information about the CPI dataset.
    """
    print("\nBasic Information:")
    print(f"Number of rows: {len(df):,}")

    print("\nColumns and their data types:")
    print(df.dtypes)

    print("\nFirst few rows:")
    print(df.head(10))

    print("\nUnique values in key columns:")
    print("\nRef_date values (First 10):")
    print(df['REF_DATE'].unique()[:10])

    print("\nGEO values:")
    print(df['GEO'].unique())

    print("\nProducts and product groups:")

    # Clean the strings more thoroughly
    def clean_string(s):
        # Remove all types of quotes and strip whitespace
        return s.replace('"', '').replace("'", "").replace(",", "").replace("'", "").strip()

    unique_products = [clean_string(product) for product in df['Products and product groups'].unique()]
    df_products = pd.DataFrame(unique_products, columns=['Product Group'])
    df_products = df_products.sort_values('Product Group')  # Sort alphabetically
    
    print("\nCleaned and sorted products:")
    print(df_products)
    export_processed_data(df_products, 'data/processed/products_and_product_groups.csv')

    print("\nBasic statistics for VALUE column:")
    pd.set_option('display.float_format', lambda x: '{:,.2f}'.format(x))
    print(df['VALUE'].describe())

def plot_cpi_analysis(df):
    """
    Create interactive plots for CPI analysis.
    Returns the plotly figure object.
    """
    # Create figure with subplots
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=("Consumer Price Index Over Time",
                       "CPI Rate of Change (Monthly Percentage Change)"),
        vertical_spacing=0.1
    )

    # Add CPI value line plot
    fig.add_trace(
        go.Scatter(
            x=df['REF_DATE'], 
            y=df['VALUE'],
            name="CPI Value",
            hovertemplate="Date: %{x}<br>CPI: %{y:.2f}<extra></extra>"
        ),
        row=1, col=1
    )

    # Add rate of change bar plot
    fig.add_trace(
        go.Bar(
            x=df['REF_DATE'], 
            y=df['Rate_of_Change'],
            name="Rate of Change",
            hovertemplate="Date: %{x}<br>Change: %{y:.2f}%<extra></extra>",
            marker_color=['red' if x < 0 else 'green' for x in df['Rate_of_Change']]
        ),
        row=2, col=1
    )

    # Add horizontal line at y=0 for rate of change
    fig.add_hline(y=0, line_dash="dash", line_color="gray", row=2, col=1)

    # Update layout
    fig.update_layout(
        height=1200,
        showlegend=True,
        hovermode='x unified',
        bargap=0.1,
        margin=dict(t=50, b=50)
    )

    # Update axes
    fig.update_yaxes(title_text="CPI Value", row=1, col=1)
    fig.update_yaxes(title_text="Percentage Change (%)", row=2, col=1)
    fig.update_xaxes(title_text="Date", row=2, col=1)

    return fig

def main():
    # File paths
    input_file = 'data/raw/consumer_price_index_monthly_not_seasonally_adjusted.csv'
    output_file = 'data/processed/cpi_processed.csv'
    
    # Load and prepare data
    df = load_and_prepare_data(input_file)
    
    # Export processed data
    export_processed_data(df, output_file)
    
    # Describe the data
    describe_data(df)
    
    # Create and show the plots
    # fig = plot_cpi_analysis(df)
    # fig.show()

if __name__ == "__main__":
    main()
