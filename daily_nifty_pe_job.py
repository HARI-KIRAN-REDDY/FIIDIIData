import requests
import json
import csv
import sys
from datetime import datetime

# Setup
index_name = "NIFTY-50"
name = "NIFTY 50"
start_date = "1990-01-01"
end_date = datetime.today().strftime("%Y-%m-%d")

# URL
url = "https://www.niftyindices.com/Backpage.aspx/getpepbHistoricaldataDBtoString"

# Payload
payload = {
    "cinfo": json.dumps({
        "name": name,
        "startDate": start_date,
        "endDate": end_date,
        "indexName": index_name
    })
}

# Headers
headers = {
    "Content-Type": "application/json; charset=utf-8",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Referer": "https://www.niftyindices.com/reports/historical-data",
    "Origin": "https://www.niftyindices.com",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
}

try:
    # Create session
    session = requests.Session()
    session.headers.update(headers)

    # Open website first to establish session/cookies
    print("Opening niftyindices.com...")
    home_response = session.get(
        "https://www.niftyindices.com/",
        timeout=30
    )

    print("Homepage status:", home_response.status_code)

    # Send POST request
    print("Requesting historical NIFTY P/E, P/B and Dividend Yield data...")

    response = session.post(
        url,
        json=payload,
        timeout=30
    )

    # Debug response
    print("API status:", response.status_code)
    print("Content-Type:", response.headers.get("Content-Type"))
    print("Response length:", len(response.text))
    print("Response preview:", response.text[:500])

    # Check HTTP status
    response.raise_for_status()

    # Parse outer JSON
    try:
        result = response.json()
    except requests.exceptions.JSONDecodeError:
        print("❌ Response is not valid JSON")
        print("Full response:")
        print(response.text[:3000])
        sys.exit(1)

    # Check expected response structure
    if "d" not in result:
        print("❌ Unexpected API response:")
        print(result)
        sys.exit(1)

    # Parse inner JSON
    try:
        data = json.loads(result["d"])
    except (json.JSONDecodeError, TypeError) as e:
        print("❌ Inner JSON decode failed:", e)
        print("Response data:")
        print(str(result["d"])[:3000])
        sys.exit(1)

    # Validate data
    if not isinstance(data, list):
        print("❌ Unexpected data format")
        print(data)
        sys.exit(1)

    if len(data) == 0:
        print("❌ API returned zero records")
        sys.exit(1)

    print("Total records fetched:", len(data))

    # Save CSV
    filename = "nifty_pe_pb_div.csv"

    with open(
        filename,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:
        writer = csv.writer(f)

        writer.writerow([
            "Date",
            "Index Name",
            "PE",
            "PB",
            "DivYield"
        ])

        for row in data:
            writer.writerow([
                row.get("DATE"),
                row.get("Index Name"),
                row.get("pe"),
                row.get("pb"),
                row.get("divYield")
            ])

    print(f"✅ Saved {len(data)} records to `{filename}`")

except requests.exceptions.RequestException as e:
    print("❌ Request failed:", e)
    sys.exit(1)

except Exception as e:
    print("❌ Unexpected error:", e)
    sys.exit(1)

