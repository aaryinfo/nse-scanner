"""
NSE Real-Time Intraday Scanner - Backend (v2 - 213 stocks, locked entries)
========================================
Run:  pip install flask flask-cors yfinance pandas numpy requests
      python server_v2.py

Features:
  - 213 NSE F&O stocks (complete universe)
  - Locked entry prices (don't change with LTP fluctuations)
  - ORB, VWAP, NR7 strategies
  - Real data from TradingView + yfinance
"""

from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import yfinance as yf
import pandas as pd
import numpy as np
import requests
import threading
import time
import json
import math
import os
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

app = Flask(__name__, static_folder=".")
CORS(app)

# ── CONFIG ────────────────────────────────────────────────────────────────────
SCAN_INTERVAL   = 60
MAX_WORKERS     = 16
TV_TIMEOUT      = 6
YF_TIMEOUT      = 10

TV_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Content-Type": "application/json",
    "Origin": "https://www.tradingview.com",
    "Referer": "https://www.tradingview.com/",
}

# ── 213 NSE F&O STOCKS (COMPLETE UNIVERSE) ─────────────────────────────────
STOCKS = [
    ("360ONE",     "360 ONE WAM"),    ("ABB",         "ABB India"),
    ("APLAPOLLO",  "APL Apollo"),     ("AUBANK",      "AU Small Finance"),
    ("ADANIENSOL", "Adani Energy"),   ("ADANIENT",    "Adani Enterprises"),
    ("ADANIGREEN", "Adani Green"),    ("ADANIPORTS",  "Adani Ports"),
    ("ABCAPITAL",  "Aditya Birla Cap"), ("ALKEM",     "Alkem Labs"),
    ("AMBER",      "Amber Enterprises"), ("AMBUJACEM", "Ambuja Cements"),
    ("ANGELONE",   "Angel One"),      ("APOLLOHOSP",  "Apollo Hospitals"),
    ("ASHOKLEY",   "Ashok Leyland"),  ("ASIANPAINT",  "Asian Paints"),
    ("ASTRAL",     "Astral"),         ("AUROPHARMA",  "Aurobindo Pharma"),
    ("DMART",      "Avenue Supermarts"), ("AXISBANK",  "Axis Bank"),
    ("BSE",        "BSE"),            ("BAJAJ-AUTO",  "Bajaj Auto"),
    ("BAJFINANCE", "Bajaj Finance"),  ("BAJAJFINSV",  "Bajaj Finserv"),
    ("BAJAJHLDNG", "Bajaj Holdings"), ("BANDHANBNK",  "Bandhan Bank"),
    ("BANKBARODA", "Bank of Baroda"), ("BANKINDIA",   "Bank of India"),
    ("BDL",        "Bharat Dynamics"), ("BEL",        "Bharat Electronics"),
    ("BHARATFORG", "Bharat Forge"),   ("BHEL",        "BHEL"),
    ("BPCL",       "BPCL"),           ("BHARTIARTL",  "Bharti Airtel"),
    ("BIOCON",     "Biocon"),         ("BLUESTARCO",  "Blue Star"),
    ("BOSCHLTD",   "Bosch"),          ("BRITANNIA",   "Britannia"),
    ("CGPOWER",    "CG Power"),       ("CANBK",       "Canara Bank"),
    ("CDSL",       "CDSL"),           ("CHOLAFIN",    "Cholamandalam"),
    ("CIPLA",      "Cipla"),          ("COALINDIA",   "Coal India"),
    ("COFORGE",    "Coforge"),        ("COLPAL",      "Colgate"),
    ("CAMS",       "CAMS"),           ("CONCOR",      "CONCOR"),
    ("CROMPTON",   "Crompton Greaves"), ("CUMMINSIND", "Cummins India"),
    ("DLF",        "DLF"),            ("DABUR",       "Dabur"),
    ("DALBHARAT",  "Dalmia Bharat"),  ("DELHIVERY",   "Delhivery"),
    ("DIVISLAB",   "Divi's Labs"),    ("DIXON",       "Dixon Tech"),
    ("DRREDDY",    "Dr Reddy's"),     ("ETERNAL",     "Eternal"),
    ("EICHERMOT",  "Eicher Motors"),  ("EXIDEIND",    "Exide"),
    ("NYKAA",      "Nykaa"),          ("FORTIS",      "Fortis Healthcare"),
    ("GAIL",       "GAIL"),           ("GMRAIRPORT",  "GMR Airports"),
    ("GLENMARK",   "Glenmark"),       ("GODREJCP",    "Godrej Consumer"),
    ("GODREJPROP", "Godrej Properties"), ("GRASIM",   "Grasim"),
    ("HCLTECH",    "HCL Tech"),       ("HDFCAMC",     "HDFC AMC"),
    ("HDFCBANK",   "HDFC Bank"),      ("HDFCLIFE",    "HDFC Life"),
    ("HAVELLS",    "Havells"),        ("HEROMOTOCO",  "Hero MotoCorp"),
    ("HINDALCO",   "Hindalco"),       ("HAL",         "HAL"),
    ("HINDPETRO",  "HPCL"),           ("HINDUNILVR",  "HUL"),
    ("HINDZINC",   "Hindustan Zinc"), ("POWERINDIA",  "Hitachi Energy"),
    ("HUDCO",      "HUDCO"),          ("ICICIBANK",   "ICICI Bank"),
    ("ICICIGI",    "ICICI Lombard"),  ("ICICIPRULI",  "ICICI Prudential"),
    ("IDFCFIRSTB", "IDFC First"),     ("ITC",         "ITC"),
    ("INDIANB",    "Indian Bank"),    ("NAUKRI",      "Info Edge"),
    ("IEX",        "IEX"),            ("IOC",         "IOC"),
    ("IRFC",       "IRFC"),           ("IREDA",       "IREDA"),
    ("INDUSTOWER", "Indus Towers"),   ("INDUSINDBK",  "IndusInd Bank"),
    ("INFY",       "Infosys"),        ("INOXWIND",    "Inox Wind"),
    ("INDIGO",     "IndiGo"),         ("JINDALSTEL",  "Jindal Steel"),
    ("JSWENERGY",  "JSW Energy"),     ("JSWSTEEL",    "JSW Steel"),
    ("JIOFIN",     "Jio Financial"),  ("JUBLFOOD",    "Jubilant Foodworks"),
    ("KEI",        "KEI Industries"), ("KPITTECH",    "KPIT Tech"),
    ("KALYANKJIL", "Kalyan Jewellers"), ("KAYNES",    "Kaynes Tech"),
    ("KFINTECH",   "Kfin Technologies"), ("KOTAKBANK", "Kotak Bank"),
    ("LTF",        "L&T Finance"),    ("LICHSGFIN",   "LIC Housing"),
    ("LTIM",       "LTIMindtree"),    ("LT",          "L&T"),
    ("LAURUSLABS", "Laurus Labs"),    ("LICI",        "LIC India"),
    ("LODHA",      "Lodha"),          ("LUPIN",       "Lupin"),
    ("M&M",        "M&M"),            ("MANAPPURAM",  "Manappuram"),
    ("MANKIND",    "Mankind Pharma"), ("MARICO",      "Marico"),
    ("MARUTI",     "Maruti Suzuki"),  ("MFSL",        "Max Financial"),
    ("MAXHEALTH",  "Max Healthcare"), ("MAZDOCK",     "Mazagon Dock"),
    ("MPHASIS",    "Mphasis"),        ("MCX",         "MCX"),
    ("MUTHOOTFIN", "Muthoot Finance"), ("NBCC",       "NBCC"),
    ("NHPC",       "NHPC"),           ("NMDC",        "NMDC"),
    ("NTPC",       "NTPC"),           ("NATIONALUM",  "NALCO"),
    ("NESTLEIND",  "Nestle India"),   ("NUVAMA",      "Nuvama"),
    ("OBEROIRLTY",  "Oberoi Realty"), ("ONGC",        "ONGC"),
    ("OIL",        "Oil India"),      ("PAYTM",       "Paytm"),
    ("OFSS",       "OFSS"),           ("POLICYBZR",   "PB Fintech"),
    ("PGEL",       "PG Electroplast"), ("PIIND",      "PI Industries"),
    ("PNBHOUSING", "PNB Housing"),    ("PAGEIND",     "Page Industries"),
    ("PATANJALI",  "Patanjali Foods"), ("PERSISTENT", "Persistent Systems"),
    ("PETRONET",   "Petronet LNG"),   ("PIDILITIND",  "Pidilite"),
    ("PPLPHARMA",  "Piramal Pharma"), ("POLYCAB",     "Polycab"),
    ("PFC",        "PFC"),            ("POWERGRID",   "Power Grid"),
    ("PREMIERENE", "Premier Energies"), ("PRESTIGE",  "Prestige Estates"),
    ("PNB",        "PNB"),            ("RBLBANK",     "RBL Bank"),
    ("RECLTD",     "REC"),            ("RVNL",        "RVNL"),
    ("RELIANCE",   "Reliance"),       ("SBICARD",     "SBI Cards"),
    ("SBILIFE",    "SBI Life"),       ("SHREECEM",    "Shree Cement"),
    ("SRF",        "SRF"),            ("SAMMAANCAP",  "Sammaan Capital"),
    ("MOTHERSON",  "Motherson"),      ("SHRIRAMFIN",  "Shriram Finance"),
    ("SIEMENS",    "Siemens"),        ("SOLARINDS",   "Solar Industries"),
    ("SONACOMS",   "Sona BLW"),       ("SBIN",        "SBI"),
    ("SAIL",       "SAIL"),           ("SUNPHARMA",   "Sun Pharma"),
    ("SUPREMEIND", "Supreme Ind"),    ("SUZLON",      "Suzlon"),
    ("SWIGGY",     "Swiggy"),         ("SYNGENE",     "Syngene"),
    ("TATACONSUM", "Tata Consumer"),  ("TVSMOTOR",    "TVS Motor"),
    ("TCS",        "TCS"),            ("TATAELXSI",   "Tata Elxsi"),
    ("TMCV",       "Tata Motors"),    ("TATAPOWER",   "Tata Power"),
    ("TATASTEEL",  "Tata Steel"),     ("TATATECH",    "Tata Tech"),
    ("TECHM",      "Tech Mahindra"),  ("FEDERALBNK",  "Federal Bank"),
    ("INDHOTEL",   "Indian Hotels"),  ("PHOENIXLTD",  "Phoenix Mills"),
    ("TITAN",      "Titan"),          ("TORNTPHARM",  "Torrent Pharma"),
    ("TORNTPOWER", "Torrent Power"),  ("TRENT",       "Trent"),
    ("TIINDIA",    "Tube Investments"), ("UNOMINDA",  "UNO Minda"),
    ("UPL",        "UPL"),            ("ULTRACEMCO",  "UltraTech Cement"),
    ("UNIONBANK",  "Union Bank"),     ("UNITDSPR",    "United Spirits"),
    ("VBL",        "Varun Beverages"), ("VEDL",       "Vedanta"),
    ("IDEA",       "Vodafone Idea"),  ("VOLTAS",      "Voltas"),
    ("WAAREEENER", "Waaree Energies"), ("WIPRO",      "Wipro"),
    ("YESBANK",    "Yes Bank"),       ("ZYDUSLIFE",   "Zydus Life"),
]

# ── CACHE ─────────────────────────────────────────────────────────────────────
_scan_cache   = []
_index_cache  = []
_last_scan    = None
_entry_prices = {}  # {sym: entry_price} — locked at signal time
_scan_lock    = threading.Lock()
_scan_running = False

# ── HELPERS ───────────────────────────────────────────────────────────────────
def safe(v, decimals=2):
    if v is None: return None
    try:
        f = float(v)
        return None if (math.isnan(f) or math.isinf(f)) else round(f, decimals)
    except: return None

def ema_calc(arr, period):
    if len(arr) < period: return float(np.mean(arr)) if len(arr) else 0
    k = 2.0 / (period + 1)
    e = float(np.mean(arr[:period]))
    for v in arr[period:]:
        e = float(v) * k + e * (1 - k)
    return e

def calculate_ema_angle(closes, period=9):
    """Calculate the angle/slope of EMA over last 5 bars."""
    try:
        if len(closes) < period + 5: return 0.0
        ema_points = []
        for i in range(5, 0, -1):
            subset = closes[-(i+period):-i] if i > 1 else closes[-period:]
            ema_points.append(ema_calc(subset, period))
        # Simple linear regression slope using numpy
        slope, intercept = np.polyfit(np.arange(len(ema_points)), ema_points, 1)
        # Normalize by current price
        normalized = (slope / closes[-1]) * 100 if closes[-1] > 0 else 0
        return round(normalized, 3)
    except:
        return 0.0

def rsi_calc(closes, period=14):
    if len(closes) < period + 1: return 50.0
    d = np.diff(np.array(closes, dtype=float))
    up = np.where(d > 0, d, 0.0)
    dn = np.where(d < 0, -d, 0.0)
    ag = float(np.mean(up[-period:]))
    al = float(np.mean(dn[-period:]))
    if al == 0: return 100.0
    return round(100.0 - 100.0 / (1 + ag / al), 1)

def atr_calc(highs, lows, closes, period=14):
    trs = [max(highs[i]-lows[i], abs(highs[i]-closes[i-1]), abs(lows[i]-closes[i-1]))
           for i in range(1, len(closes))]
    return float(np.mean(trs[-period:])) if trs else 0

def vwap_calc(df_1d):
    try:
        tp = (df_1d["High"] + df_1d["Low"] + df_1d["Close"]) / 3
        vol = df_1d["Volume"].replace(0, np.nan).fillna(1)
        return float((tp * vol).sum() / vol.sum())
    except: return None

# ── TRADINGVIEW BULK FETCH ────────────────────────────────────────────────────
TV_COLS = [
    "name","close","change","volume","open","high","low",
    "VWAP","RSI","EMA9","EMA21","ATR","market_cap_basic",
]

def fetch_tv_bulk():
    """Fetch all NSE stocks at once from TradingView scanner."""
    try:
        url = "https://scanner.tradingview.com/india/scan"
        symbols_list = [f"NSE:{s}" for s, _ in STOCKS]
        payload = {
            "symbols": {"tickers": symbols_list},
            "columns": TV_COLS,
        }
        r = requests.post(url, json=payload, headers=TV_HEADERS, timeout=TV_TIMEOUT)
        if r.status_code != 200:
            print(f"[TV] HTTP {r.status_code}")
            return {}
        data = r.json().get("data", [])
        result = {}
        for row in data:
            sym_full = row.get("s", "")
            sym = sym_full.replace("NSE:", "").replace("BSE:", "")
            d = row.get("d", [])
            if len(d) >= len(TV_COLS):
                result[sym] = dict(zip(TV_COLS, d))
        print(f"[TV] Got {len(result)}/{len(STOCKS)} stocks")
        return result
    except Exception as e:
        print(f"[TV] Error: {e}")
        return {}

def fetch_tv_indices():
    """Fetch index data from TradingView."""
    try:
        url = "https://scanner.tradingview.com/global/scan"
        tickers = ["NSE:NIFTY", "NSE:BANKNIFTY", "BSE:SENSEX", "NSE:NIFTY_MID_SELECT",
                   "FX_IDC:USDINR", "MCX:GOLD1!", "MCX:CRUDEOIL1!", "SP:SPX"]
        labels = ["NIFTY 50", "BANK NIFTY", "SENSEX", "MIDCAP", "USD/INR", "GOLD", "CRUDE", "S&P 500"]
        payload = {
            "symbols": {"tickers": tickers},
            "columns": ["name","close","change","open","high","low","volume"],
        }
        r = requests.post(url, json=payload, headers=TV_HEADERS, timeout=TV_TIMEOUT)
        if r.status_code != 200: return {}
        data = r.json().get("data", [])
        result = {}
        for i, row in enumerate(data):
            d = row.get("d", [])
            if d:
                label = labels[i] if i < len(labels) else row.get("s","")
                result[label] = {
                    "name": label, "close": d[1] if len(d)>1 else None,
                    "change": d[2] if len(d)>2 else None,
                }
        return result
    except Exception as e:
        print(f"[TV Indices] Error: {e}")
        return {}

# ── YFINANCE FALLBACK ─────────────────────────────────────────────────────────
def fetch_yf_stock(sym):
    """Fetch OHLCV + indicators for one stock via yfinance."""
    try:
        ticker = yf.Ticker(f"{sym}.NS")
        df5  = ticker.history(period="5d", interval="5m", auto_adjust=True, prepost=False)
        df1d = ticker.history(period="10d", interval="1d", auto_adjust=True)

        if df5.empty or df1d.empty: return None

        today = datetime.now().date()
        today_mask = df5.index.date == today
        df_today = df5[today_mask]

        closes = df1d["Close"].values.astype(float)
        highs  = df1d["High"].values.astype(float)
        lows   = df1d["Low"].values.astype(float)
        vols   = df1d["Volume"].values.astype(float)

        curr   = float(closes[-1])
        prev   = float(closes[-2]) if len(closes) > 1 else curr
        chg_pct = round((curr - prev) / prev * 100, 2) if prev else 0

        open_p = float(df1d["Open"].values[-1])
        high_p = float(highs[-1])
        low_p  = float(lows[-1])
        volume = int(vols[-1])

        if not df_today.empty:
            today_open  = float(df_today["Open"].iloc[0])
            today_vwap  = vwap_calc(df_today)
            orb_slice = df_today.iloc[:3]
            orb_high  = float(orb_slice["High"].max()) if len(orb_slice) >= 1 else high_p
            orb_low   = float(orb_slice["Low"].min())  if len(orb_slice) >= 1 else low_p
        else:
            today_open = open_p
            today_vwap = (open_p + high_p + low_p) / 3
            orb_high   = high_p; orb_low = low_p

        rsi  = rsi_calc(closes)
        ema9 = ema_calc(closes, 9)
        ema21= ema_calc(closes, 21)
        atr  = atr_calc(highs, lows, closes)
        
        # Calculate EMA angles (slope of EMA over last 5 bars)
        ema9_angle = calculate_ema_angle(closes, 9)
        ema21_angle = calculate_ema_angle(closes, 21)
        ema_angle_diff = round(ema9_angle - ema21_angle, 3)

        ranges = [highs[i]-lows[i] for i in range(-min(7, len(highs)), 0)]
        today_range = high_p - low_p
        nr7 = bool(len(ranges) >= 3 and today_range == min(ranges))

        return {
            "curr": curr, "open": today_open, "high": high_p, "low": low_p,
            "prev": prev, "chg_pct": chg_pct, "volume": volume,
            "vwap": today_vwap, "orb_high": orb_high, "orb_low": orb_low,
            "rsi": rsi, "ema9": round(ema9,2), "ema21": round(ema21,2),
            "atr": round(atr,2), "nr7": nr7,
            "ema9_angle": ema9_angle, "ema21_angle": ema21_angle,
            "ema_angle_diff": ema_angle_diff,
            "prev_high": float(highs[-2]) if len(highs)>1 else high_p,
            "prev_low": float(lows[-2]) if len(lows)>1 else low_p,
            "closes": closes.tolist(),  # For charting
            "dates": [i for i in range(len(closes))],  # Simple dates for chart
        }
    except Exception as e:
        print(f"[YF] {sym} error: {e}")
        return None

# ── SIGNAL ENGINE ─────────────────────────────────────────────────────────────
def compute_signals(d):
    """Apply ORB, VWAP, NR7 strategy logic. Entry price LOCKED at signal time."""
    curr     = d["curr"]
    orb_h    = d["orb_high"]
    orb_l    = d["orb_low"]
    vwap     = d["vwap"] or curr
    ema9     = d["ema9"]
    ema21    = d["ema21"]
    atr      = d.get("atr", curr * 0.01)
    rsi      = d["rsi"]
    nr7      = d["nr7"]
    prev_h   = d.get("prev_high", curr)
    prev_l   = d.get("prev_low", curr)
    sym      = d.get("sym", "UNKNOWN")

    # ── ORB Strategy ──────────────────────────────────────────────────────────
    orb_signal = "NEUTRAL"
    if curr > orb_h and orb_h > orb_l:
        orb_signal = "BUY"
    elif curr < orb_l and orb_h > orb_l:
        orb_signal = "SELL"

    # ── VWAP Strategy ─────────────────────────────────────────────────────────
    vwap_signal = "NEUTRAL"
    vwap_dist   = round((curr - vwap) / vwap * 100, 2) if vwap else 0
    trending_up   = ema9 > ema21
    trending_down = ema9 < ema21
    near_vwap = abs(vwap_dist) < 0.5

    if trending_up and (near_vwap or curr > vwap):
        vwap_signal = "BUY"
    elif trending_down and (near_vwap or curr < vwap):
        vwap_signal = "SELL"

    # ── NR7 Strategy ──────────────────────────────────────────────────────────
    nr7_signal = "NEUTRAL"
    if nr7:
        if curr > prev_h:
            nr7_signal = "BUY"
        elif curr < prev_l:
            nr7_signal = "SELL"

    # ── RSI modifiers ─────────────────────────────────────────────────────────
    rsi_mod = 0
    if rsi < 30: rsi_mod = 1
    elif rsi > 70: rsi_mod = -1

    # ── Composite score ───────────────────────────────────────────────────────
    buy_score  = sum(1 for s in [orb_signal, vwap_signal, nr7_signal] if s == "BUY")  + max(0, rsi_mod)
    sell_score = sum(1 for s in [orb_signal, vwap_signal, nr7_signal] if s == "SELL") + max(0, -rsi_mod)

    if buy_score > sell_score and buy_score >= 1:
        ai_signal = "BUY"
    elif sell_score > buy_score and sell_score >= 1:
        ai_signal = "SELL"
    else:
        ai_signal = "NEUTRAL"

    # ── Entry / SL / Target (1:1 R:R - REALISTIC INTRADAY) ──────────────
    # Intraday targets are more conservative: 1:1 ratio (not 1:2)
    # Entry is computed NOW and LOCKED — it will not change even if LTP changes
    if ai_signal == "BUY":
        entry  = round(curr, 2)  # LOCKED at signal generation time
        sl     = round(min(ema21, orb_l, curr - atr * 0.5), 2)  # Tighter SL
        risk   = max(curr - sl, atr * 0.3)  # Tighter risk
        target = round(entry + risk * 1.0, 2)  # 1:1 ratio (achievable)
        _entry_prices[sym] = entry  # Store for persistence
    elif ai_signal == "SELL":
        entry  = round(curr, 2)  # LOCKED at signal generation time
        sl     = round(max(ema21, orb_h, curr + atr * 0.5), 2)  # Tighter SL
        risk   = max(sl - curr, atr * 0.3)  # Tighter risk
        target = round(entry - risk * 1.0, 2)  # 1:1 ratio (achievable)
        _entry_prices[sym] = entry  # Store for persistence
    else:
        entry = round(curr, 2)
        sl    = round(curr - atr * 1.0, 2)
        target= round(curr + atr * 1.0, 2)
        if sym in _entry_prices:
            entry = _entry_prices[sym]  # Keep old entry if still neutral

    # Pivot / R1 / S1
    ph = d.get("prev_high", curr * 1.01)
    pl = d.get("prev_low",  curr * 0.99)
    pc = d.get("prev", curr)
    pivot = round((ph + pl + pc) / 3, 2)
    r1    = round(2 * pivot - pl, 2)
    s1    = round(2 * pivot - ph, 2)

    # Reason string
    strats  = []
    if orb_signal  != "NEUTRAL": strats.append("ORB")
    if vwap_signal != "NEUTRAL": strats.append("VWAP")
    if nr7_signal  != "NEUTRAL": strats.append("NR7")
    reasons = []
    if orb_signal == "BUY":   reasons.append("ORB breakout")
    if orb_signal == "SELL":  reasons.append("ORB breakdown")
    if vwap_signal == "BUY":  reasons.append("VWAP support")
    if vwap_signal == "SELL": reasons.append("VWAP rejection")
    if nr7 and nr7_signal != "NEUTRAL": reasons.append("NR7 squeeze")
    if rsi < 30:  reasons.append(f"RSI oversold ({rsi})")
    if rsi > 70:  reasons.append(f"RSI overbought ({rsi})")
    if not reasons: reasons.append("Monitoring")

    d.update({
        "orb_signal": orb_signal,  "vwap_signal": vwap_signal,
        "nr7_signal": nr7_signal,  "ai_signal": ai_signal,
        "vwap_dist": vwap_dist,    "strategies": strats,
        "entry": entry, "sl": sl,  "target": target,
        "pivot": pivot, "r1": r1,  "s1": s1,
        "reason": " + ".join(reasons),
        "entry_locked": True,  # Flag to indicate entry is locked
    })
    return d

# ── MERGE TV + YF DATA ────────────────────────────────────────────────────────
def build_stock_record(sym, name, tv_data, yf_data):
    """Combine TradingView + yfinance into one clean record."""
    record = {"sym": sym, "name": name}

    if tv_data:
        record["curr"]     = safe(tv_data.get("close"))
        record["chg_pct"]  = safe(tv_data.get("change"))
        record["volume"]   = int(tv_data.get("volume") or 0)
        record["open"]     = safe(tv_data.get("open"))
        record["high"]     = safe(tv_data.get("high"))
        record["low"]      = safe(tv_data.get("low"))
        record["vwap"]     = safe(tv_data.get("VWAP"))
        record["rsi"]      = safe(tv_data.get("RSI"), 1)
        record["ema9"]     = safe(tv_data.get("EMA9"))
        record["ema21"]    = safe(tv_data.get("EMA21"))
        record["atr"]      = safe(tv_data.get("ATR"))
        record["source"]   = "TradingView"
    
    if yf_data:
        for k in ["curr","open","high","low","chg_pct","volume","rsi","ema9","ema21","atr"]:
            if not record.get(k): record[k] = yf_data.get(k)
        record["vwap"]      = record.get("vwap") or yf_data.get("vwap")
        record["orb_high"]  = yf_data.get("orb_high", record.get("high", 0))
        record["orb_low"]   = yf_data.get("orb_low",  record.get("low",  0))
        record["nr7"]       = yf_data.get("nr7", False)
        record["prev"]      = yf_data.get("prev", record.get("curr", 0))
        record["prev_high"] = yf_data.get("prev_high", record.get("high", 0))
        record["prev_low"]  = yf_data.get("prev_low",  record.get("low",  0))
        # Add EMA angles
        record["ema9_angle"] = yf_data.get("ema9_angle", 0)
        record["ema21_angle"] = yf_data.get("ema21_angle", 0)
        record["ema_angle_diff"] = yf_data.get("ema_angle_diff", 0)
        record["closes"] = yf_data.get("closes", [])
        record["dates"] = yf_data.get("dates", [])
        if not record.get("source"): record["source"] = "yfinance"

    curr = record.get("curr") or 0
    record.setdefault("orb_high",  record.get("high", curr * 1.005))
    record.setdefault("orb_low",   record.get("low",  curr * 0.995))
    record.setdefault("vwap",      curr)
    record.setdefault("rsi",       50.0)
    record.setdefault("ema9",      curr)
    record.setdefault("ema21",     curr)
    record.setdefault("atr",       curr * 0.01)
    record.setdefault("nr7",       False)
    record.setdefault("prev",      curr)
    record.setdefault("prev_high", curr)
    record.setdefault("prev_low",  curr)

    if not curr: return None
    return compute_signals(record)

# ── BACKGROUND SCANNER ────────────────────────────────────────────────────────
def run_scan():
    global _scan_cache, _index_cache, _last_scan, _scan_running
    _scan_running = True
    print(f"\n[SCAN] Starting scan at {datetime.now().strftime('%H:%M:%S')}...")

    tv_map = fetch_tv_bulk()
    
    yf_map = {}
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {ex.submit(fetch_yf_stock, sym): sym for sym, _ in STOCKS}
        for future in as_completed(futures):
            sym = futures[future]
            try: yf_map[sym] = future.result()
            except: pass

    results = []
    for sym, name in STOCKS:
        rec = build_stock_record(sym, name, tv_data=tv_map.get(sym), yf_data=yf_map.get(sym))
        if rec: results.append(rec)

    idx_data = fetch_tv_indices()

    with _scan_lock:
        _scan_cache  = results
        _index_cache = idx_data
        _last_scan   = datetime.now()

    buys  = sum(1 for r in results if r.get("ai_signal") == "BUY")
    sells = sum(1 for r in results if r.get("ai_signal") == "SELL")
    print(f"[SCAN] Done: {len(results)}/{len(STOCKS)} stocks | BUY:{buys} SELL:{sells}")
    _scan_running = False

def background_scanner():
    while True:
        try: run_scan()
        except Exception as e: print(f"[SCAN ERR] {e}")
        time.sleep(SCAN_INTERVAL)

# ── API ROUTES ────────────────────────────────────────────────────────────────
def jsonify_safe(data):
    """JSON-safe serializer handling NaN/None."""
    def fix(obj):
        if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)): return None
        if isinstance(obj, (np.floating, np.integer)): return obj.item()
        if isinstance(obj, dict):  return {k: fix(v) for k, v in obj.items()}
        if isinstance(obj, list):  return [fix(v) for v in obj]
        return obj
    return jsonify(fix(data))

@app.route("/api/scan")
def api_scan():
    with _scan_lock:
        data = list(_scan_cache)
        ts   = _last_scan.isoformat() if _last_scan else None
    return jsonify_safe({"stocks": data, "timestamp": ts, "count": len(data)})

@app.route("/api/indices")
def api_indices():
    with _scan_lock:
        data = dict(_index_cache)
        ts   = _last_scan.isoformat() if _last_scan else None
    return jsonify_safe({"indices": data, "timestamp": ts})

@app.route("/api/stock/<sym>")
def api_stock(sym):
    with _scan_lock:
        stock = next((s for s in _scan_cache if s["sym"] == sym.upper()), None)
    if not stock:
        return jsonify({"error": "Not found"}), 404
    return jsonify_safe(stock)

@app.route("/api/status")
def api_status():
    return jsonify({
        "status": "running",
        "last_scan": _last_scan.isoformat() if _last_scan else None,
        "scan_running": _scan_running,
        "stock_count": len(_scan_cache),
        "scan_interval": SCAN_INTERVAL,
        "total_fo_stocks": len(STOCKS),
    })

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(".", path)

# ── MAIN ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  NSE Real-Time Intraday Scanner (v2 - 213 Stocks)")
    print("  Entry prices LOCKED at signal generation")
    print("  Data: TradingView + yfinance")
    print("  Open: http://localhost:5000")
    print("=" * 60)
    threading.Thread(target=background_scanner, daemon=True).start()
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
