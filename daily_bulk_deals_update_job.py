import pandas as pd
import numpy as np
from requests_html import HTMLSession

def save_bulk_csv_file():
    session = HTMLSession()
    url = "https://nsearchives.nseindia.com/content/equities/bulk.csv"

    # Make initial request to nseindia.com to set cookies
    session.get("https://www.nseindia.com", timeout=10)

    # Now make actual request
    response = session.get(url, timeout=10)

    if response.status_code == 200:
        with open("bulk.csv", "w", newline="", encoding="utf-8") as f:
            f.write(response.text)
        print("✅ Saved Bulk Deals to `bulk.csv`")
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







