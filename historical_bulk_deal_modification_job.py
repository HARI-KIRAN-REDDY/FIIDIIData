import numpy as np
import pandas as pd
import requests
from io import StringIO


URL = "https://raw.githubusercontent.com/HARI-KIRAN-REDDY/FIIDIIData/main/historical_bulk.csv"
THRESHOLD = 2_00_00_000  # 2 Cr


response = requests.get(URL,  timeout=10)
response.raise_for_status()
df = pd.read_csv(StringIO(response.text))


df['Quantity Traded'] = np.where(df['Buy/Sell'] == 'BUY',
                                 df['Quantity Traded'],
                                 -df['Quantity Traded'])
df['net_value'] = np.where(df['Buy/Sell'] == 'BUY',
                           df['Trade Price / Wght. Avg. Price']*df["Quantity Traded"],
                           -df['Trade Price / Wght. Avg. Price']*df["Quantity Traded"])

# NET_VALUE per Date + Symbol + Client Name
df = df.groupby(["Date", "Symbol", "Client Name"])['net_value'].sum().reset_index()

# filter by threshold
df = df[df["net_value"].abs() >= THRESHOLD]
df['action'] = np.where(df["net_value"] > 0, 'BUY', 'SELL')


df.to_csv('modified_historical_bulk_deals.csv', index=False)

