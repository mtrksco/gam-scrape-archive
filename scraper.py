import pandas as pd
import requests
from datetime import datetime
import os

URL = "https://nb.ptgam.com/?hauling&id=6f48a9b09bc4a0a83cd52e6b5a3c6d31c9fcff5a945add5721038fb201a8742a"

def extract_hauling_data():
    print(f"[{datetime.now()}] Initiating extraction for Kim...")
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(URL, headers=headers, timeout=15)
        response.raise_for_status()
        
        tables = pd.read_html(response.text)
        if not tables:
            print("Critical: No tables detected.")
            return
            
        df = tables[0]
        if 'No.Bontrip' not in df.columns or 'Tanggal' not in df.columns:
            print("Critical: Table structure changed.")
            return

        # Extract the actual date from the first row of the Tanggal column
        actual_date = pd.to_datetime(df['Tanggal'].iloc[0]).strftime('%Y-%m-%d')
        csv_filename = f"hauling_data_{actual_date}.csv"

        if os.path.exists(csv_filename):
            existing_df = pd.read_csv(csv_filename)
            combined_df = pd.concat([existing_df, df])
            final_df = combined_df.drop_duplicates(subset=['No.Bontrip'], keep='last')
        else:
            final_df = df
            
        final_df.to_csv(csv_filename, index=False)
        print(f"Success. Saved to {csv_filename}. Total records: {len(final_df)}")
        
    except Exception as e:
        print(f"EXTRACTION FAILURE: {e}")

if __name__ == "__main__":
    extract_hauling_data()
