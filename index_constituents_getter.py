import csv
import gzip
import io
import json
import os
import time
import requests

UPSTOX_NSE_MASTER_URL = "https://upstox.com"
OUTPUT_CSV_FILE = "index_constituents.csv"

# Mapping of Upstox index_instrument_key -> (index_name, NSE constituent CSV URL)
INDEX_SOURCES = {
    # Broad Market Indices
    "NSE_INDEX|Nifty 50": ("Nifty 50", "https://nseindia.com"),
    "NSE_INDEX|Nifty Next 50": ("Nifty Next 50", "https://nseindia.com"),
    "NSE_INDEX|Nifty 100": ("Nifty 100", "https://nseindia.com"),
    "NSE_INDEX|Nifty 200": ("Nifty 200", "https://nseindia.com"),
    "NSE_INDEX|Nifty 500": ("Nifty 500", "https://nseindia.com"),
    "NSE_INDEX|Nifty Midcap 50": ("Nifty Midcap 50", "https://nseindia.com"),
    "NSE_INDEX|NIFTY MIDCAP 100": ("Nifty Midcap 100", "https://nseindia.com"),
    "NSE_INDEX|NIFTY MIDCAP 150": ("Nifty Midcap 150", "https://nseindia.com"),
    "NSE_INDEX|NIFTY MID SELECT": ("Nifty Midcap Select", "https://nseindia.com"),
    "NSE_INDEX|NIFTY SMLCAP 50": ("Nifty Smallcap 50", "https://nseindia.com"),
    "NSE_INDEX|NIFTY SMLCAP 100": ("Nifty Smallcap 100", "https://nseindia.com"),
    "NSE_INDEX|NIFTY SMLCAP 250": ("Nifty Smallcap 250", "https://nseindia.com"),

    # Sectoral Indices
    "NSE_INDEX|Nifty Bank": ("Nifty Bank", "https://nseindia.com"),
    "NSE_INDEX|Nifty Pvt Bank": ("Nifty Private Bank", "https://nseindia.com"),
    "NSE_INDEX|Nifty PSU Bank": ("Nifty PSU Bank", "https://nseindia.com"),
    "NSE_INDEX|Nifty Fin Service": ("Nifty Financial Services", "https://nseindia.com"),
    "NSE_INDEX|Nifty FinSrv25 50": ("Nifty Fin Service 25/50", "https://nseindia.com"),
    "NSE_INDEX|Nifty IT": ("Nifty IT", "https://nseindia.com"),
    "NSE_INDEX|Nifty Auto": ("Nifty Auto", "https://nseindia.com"),
    "NSE_INDEX|Nifty Pharma": ("Nifty Pharma", "https://nseindia.com"),
    "NSE_INDEX|NIFTY HEALTHCARE": ("Nifty Healthcare", "https://nseindia.com"),
    "NSE_INDEX|Nifty FMCG": ("Nifty FMCG", "https://nseindia.com"),
    "NSE_INDEX|Nifty Metal": ("Nifty Metal", "https://nseindia.com"),
    "NSE_INDEX|Nifty Energy": ("Nifty Energy", "https://nseindia.com"),
    "NSE_INDEX|NIFTY OIL AND GAS": ("Nifty Oil & Gas", "https://nseindia.com"),
    "NSE_INDEX|Nifty Realty": ("Nifty Realty", "https://nseindia.com"),
    "NSE_INDEX|Nifty Media": ("Nifty Media", "https://nseindia.com"),
    "NSE_INDEX|NIFTY CONSR DURBL": ("Nifty Consumer Durables", "https://nseindia.com"),
    "NSE_INDEX|Nifty Infra": ("Nifty Infrastructure", "https://nseindia.com"),
    "NSE_INDEX|Nifty Commodities": ("Nifty Commodities", "https://nseindia.com"),
    "NSE_INDEX|Nifty PSE": ("Nifty PSE", "https://nseindia.com"),
    "NSE_INDEX|Nifty MNC": ("Nifty MNC", "https://nseindia.com"),
}


def get_upstox_equity_map() -> dict[str, dict]:
    """
    Fetches Upstox's daily NSE instrument master file and returns a lookup dictionary:
    { isin: { "stock_instrument_key": ..., "trading_symbol": ..., "company_name": ... } }
    """
    response = requests.get(UPSTOX_NSE_MASTER_URL, timeout=30)
    response.raise_for_status()

    with gzip.GzipFile(fileobj=io.BytesIO(response.content)) as gz_file:
        instruments = json.loads(gz_file.read().decode("utf-8"))

    equity_map = {}
    for item in instruments:
        if item.get("segment") == "NSE_EQ" and item.get("instrument_type") == "EQ":
            isin = (item.get("isin") or "").strip()
            if isin:
                equity_map[isin] = {
                    "stock_instrument_key": item["instrument_key"],
                    "trading_symbol": item.get("trading_symbol", ""),
                    "company_name": item.get("name", ""),
                }
    return equity_map


def create_nse_session() -> requests.Session:
    """Initializes a requests session with headers and cookies accepted by NSE archives."""
    session = requests.Session()
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept": "text/csv,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://niftyindices.com",
    })
    return session


def fetch_and_save_csv(output_path: str = OUTPUT_CSV_FILE) -> None:
    equity_map = get_upstox_equity_map()
    print(f"Loaded {len(equity_map)} valid NSE_EQ stocks from Upstox master.")

    session = create_nse_session()
    all_rows = []

    for index_key, (index_name, csv_url) in INDEX_SOURCES.items():
        try:
            resp = session.get(csv_url, timeout=20)
            resp.raise_for_status()

            reader = csv.DictReader(io.StringIO(resp.text))
            added_count = 0

            for row in reader:
                isin = (row.get("ISIN Code") or "").strip()
                series = (row.get("Series") or "").strip()

                if series == "EQ" and isin in equity_map:
                    stock = equity_map[isin]
                    all_rows.append({
                        "index_instrument_key": index_key,
                        "index": index_name,
                        "stock_instrument_key": stock["stock_instrument_key"],
                        "trading_symbol": stock["trading_symbol"],
                        "company_name": stock["company_name"],
                        "isin": isin,
                    })
                    added_count += 1

            print(f"[SUCCESS] {index_name} ({index_key}) -> {added_count} stocks")
            time.sleep(0.5)

        except Exception as err:
            print(f"[ERROR] Failed fetching {index_name} ({csv_url}): {err}")

    if not all_rows:
        raise RuntimeError("No records fetched from NSE. Existing CSV was not overwritten.")

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    fieldnames = [
        "index_instrument_key",
        "index",
        "stock_instrument_key",
        "trading_symbol",
        "company_name",
        "isin",
    ]

    with open(output_path, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"\nDone! Wrote {len(all_rows)} rows to '{output_path}'.")


if __name__ == "__main__":
    fetch_and_save_csv()
