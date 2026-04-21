# NSE Real-Time Scanner - Quick Start

## Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

## Step 2: Run Server
```bash
python server_v2.py
# or: python server.py (if you renamed server_v2.py)
```

Expected output:
```
============================================================
  NSE Real-Time Intraday Scanner (v2 - 213 Stocks)
  Entry prices LOCKED at signal generation
  Data: TradingView + yfinance
  Open: http://localhost:5000
============================================================

[SCAN] Starting scan at 14:30:45...
[TV] Got 150/213 stocks
[SCAN] Done: 150 stocks | BUY:42 SELL:18
```

## Step 3: Open Browser
```
http://localhost:5000
```

## Features

- ✅ **213 F&O stocks** scanned in real-time
- ✅ **Entry prices locked** (don't change with LTP)
- ✅ **ORB, VWAP, NR7** strategy signals
- ✅ **Live ticker** with indices
- ✅ **Detail panel** with full analysis
- ✅ **Real data** from TradingView + yfinance

## Data Updates

- Refreshes every **60 seconds** automatically
- Real-time LTP from **TradingView**
- Intraday candles from **yfinance**
- Entry/SL/Target locked at signal time

## Troubleshooting

### "Module not found"
```bash
pip install flask flask-cors yfinance pandas numpy requests --break-system-packages
```

### "Port 5000 already in use"
```bash
# Kill existing process
pkill -f "python server"
# Or use different port
python server_v2.py --port 8080
```

### "TradingView API blocked"
- This is expected in cloud environments
- Works fine on your local machine or Render.com

## GitHub Deployment

See `GITHUB_DEPLOYMENT.md` for complete guide to deploy on:
- ✅ Render.com (RECOMMENDED - free tier)
- ✅ Railway.app
- ✅ GitHub Pages (static only)

## Files Included

| File | Purpose |
|------|---------|
| `server_v2.py` | Flask backend (213 stocks, locked entries) |
| `index.html` | Web UI (responsive design) |
| `requirements.txt` | Python dependencies |
| `Procfile` | Cloud deployment config |
| `GITHUB_DEPLOYMENT.md` | Complete GitHub + hosting guide |
| `QUICK_START.md` | This file |

---

**Need help?** Check GITHUB_DEPLOYMENT.md for detailed setup & troubleshooting.
