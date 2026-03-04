import yfinance as yf
import pandas as pd

def save_gold_nifty_ratio_csv(option_type='bulk'):
    gold_etf = yf.Ticker("GOLDBEES.NS")
    gold_df = gold_etf.history(period="30y")
    gold_df['10gm_gold_price'] = gold_df['Close']*1000
    gold_df = gold_df.reset_index()
    gold_df = gold_df[['Date', '10gm_gold_price']]
    
    nifty_etf = yf.Ticker("^NSEI")
    nifty_etf = nifty_etf.history(period="30y")
    nifty_etf = nifty_etf.reset_index()
    nifty_etf = nifty_etf[['Date', 'Close']]
    
    
    merged_df = pd.merge(nifty_etf, gold_df, on='Date', how='inner')
    merged_df = merged_df.rename(columns={'Close': 'Nifty_Price'})
    
    merged_df['gold_nifty_ratio'] = merged_df['10gm_gold_price'] / merged_df['Nifty_Price']
    merged_df['gold_nifty_ratio'] = merged_df['gold_nifty_ratio'].round(1)
    merged_df = merged_df.set_index('Date')

    with open("gold_nifty_ratio.csv", "w", newline="", encoding="utf-8") as f:
        f.write(response.text)
    print("✅ Saved Gold Nifty Ratio to 'gold_nifty_ratio.csv' file")

if __name__ == "__main__":
    save_gold_nifty_ratio_csv()
