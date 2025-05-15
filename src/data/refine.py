import pandas as pd
import numpy as np

def process_cpi_data(input_file, output_file):
    # Read the CSV file
    df = pd.read_csv(input_file)
    
    # Pivot the data to create a wide format
    # Each row will be a (date, GEO), and each column will be a product group
    pivot_df = df.pivot(
        index=['REF_DATE', 'GEO'],
        columns='Products and product groups',
        values='VALUE'
    )
    
    # Reset index to make REF_DATE and GEO columns
    pivot_df = pivot_df.reset_index()
    
    # Save the processed data
    pivot_df.to_csv(output_file, index=False)
    print(f"Processed data saved to {output_file}")
    
    return pivot_df
