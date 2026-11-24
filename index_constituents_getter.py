
import requests
import pandas as pd
from bs4 import BeautifulSoup
from io import StringIO
from urllib.parse import urljoin
from pathlib import Path
import re
import time

BASE_URL = "https://www.niftyindices.com"
OUTPUT_FILE = "nifty_all_indices.csv"
FAILED_FILE = "failed_indices.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "text/csv,*/*;q=0.8",
    "Referer": "https://www.niftyindices.com/",
}

DISCOVERY_PAGES = [
    "https://www.niftyindices.com/indices/equity",
]

KNOWN_INDICES = {
    "Nifty 50": "ind_nifty50list.csv",
    "Nifty 100": "ind_nifty100list.csv",
    "Nifty 200": "ind_nifty200list.csv",
    "Nifty 500": "ind_nifty500list.csv",
    "Nifty Next 50": "ind_niftynext50list.csv",
    "Nifty Midcap 50": "ind_niftymidcap50list.csv",
    "Nifty Midcap 100": "ind_niftymidcap100list.csv",
    "Nifty Midcap 150": "ind_niftymidcap150list.csv",
    "Nifty Smallcap 50": "ind_niftysmallcap50list.csv",
    "Nifty Smallcap 100": "ind_niftysmallcap100list.csv",
    "Nifty Smallcap 250": "ind_niftysmallcap250list.csv",
    "Nifty Auto": "ind_niftyautolist.csv",
    "Nifty Bank": "ind_niftybanklist.csv",
    "Nifty IT": "ind_niftyitlist.csv",
    "Nifty FMCG": "ind_niftyfmcglist.csv",
    "Nifty Pharma": "ind_niftypharmalist.csv",
    "Nifty Healthcare": "ind_niftyhealthcarelist.csv",
    "Nifty Media": "ind_niftymedialist.csv",
    "Nifty Metal": "ind_niftymetallist.csv",
    "Nifty Realty": "ind_niftyrealtylist.csv",
    "Nifty Energy": "ind_niftyenergylist.csv",
    "Nifty PSU Bank": "ind_niftypsubanklist.csv",
    "Nifty Private Bank": "ind_niftyprivatebanklist.csv",
    "Nifty Oil & Gas": "ind_niftyoilgaslist.csv",
    "Nifty Financial Services": "ind_niftyfinancelist.csv",
    "Nifty Financial Services 25/50":
        "ind_niftyfinancialservices25-50list.csv",
    "Nifty Infrastructure": "ind_niftyinfralist.csv",
    "Nifty Commodities": "ind_niftycommoditieslist.csv",
    "Nifty Consumption": "ind_niftyconsumptionlist.csv",
    "Nifty CPSE": "ind_niftycpselist.csv",
    "Nifty PSE": "ind_niftypselist.csv",
    "Nifty MNC": "ind_niftymnclist.csv",
    "Nifty India Defence": "ind_niftyindiadefencelist.csv",
    "Nifty Chemicals": "ind_niftychemicalslist.csv",
    "Nifty Consumer Durables": "ind_niftyconsumerdurableslist.csv",
    "Nifty Services Sector": "ind_niftyservicelist.csv",
    "Nifty India Tourism": "ind_niftyindiatourismlist.csv",
}

session = requests.Session()
session.headers.update(HEADERS)


def discover_indices():
    indices = {
        name: urljoin(
            BASE_URL,
            f"/IndexConstituent/{filename}"
        )
        for name, filename in KNOWN_INDICES.items()
    }

    print("Discovering additional index CSVs...")

    for page in DISCOVERY_PAGES:
        try:
            response = session.get(page, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            for anchor in soup.find_all("a", href=True):
                href = anchor["href"]

                if not re.search(
                    r"IndexConstituent/.*\.csv$",
                    href,
                    re.I
                ):
                    continue

                url = urljoin(BASE_URL, href)

                filename = url.rsplit("/", 1)[-1]

                name = anchor.get_text(" ", strip=True)

                if not name:
                    name = re.sub(
                        r"^ind_|list\.csv$",
                        "",
                        filename,
                        flags=re.I
                    ).replace("_", " ").title()

                indices.setdefault(name, url)

            time.sleep(1)

        except Exception as exc:
            print(f"Discovery failed for {page}: {exc}")

    return indices


def get_column(df, candidates):
    normalized = {
        re.sub(r"[^a-z0-9]", "", str(c).lower()): c
        for c in df.columns
    }

    for candidate in candidates:
        key = re.sub(
            r"[^a-z0-9]",
            "",
            candidate.lower()
        )

        if key in normalized:
            return normalized[key]

    return None


def download_index(index_name, url):
    response = session.get(url, timeout=30)
    response.raise_for_status()

    df = pd.read_csv(
        StringIO(response.content.decode("utf-8-sig"))
    )

    symbol_col = get_column(
        df, ["Symbol", "Trading Symbol"]
    )

    company_col = get_column(
        df, ["Company Name", "CompanyName"]
    )

    isin_col = get_column(
        df, ["ISIN Code", "ISIN"]
    )

    if not symbol_col:
        raise ValueError("Symbol column missing")

    if not company_col:
        raise ValueError("Company Name column missing")

    if not isin_col:
        raise ValueError("ISIN column missing")

    rows = []

    for _, stock in df.iterrows():
        symbol = str(stock[symbol_col]).strip()

        if not symbol or symbol.lower() == "nan":
            continue

        company = str(stock[company_col]).strip()
        isin = str(stock[isin_col]).strip()

        rows.append({
            "index_instrument_key": f"NSE_INDEX|{index_name}",
            "index_name": index_name,
            "stock_instrument_key": f"NSE_EQ|{symbol}",
            "trading_symbol": symbol,
            "company_name": company,
            "isin": isin,
        })

    return rows


def main():
    indices = discover_indices()

    print(f"\nTotal indices discovered: {len(indices)}")

    all_rows = []
    failed = []

    for index_name, url in indices.items():
        try:
            rows = download_index(index_name, url)
            all_rows.extend(rows)

            print(f"SUCCESS: {index_name}: {len(rows)} stocks")

        except Exception as exc:
            print(f"FAILED: {index_name}: {exc}")

            failed.append({
                "index_name": index_name,
                "url": url,
                "error": str(exc),
            })

        time.sleep(0.5)

    columns = [
        "index_instrument_key",
        "index_name",
        "stock_instrument_key",
        "trading_symbol",
        "company_name",
        "isin",
    ]

    result = pd.DataFrame(all_rows, columns=columns)

    if not result.empty:
        result.drop_duplicates(
            subset=["index_name", "isin"],
            inplace=True
        )

    result.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    pd.DataFrame(
        failed,
        columns=["index_name", "url", "error"]
    ).to_csv(
        FAILED_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    print("\n========== SUMMARY ==========")
    print("Indices discovered:", len(indices))
    print("Successful rows:", len(result))
    print("Unique stocks:", result["isin"].nunique())
    print("Failed indices:", len(failed))
    print("CSV:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
