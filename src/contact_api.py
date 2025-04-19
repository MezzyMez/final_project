import requests
import json
import pandas as pd
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def contactStatsCanAPI(endpoint, payload={}):
    """
    Fetches all available tables from Statistics Canada API and returns a DataFrame
    containing productId, cansimId, and cubeTitleEn.
    
    Returns:
        pandas.DataFrame: DataFrame containing the selected columns from the API response
    """
    # Base URL for Statistics Canada API
    base_url = "https://www150.statcan.gc.ca/t1/wds/rest"
    url = f"{base_url}/{endpoint}"
    
    try:
        print(f"Making request to: {url}")
        # Disable SSL verification for testing
        response = requests.get(url, json=payload, verify=False)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            # Convert response to DataFrame
            data = response.json()
            df = pd.DataFrame(data)
                   
            return df
            
        else:
            print(f"Error: Received status code {response.status_code}")
            print("Response content:", response.text)
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None
    except ValueError as e:
        print(f"Failed to parse JSON: {e}")
        print("Raw response:", response.text)
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        print("Response content:", response.text if 'response' in locals() else "No response available")
        return None

if __name__ == "__main__":
    # Example usage
    tables_df = contactStatsCanAPI("getAllCubesListLite")
    if tables_df is not None:
        print("\nDataFrame Info:")
        print(tables_df.info())

        # Select only the desired columns
        selected_columns = ['productId', 'cansimId', 'cubeTitleEn']
        df_selected = tables_df[selected_columns]

        print("\nFirst few rows:")
        print(tables_df.head(20))

        # Save the dataframe to a csv file
        tables_df.to_csv('../data/raw/stats_can_available_tables.csv', index=False)
        print("\nData saved to 'stats_can_available_tables.csv'")

