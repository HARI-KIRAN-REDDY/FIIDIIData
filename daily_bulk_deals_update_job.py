import pandas as pd
import numpy as np
import requests

def save_bulk_csv_file():
    # Set URL for bulk deals
    url = "https://nsearchives.nseindia.com/content/equities/bulk.csv"

    # Set headers to mimic browser
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "text/csv",
        "Referer": "https://www.nseindia.com/market-data/large-deals",
        "Origin": "https://www.nseindia.com",
        "X-Requested-With": "XMLHttpRequest",
    }

    response = requests.get(url, headers=headers, timeout=10)

    if response.status_code == 200:
        filename = f"bulk.csv"
        with open(filename, "w", newline="", encoding="utf-8") as f:
            f.write(response.text)
        print(f"✅ Saved Bulk Deals to `{filename}`")
    else:
        print(f"❌ Request failed: {response.status_code}")
        print("Response:", response.text)


def prepare_data():
    df = pd.read_csv("bulk.csv")
    df.columns = df.columns.str.strip()


    df['Price'] = df['Trade Price / Wght. Avg. Price']
    df['Quantity'] = df['Quantity Traded']

    df['Trade Value'] = np.where(df['Buy/Sell'] == 'BUY',
                                 df['Price'] * df['Quantity'],
                                 df['Price'] * df['Quantity']*-1)/10000000

    result = round(df.groupby('Symbol', as_index=False)['Trade Value'].sum(),2)

    result[result['Trade Value']>=2].to_csv('bulk.csv', index = False)

save_bulk_csv_file()
prepare_data()
