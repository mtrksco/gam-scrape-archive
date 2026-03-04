import pandas as pd
import requests
from datetime import datetime, timedelta, timezone
import os

def extract_yesterdays_hauling():
    # Force the script to calculate based on Indonesia time (WIB = UTC+7)
    wib_tz = timezone(timedelta(hours=7))
    now_wib = datetime.now(wib_tz)
    
    # We are scraping at 7:15 AM, so we want the finalized data from yesterday
    target_date = now_wib - timedelta(days=1)
    
    # Format dates for the URL and the filename
    url_date = target_date.strftime('%Y%m%d')
    file_date = target_date.strftime('%Y-%m-%d')

    # NEW: Define the folder and ensure it exists
    folder_name = "archive"
    os.makedirs(folder_name, exist_ok=True)
    
    URL = f"https://nb.ptgam.com/?hauling={url_date}&id=6f48a9b09bc4a0a83cd52e6b5a3c6d31c9fcff5a945add5721038fb201a8742a"
    filename = f"{folder_name}/hauling_data_{file_date}.csv"

    print(f"[{now_wib}] Initiating extraction for Kim. Target Date: {file_date}")
    
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(URL, headers=headers, timeout=15)
        response.raise_for_status()
        
        tables = pd.read_html(response.text)
        if not tables:
            print("Critical: No tables detected. They may not have operated this day.")
            return
            
        df = tables[0]
        
        # Save directly. No appending needed since we pull the whole day at once.
        df.to_csv(filename, index=False)
        print(f"Success. Saved to {filename}. Total records: {len(df)}")
        
    except Exception as e:
        print(f"EXTRACTION FAILURE: {e}")

if __name__ == "__main__":
    extract_yesterdays_hauling()
