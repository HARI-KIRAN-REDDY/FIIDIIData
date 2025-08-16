import requests
from datetime import datetime, timedelta

def save_bulk_csv_file():
    # one day
    # url = "https://nsearchives.nseindia.com/content/equities/bulk.csv"

    # one week
    end_date = datetime.today()
    start_date = end_date - timedelta(days=7)
    url = (
        "https://www.nseindia.com/api/historicalOR/bulk-block-short-deals?"
        f"optionType={option_type}_deals"
        f"&from={start_date.strftime('%d-%m-%Y')}"
        f"&to={end_date.strftime('%d-%m-%Y')}"
        f"&csv=true"
    )

    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Referer": "https://www.niftyindices.com/reports/historical-data",
        "Origin": "https://www.niftyindices.com",
        "Accept": "*/*",
        "X-Requested-With": "XMLHttpRequest",
    }

    response = requests.get(url, headers=headers, timeout=10)

    if response.status_code == 200:
        with open("bulk.csv", "w", newline="", encoding="utf-8") as f:
            f.write(response.text)
        print("✅ Saved Bulk Deals to `bulk.csv`")
    else:
        print(f"❌ Request failed: {response.status_code}")
        print("Response:", response.text)

if __name__ == "__main__":
    save_bulk_csv_file()


