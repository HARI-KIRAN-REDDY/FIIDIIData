import csv
import io
import os
import time
import requests

OUTPUT_CSV_FILE = "index_constituents.csv"

INDEX_SOURCES = {
    # Broad Market & Sectoral Indices mapping
    "NSE_INDEX|Nifty 50": ("Nifty 50", "https://niftyindices.com"),
    "NSE_INDEX|Nifty Bank": ("Nifty Bank", "https://niftyindices.com"),
    # ... (includes major broad market and sectoral Nifty CSV endpoints)
}

def build_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/csv,*/*;q=0.8",
        "Referer": "https://niftyindices.com",
    })
    return session

def fetch_and_save_csv(output_path: str = OUTPUT_CSV_FILE) -> None:
    session = build_session()
    all_rows = []

    for index_key, (index_name, csv_url) in INDEX_SOURCES.items():
        try:
            resp = session.get(csv_url, timeout=25)
            resp.raise_for_status()
            text_content = resp.text.lstrip("\ufeff").strip()
            if text_content.startswith("<"):
                raise ValueError("Received HTML instead of CSV")

            reader = csv.DictReader(io.StringIO(text_content))
            for row in reader:
                isin = (row.get("ISIN Code") or "").strip()
                series = (row.get("Series") or "").strip()
                if series == "EQ" and isin:
                    all_rows.append({
                        "index_instrument_key": index_key,
                        "index": index_name,
                        "stock_instrument_key": f"NSE_EQ|{isin}",
                        "trading_symbol": (row.get("Symbol") or "").strip(),
                        "company_name": (row.get("Company Name") or "").strip(),
                        "isin": isin,
                    })
            time.sleep(0.5)
        except Exception as err:
            print(f"[ERROR] {index_name}: {err}")

    if all_rows:
        os.makedirs(os.path.dirname(output_path), exist_ok=True) if os.path.dirname(output_path) else None
        fieldnames = ["index_instrument_key", "index", "stock_instrument_key", "trading_symbol", "company_name", "isin"]
        with open(output_path, mode="w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_rows)

if __name__ == "__main__":
    fetch_and_save_csv()
