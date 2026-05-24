"""Generate a large synthetic trades CSV for testing.

This script creates N_ROWS simulated trade records in chunks and writes to
OUTPUT_FILE. Each row contains timestamp, symbol, trader_id, desk, region,
execution_venue, order_type, price, quantity, fee, pnl, volatility, spread,
liquidity_flag, algorithm, client_type, settlement_date, and is_crossed flag.

Adjust `N_ROWS`, `CHUNK_SIZE` and the categorical pools below to change the
volume and variation of generated data.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

N_ROWS = 100_000
CHUNK_SIZE = 1_000_000
OUTPUT_FILE = "trades_100k.csv"

# --- Fixed categorical pools ---
symbols = [
    # --- Equities (US & Global) ---
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "JPM", "V", "WMT",
    "DIS", "NFLX", "AMD", "BABA", "TSMC", "ASML", "LVMH", "SHEL", "NVO", "SAP",
    "JNJ", "PG", "XOM", "LLY", "AVGO", "HD", "COST", "MA", "ADBE", "CRM",
    "NESTLE", "ROCHE", "NOVARTIS", "HSBC", "BP", "RIO", "BHP", "SONY", "TENCENT", "ASDF",
    # --- FX Pairs ---
    "EURUSD", "USDJPY", "GBPUSD", "AUDUSD", "USDCAD", "USDCHF", "NZDUSD", "EURGBP", "EURJPY", "GBPJPY",
    # --- Commodities / Commodity ETFs ---
    "GLD", "SLV", "USO", "UNG", "DBA", "CORN", "SOYB", "WEAT", "COPX", "CPER",
    # --- Rates, Fixed Income & Treasury ETFs ---
    "TLT", "IEF", "SHY", "LQD", "HYG", "BND", "TIP", "AGG", "SHV", "MBB",
    # --- Major Indices & Sector ETFs ---
    "SPY", "QQQ", "DIA", "IWM", "EEM", "VGK", "EWJ", "FXI", "XLF", "XLK",
    "XLV", "XLE", "XLI", "XLB", "XLY", "XLP", "XLU", "XLRE", "XLC", "KRE",
    # --- Crypto Pairs ---
    "BTCUSD", "ETHUSD", "SOLUSD", "XRPUSD", "ADAUSD", "DOTUSD", "LTCUSD", "LINKUSD", "UNIUSD", "DOGEUSD"
]
traders = [f"TRD_{i}" for i in range(1, 401)]
desks = [
    "Equities",
    "Derivatives",
    "FX",
    "FixedIncome",
    "Commodities",
    "Rates",
    "PrimeServices",
]
# Regions updated per request: North America (NAM), Asia Pacific (APAC), Europe/Middle East/Africa (EMEA)
regions = ["NAM", "APAC", "EMEA"]
venues = [
    "XNYS",
    "XLON",
    "XJPX",
    "XSHG",
    "XETR",
    "XPAR",
    "XASX",
    "XNSE",
    "XBSE",
    "XTAE",
    "XHKG",
    "XBOM",
    "XCME",
    "XNAS",
]
order_types = ["MARKET", "LIMIT", "IOC", "FOK", "STOP", "PEG", "ICEBERG"]
liquidity = ["VERY_HIGH", "HIGH", "MEDIUM", "LOW"]
algorithms = ["VWAP", "TWAP", "IS", "POV", "SNAP", None]
client_types = [
    "INSTITUTIONAL",
    "RETAIL",
    "HFT",
    "PROPRIETARY",
    "HEDGE_FUND",
]

def rand_cat(size, categories):
    return np.random.choice(categories, size=size)

# --- Write CSV in chunks ---
header_written = False
for start in range(0, N_ROWS, CHUNK_SIZE):
    chunk_size = min(CHUNK_SIZE, N_ROWS - start)
    idx = np.arange(start, start + chunk_size)

    # Timestamps (3 years range)
    start_ts = datetime(2023, 1, 1)
    end_ts = datetime(2025, 12, 31)
    total_seconds = int((end_ts - start_ts).total_seconds())
    ts_sec = np.random.randint(0, total_seconds, chunk_size)
    # FIX: convert numpy.int64 to Python int using int(s)
    timestamps = [start_ts + timedelta(seconds=int(s)) for s in ts_sec]

    # Numeric columns
    price = np.random.uniform(10, 500, chunk_size)
    quantity = np.random.randint(1, 10001, chunk_size)
    side = np.random.choice(["BUY", "SELL"], chunk_size, p=[0.52, 0.48])
    pnl = np.random.normal(0, 25, chunk_size) * quantity / 100
    fee = np.random.uniform(0, 50, chunk_size)
    volatility = np.random.uniform(0.01, 0.50, chunk_size)
    spread = 0.002 + volatility * 0.1 + np.random.normal(0, 0.005, chunk_size)
    spread = np.clip(spread, 0.001, 0.05)

    # Settlement date (T+2)
    settlement = [ts + timedelta(days=2) for ts in timestamps]

    is_crossed = np.random.choice([True, False], chunk_size, p=[0.3, 0.7])

    # Build DataFrame chunk
    df_chunk = pd.DataFrame({
        "trade_id": idx,
        "timestamp": timestamps,
        "symbol": rand_cat(chunk_size, symbols),
        "side": side,
        "quantity": quantity,
        "price": price,
        "trader_id": rand_cat(chunk_size, traders),
        "desk": rand_cat(chunk_size, desks),
        "region": rand_cat(chunk_size, regions),
        "execution_venue": rand_cat(chunk_size, venues),
        "order_type": rand_cat(chunk_size, order_types),
        "fee": fee,
        "pnl": pnl,
        "volatility": volatility,
        "spread": spread,
        "liquidity_flag": rand_cat(chunk_size, liquidity),
        "algorithm": rand_cat(chunk_size, algorithms),
        "client_type": rand_cat(chunk_size, client_types),
        "settlement_date": settlement,
        "is_crossed": is_crossed
    })

    # Append to CSV
    df_chunk.to_csv(OUTPUT_FILE, mode='a', header=not header_written, index=False)
    header_written = True
    print(f"Written rows {start+1} to {start+chunk_size}")

print(f"✅ Generated {N_ROWS} rows in {OUTPUT_FILE}")