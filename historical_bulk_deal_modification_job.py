import numpy as np
import pandas as pd
import requests
from io import StringIO


URL = "https://raw.githubusercontent.com/HARI-KIRAN-REDDY/FIIDIIData/main/historical_bulk.csv"
THRESHOLD = 20000000  # 2 Cr


response = requests.get(URL,  timeout=10)
response.raise_for_status()
df = pd.read_csv(StringIO(response.text))


df['Quantity Traded'] = df['Quantity Traded'].astype(int)
df['Trade Price / Wght. Avg. Price'] = df['Trade Price / Wght. Avg. Price'].astype(int)

df['quantity_traded'] = np.where(df['Buy/Sell'] == 'BUY',
                                 df['Quantity Traded'],
                                 -df['Quantity Traded'])
df['net_value'] = df['quantity_traded']*df['Trade Price / Wght. Avg. Price']

# NET_VALUE per Date + Symbol + Client Name
df = df.groupby(["Date", "Symbol", "Client Name"])[['net_value', 'quantity_traded']].sum().reset_index()

# filter by threshold
df = df[df["net_value"].abs() >= THRESHOLD]
df['action'] = np.where(df["net_value"] > 0, 'BUY', 'SELL')
df['date_to_sort'] = pd.to_datetime(df['Date'], format='%d-%b-%y')
df = df.sort_values(by=['date_to_sort'])

df.to_csv('modified_historical_bulk_deals.csv', index=False)




