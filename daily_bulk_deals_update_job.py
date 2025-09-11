# import requests
# from datetime import datetime, timedelta

# def save_bulk_csv_file(option_type='bulk'):
#     # one day
#     url = "https://nsearchives.nseindia.com/content/equities/bulk.csv"

#     # one week
#     # end_date = datetime.today()
#     # start_date = end_date - timedelta(days=7)
#     # url = (
#     #     "https://www.nseindia.com/api/historicalOR/bulk-block-short-deals?"
#     #     f"optionType={option_type}_deals"
#     #     f"&from={start_date.strftime('%d-%m-%Y')}"
#     #     f"&to={end_date.strftime('%d-%m-%Y')}"
#     #     f"&csv=true"
#     # )

#     headers = {
#         "Content-Type": "application/json; charset=utf-8",
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
#         "Referer": "https://www.niftyindices.com/reports/historical-data",
#         "Origin": "https://www.niftyindices.com",
#         "Accept": "*/*",
#         "X-Requested-With": "XMLHttpRequest",
#     }

#     response = requests.get(url, headers=headers, timeout=10)

#     if response.status_code == 200:
#         with open("bulk.csv", "w", newline="", encoding="utf-8") as f:
#             f.write(response.text)
#         print("✅ Saved Bulk Deals to `bulk.csv`")
#     else:
#         print(f"❌ Request failed: {response.status_code}")
#         print("Response:", response.text)

# if __name__ == "__main__":
#     save_bulk_csv_file()



import requests

def save_bulk_csv_file():
    url = "https://nsearchives.nseindia.com/content/equities/bulk.csv"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.nseindia.com/",
        "Connection": "keep-alive",
    }

    # Create a session
    session = requests.Session()
    session.headers.update(headers)

    # Step 1: Hit NSE home to get cookies
    session.get("https://www.nseindia.com", timeout=10)

    # Step 2: Now request bulk file
    response = session.get(url, timeout=10)

    if response.status_code == 200:
        with open("bulk.csv", "w", encoding="utf-8") as f:
            f.write(response.text)
        print("✅ Saved Bulk Deals to `bulk.csv`")
    else:
        print(f"❌ Request failed: {response.status_code}")
        print("Response:", response.text)

if __name__ == "__main__":
    save_bulk_csv_file()


