import pandas as pd
import requests
from datetime import datetime, timedelta, timezone

def generate_dashboard():
    wib_tz = timezone(timedelta(hours=7))
    now_wib = datetime.now(wib_tz)
    today_str = now_wib.strftime('%Y%m%d')
    
    URL = f"https://nb.ptgam.com/?hauling={today_str}&id=6f48a9b09bc4a0a83cd52e6b5a3c6d31c9fcff5a945add5721038fb201a8742a"
    
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(URL, headers=headers, timeout=15)
        response.raise_for_status()
        
        tables = pd.read_html(response.text)
        if not tables:
            print("No data available yet for today.")
            return
            
        df = tables[0]
        
        # Clean Netto and convert Kg to Tons
        df['Netto'] = pd.to_numeric(df['Netto'].astype(str).str.replace(',', ''), errors='coerce') / 1000
        
        total_trips = len(df)
        total_tonnage = df['Netto'].sum()
        
        driver_stats = df.groupby('Driver')['Netto'].sum().sort_values(ascending=False).head(5)
        top_unit_stats = df.groupby('DT Hauling')['Netto'].sum().sort_values(ascending=False).head(5)
        all_units_stats = df.groupby('DT Hauling').agg(
            Trips=('Netto', 'count'), Tonnage=('Netto', 'sum')
        ).sort_values(by='Tonnage', ascending=False)
        
        # Generate the HTML Webpage
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Hauling Pulse Dashboard</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; padding: 20px; background-color: #f4f4f9; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                h1 {{ font-size: 24px; color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; margin-top: 0; }}
                .timestamp {{ color: #7f8c8d; font-size: 14px; margin-bottom: 20px; font-weight: bold; }}
                .summary-box {{ background: #e8f4f8; padding: 15px; border-radius: 6px; margin-bottom: 20px; font-size: 18px; font-weight: bold; border-left: 5px solid #3498db; }}
                h2 {{ font-size: 18px; color: #2980b9; margin-top: 25px; border-bottom: 1px solid #eee; padding-bottom: 5px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 14px; }}
                th, td {{ text-align: left; padding: 10px 8px; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #f8f9fa; color: #555; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Hauling Operations Pulse</h1>
                <div class="timestamp">Last Updated: {now_wib.strftime('%Y-%m-%d %H:%M')} WIB</div>
                
                <div class="summary-box">
                    Total Trips: {total_trips}<br>
                    Total Tonnage: {total_tonnage:,.2f} Tons
                </div>
                
                <h2>Top 5 Drivers</h2>
                <table>
                    <tr><th>Driver</th><th>Tons</th></tr>
                    {''.join(f'<tr><td>{k}</td><td>{v:,.2f}</td></tr>' for k, v in driver_stats.items())}
                </table>

                <h2>Top 5 Units</h2>
                <table>
                    <tr><th>Unit</th><th>Tons</th></tr>
                    {''.join(f'<tr><td>{k}</td><td>{v:,.2f}</td></tr>' for k, v in top_unit_stats.items())}
                </table>

                <h2>All Units Status</h2>
                <table>
                    <tr><th>Unit</th><th>Trips</th><th>Tons</th></tr>
                    {''.join(f'<tr><td>{u}</td><td>{int(r["Trips"])}</td><td>{r["Tonnage"]:,.2f}</td></tr>' for u, r in all_units_stats.iterrows())}
                </table>
            </div>
        </body>
        </html>
        """
        
        # Save it directly to the root as index.html
        with open("index.html", "w") as f:
            f.write(html)
        print("Dashboard HTML successfully generated.")

    except Exception as e:
        print(f"DASHBOARD FAILURE: {e}")

if __name__ == "__main__":
    generate_dashboard()
