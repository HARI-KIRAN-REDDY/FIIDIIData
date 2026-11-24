import csv
import io
import os
import time
from playwright.sync_api import sync_playwright

OUTPUT_CSV_FILE = "index_constituents.csv"

INDEX_SOURCES = {
    # Broad Market Indices
    "NSE_INDEX|Nifty 50": ("Nifty 50", "https://niftyindices.com"),
    "NSE_INDEX|Nifty Next 50": ("Nifty Next 50", "https://niftyindices.com"),
    "NSE_INDEX|Nifty 100": ("Nifty 100", "https://niftyindices.com"),
    "NSE_INDEX|Nifty 200": ("Nifty 200", "https://niftyindices.com"),
    "NSE_INDEX|Nifty 500": ("Nifty 500", "https://niftyindices.com"),
    "NSE_INDEX|Nifty Midcap 50": ("Nifty Midcap 50", "https://niftyindices.com"),
    "NSE_INDEX|NIFTY MIDCAP 100": ("Nifty Midcap 100", "https://niftyindices.com"),
    "NSE_INDEX|NIFTY MIDCAP 150": ("Nifty Midcap 150", "https://niftyindices.com"),
    "NSE_INDEX|NIFTY MID SELECT": ("Nifty Midcap Select", "https://niftyindices.com"),
    "NSE_INDEX|NIFTY SMLCAP 50": ("Nifty Smallcap 50", "https://niftyindices.com"),
    "NSE_INDEX|NIFTY SMLCAP 100": ("Nifty Smallcap 100", "https://niftyindices.com"),
    "NSE_INDEX|NIFTY SMLCAP 250": ("Nifty Smallcap 250", "https://niftyindices.com"),

    # Sectoral Indices
    "NSE_INDEX|Nifty Bank": ("Nifty Bank", "https://niftyindices.com"),
    "NSE_INDEX|Nifty Pvt Bank": ("Nifty Private Bank", "https://niftyindices.com"),
    "NSE_INDEX|Nifty PSU Bank": ("Nifty PSU Bank", "https://niftyindices.com"),
    "NSE_INDEX|Nifty Fin Service": ("Nifty Financial Services", "https://niftyindices.com"),
    "NSE_INDEX|Nifty FinSrv25 50": ("Nifty Fin Service 25/50", "https://niftyindices.com"),
    "NSE_INDEX|Nifty IT": ("Nifty IT", "https://niftyindices.com"),
    "NSE_INDEX|Nifty Auto": ("Nifty Auto", "https://niftyindices.com"),
    "NSE_INDEX|Nifty Pharma": ("Nifty Pharma", "https://niftyindices.com"),
    "NSE_INDEX|NIFTY HEALTHCARE": ("Nifty Healthcare", "https://niftyindices.com"),
    "NSE_INDEX|Nifty FMCG": ("Nifty FMCG", "https://niftyindices.com"),
    "NSE_INDEX|Nifty Metal": ("Nifty Metal", "https://niftyindices.com"),
    "NSE_INDEX|Nifty Energy": ("Nifty Energy", "https://niftyindices.com"),
    "NSE_INDEX|NIFTY OIL AND GAS": ("Nifty Oil & Gas", "https://niftyindices.com"),
    "NSE_INDEX|Nifty Realty": ("Nifty Realty", "https://niftyindices.com"),
    "NSE_INDEX|Nifty Media": ("Nifty Media", "https://niftyindices.com"),
    "NSE_INDEX|NIFTY CONSR DURBL": ("Nifty Consumer Durables", "https://niftyindices.com"),
    "NSE_INDEX|Nifty Infra": ("Nifty Infrastructure", "https://niftyindices.com"),
    "NSE_INDEX|Nifty Commodities": ("Nifty Commodities", "https://niftyindices.com"),
    "NSE_INDEX|Nifty PSE": ("Nifty PSE", "https://niftyindices.com"),
    "NSE_INDEX|Nifty MNC": ("Nifty MNC", "https://niftyindices.com"),
}


def fetch_and_save_csv(output_path: str = OUTPUT_CSV_FILE) -> None:
    all_rows = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        )
        page = context.new_page()

        # Pass JS security challenge on niftyindices.com first
        print("Warming up session on niftyindices.com...")
        page.goto("https://niftyindices.com", wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(3000)

        for index_key, (index_name, csv_url) in INDEX_SOURCES.items():
            try:
                # Use context.request which shares all JS-generated browser cookies
                resp = context.request.get(csv_url, timeout=30000)
                if not resp.ok:
                    raise ValueError(f"HTTP {resp.status}")

                text_content = resp.text().lstrip("\ufeff").strip()
                if text_content.startswith("<"):
                    raise ValueError("Received HTML instead of CSV")

                reader = csv.DictReader(io.StringIO(text_content))
                count = 0

                for row in reader:
                    isin = (row.get("ISIN Code") or "").strip()
                    series = (row.get("Series") or "").strip()
                    symbol = (row.get("Symbol") or "").strip()
                    company_name = (row.get("Company Name") or "").strip()

                    if series == "EQ" and isin:
                        all_rows.append({
                            "index_instrument_key": index_key,
                            "index": index_name,
                            "stock_instrument_key": f"NSE_EQ|{isin}",
                            "trading_symbol": symbol,
                            "company_name": company_name,
                            "isin": isin,
                        })
                        count += 1

                print(f"[SUCCESS] {index_name} -> {count} stocks")
                time.sleep(0.3)

            except Exception as err:
                print(f"[ERROR] {index_name} ({csv_url}): {err}")

        browser.close()

    if not all_rows:
        raise RuntimeError("No records fetched from Nifty Indices. Existing CSV was not overwritten.")

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

    print(f"\nSaved {len(all_rows)} rows to {output_path}")


if __name__ == "__main__":
    fetch_and_save_csv()
