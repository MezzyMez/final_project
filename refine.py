import pandas as pd
import numpy as np

def process_cpi_data(input_file, output_file):
    # Read the CSV file
    df = pd.read_csv(input_file)
    
    # Pivot the data to create a wide format
    # Each row will be a date, and each column will be a product group
    pivot_df = df.pivot(
        index='REF_DATE',
        columns='Products and product groups',
        values='VALUE'
    )
    
    # Reset index to make REF_DATE a column
    pivot_df = pivot_df.reset_index()
    
    # Save the processed data
    pivot_df.to_csv(output_file, index=False)
    print(f"Processed data saved to {output_file}")
    
    return pivot_df

if __name__ == "__main__":
    input_file = "data/processed/cpi_processed.csv"
    output_file = "data/processed/cpi_wide_format.csv"
    
    processed_df = process_cpi_data(input_file, output_file)
    print("\nDataFrame shape:", processed_df.shape)
    print("\nFirst few rows of processed data:")
    print(processed_df.head())
