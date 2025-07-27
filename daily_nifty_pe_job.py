import requests
import json
import csv
from datetime import datetime

# Setup
index_name = "NIFTY–50"
name = "NIFTY 50"
start_date = "1990-01-01"
end_date = datetime.today().strftime("%Y-%m-%d")

# Build payload
payload = {
    "cinfo": json.dumps({
        "name": name,
        "startDate": start_date,
        "endDate": end_date,
        "indexName": index_name
    })
}

headers = {
    "Content-Type": "application/json; charset=utf-8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Referer": "https://www.niftyindices.com/reports/historical-data",
    "Origin": "https://www.niftyindices.com",
    "Accept": "*/*",
    "X-Requested-With": "XMLHttpRequest",  # Important for ASP.NET AJAX
}

# url = "https://www.niftyindices.com/Backpage.aspx/getHistoricaldatatabletoString"
url = "https://www.niftyindices.com/Backpage.aspx/getpepbHistoricaldataDBtoString"

response = requests.post(url, headers=headers, json=payload, timeout=15)
# Send POST request
if response.status_code == 200:
    result = response.json()
    print(result)
    try:
        data = json.loads(result["d"])  # Extract inner JSON string
    except Exception as e:
        print("❌ JSON decode failed:", e)
        print("Response data:", result)
        exit(1)

    # Save as CSV
    filename = "nifty_pe_pb_div.csv"
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Index Name", "PE", "PB", "DivYield"])
        for row in data:
            writer.writerow([
                row["DATE"],
                row["Index Name"],
                row["pe"],
                row["pb"],
                row["divYield"]
            ])
    print(f"✅ Saved historical P/E, P/B, DivYield data to `{filename}`")
else:
    print(f"❌ Request failed: {response.status_code} - {response.text}")
