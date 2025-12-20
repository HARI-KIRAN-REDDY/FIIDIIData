import numpy as np
import pandas as pd
import requests
from io import StringIO


URL = "https://raw.githubusercontent.com/HARI-KIRAN-REDDY/FIIDIIData/main/historical_bulk.csv"
THRESHOLD = 2_00_00_000  # 2 Cr


response = requests.get(URL,  timeout=10)
response.raise_for_status()
df = pd.read_csv(StringIO(response.text))

# signed value (BUY +, SELL -)
signed = (
    df["Quantity Traded"]
    * df["Trade Price / Wght. Avg. Price"]
    * np.where(df["Buy/Sell"] == "BUY", 1, -1)
)

# NET_VALUE per Date + Symbol + Client Name
df["NET_VALUE"] = (
    signed.groupby([df["Date"], df["Symbol"], df["Client Name"]])
    .transform("sum")
)

# filter by threshold
df = df[df["NET_VALUE"].abs() >= THRESHOLD]

df.to_csv('modified_historical_bulk_deals.csv', index=False)
