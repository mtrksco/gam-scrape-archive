import pandas as pd
import requests
from datetime import datetime
import os

# Configuration
URL = "https://nb.ptgam.com/?hauling&id=6f48a9b09bc4a0a83cd52e6b5a3c6d31c9fcff5a945add5721038fb201a8742a"
CSV_FILE = "hauling_data_master.csv"

def extract_hauling_data():
    print(f"[{datetime.now()}] Initiating extraction for Kim...")
    try:
        # Standard headers to bypass basic vendor bot-blocking
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        response = requests.get(URL, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Pandas reads all HTML tables instantly
        tables = pd.read_html(response.text)
        
        if not tables:
            print("Critical: No tables detected in the DOM.")
            return
            
        # The main data is likely the first or largest table
        df = tables[0]
        
        # Validation: Ensure it's the right table before doing anything
        if 'No.Bontrip' not in df.columns:
            print("Critical: Table structure changed. Vendor may have updated the site.")
            return

        # Deduplication Logic
        if os.path.exists(CSV_FILE):
            existing_df = pd.read_csv(CSV_FILE)
            # Concat the new scrape with our master file
            combined_df = pd.concat([existing_df, df])
            # Keep only unique rows based on the receipt number 'No.Bontrip'
            final_df = combined_df.drop_duplicates(subset=['No.Bontrip'], keep='last')
        else:
            final_df = df
            
        final_df.to_csv(CSV_FILE, index=False)
        print(f"Success. Master archive safely updated. Total records: {len(final_df)}")
        
    except Exception as e:
        # If this fires, you need an alert immediately. 
        print(f"EXTRACTION FAILURE: {e}")

if __name__ == "__main__":
    extract_hauling_data()
