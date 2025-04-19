import requests
import pandas as pd
import urllib3
from io import StringIO, BytesIO
import json
import zipfile
import re
import os

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def to_snake_case(name):
    """Convert a string to snake_case."""
    # Replace spaces and special characters with underscores
    name = re.sub(r'[^a-zA-Z0-9\s]', '', name)
    # Convert to lowercase and replace spaces with underscores
    return '_'.join(name.lower().split())

def get_table_name(product_id):
    """Look up the table name from the available tables CSV."""
    try:
        # Read the available tables CSV
        print(f"\nLooking up table name for product_id: {product_id}")
        tables_df = pd.read_csv('data/raw/stats_can_available_tables.csv')
        print(f"Available columns in CSV: {tables_df.columns.tolist()}")
        
        # Convert product_id to string for comparison
        product_id = str(product_id)
        print(f"Product ID type: {type(product_id)}")
        print(f"CSV productId type: {tables_df['productId'].dtype}")
        
        # Convert CSV productId to string
        tables_df['productId'] = tables_df['productId'].astype(str)
        
        # Find the row with matching productId
        table_info = tables_df[tables_df['productId'] == product_id]
        print(f"Found {len(table_info)} matching rows")
        
        if not table_info.empty:
            table_name = table_info['cubeTitleEn'].iloc[0]
            print(f"Found table name: {table_name}")
            return table_name
        else:
            print("No matching table found")
            # Print first few productIds from CSV for debugging
            print("First few productIds in CSV:")
            print(tables_df['productId'].head())
            return None
    except Exception as e:
        print(f"Error looking up table name: {e}")
        print(f"Error type: {type(e)}")
        return None

def getTableCSV(product_id, language="en"):
    """
    Downloads a specific table's CSV data from Statistics Canada.
    
    Args:
        product_id (str): The product ID of the table to download
        language (str): The language code (default: "en" for English)
    
    Returns:
        pandas.DataFrame: DataFrame containing the table data
    """
    try:
        # Get the table name
        table_name = get_table_name(product_id)
        if table_name:
            print(f"Found table: {table_name}")
        
        # Construct the API URL
        api_url = f"https://www150.statcan.gc.ca/t1/wds/rest/getFullTableDownloadCSV/{product_id}/{language}"
        print(f"Requesting URL: {api_url}")
        
        # Make the API request
        response = requests.get(api_url, verify=False)
        print(f"Status Code: {response.status_code}")
        
        response.raise_for_status()  # Raise an error for bad status codes
        
        # Parse the JSON response to get the download URL
        download_info = response.json()
        print("\nParsed JSON Response:")
        print(json.dumps(download_info, indent=2))
        
        # Get the ZIP file URL from the 'object' field
        zip_url = download_info.get('object')
        
        if not zip_url:
            print("Error: No download URL found in response")
            return None
            
        # Download the ZIP file
        print(f"\nDownloading ZIP from: {zip_url}")
        zip_response = requests.get(zip_url, verify=False)
        zip_response.raise_for_status()
        
        # Extract CSV from ZIP
        with zipfile.ZipFile(BytesIO(zip_response.content)) as z:
            # Get the first CSV file in the ZIP
            csv_filename = [f for f in z.namelist() if f.endswith('.csv')][0]
            with z.open(csv_filename) as f:
                # Load the CSV data into a pandas DataFrame
                df = pd.read_csv(f)
                return df, table_name
        
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None, None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None, None

if __name__ == "__main__":
    # Example usage
    product_id = "18100004"
    df, table_name = getTableCSV(product_id)
    
    if df is not None:
        print("\nDataFrame Info:")
        print(df.info())
        print("\nFirst few rows:")
        print(df.head())
        
        # Create output filename using table name if available
        if table_name:
            output_file = f"data/raw/{to_snake_case(table_name)}.csv"
        else:
            output_file = f"data/raw/table_{product_id}.csv"
            
        df.to_csv(output_file, index=False)
        print(f"\nData saved to {output_file}")
