# NSE Scanner v2 - Complete Package

## What You Have

All files needed to run a **real-time NSE intraday scanner** with 213 stocks, deployed on GitHub.

## Files Included

| File | What It Does | Size |
|------|---|---|
| **server_v2.py** | Flask backend (213 stocks, locked entries, real data) | 27 KB |
| **index.html** | Web UI (dark theme, responsive, real-time) | 40 KB |
| **requirements.txt** | Python dependencies (Flask, yfinance, etc.) | 92 B |
| **Procfile** | Cloud deployment config (Render/Railway) | 22 B |
| **README.md** | Complete documentation | 8 KB |
| **.gitignore** | Git ignore rules | 1 KB |
| **GITHUB_DEPLOYMENT.md** | Step-by-step GitHub + hosting setup | 6.4 KB |
| **QUICK_START.md** | Quick local setup guide | 2.2 KB |

## What's Fixed (v2 vs Demo)

### ✅ 213 Stocks (Was 88)
- Added complete NSE F&O universe
- All indices covered

### ✅ Locked Entry Prices
- Entry computed at signal time
- Doesn't change when LTP changes
- Shows "Entry Locked" flag in API

### ✅ Real Data
- TradingView Scanner API (real-time LTP, VWAP, RSI)
- yfinance 5-min candles (real ORB, NR7 detection)
- Merge both sources for best accuracy

## 3-Minute Setup (Local)

```bash
# 1. Copy all files to a folder
mkdir nse-scanner
cd nse-scanner
# Copy: server_v2.py, index.html, requirements.txt, Procfile, .gitignore

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run server
python server_v2.py

# 4. Open browser
# http://localhost:5000
```

That's it! You now have:
- 🔴 Live NSE scanner
- 📊 213 F&O stocks
- 💹 Real TradingView + yfinance data
- ⚡ Auto-refreshing every 60 seconds

## GitHub Upload

1. **Create GitHub repo**:
   - Go to https://github.com/new
   - Name: `nse-scanner`
   - Public
   - Add README

2. **Upload files**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/nse-scanner.git
   cd nse-scanner
   # Copy all 8 files here
   git add .
   git commit -m "Add NSE scanner v2"
   git push origin main
   ```

3. **Deploy on Render** (FREE tier):
   - Go to https://render.com
   - Click "New +" → "Web Service"
   - Connect GitHub repo
   - Name: nse-scanner
   - Build: `pip install -r requirements.txt`
   - Start: `python server_v2.py`
   - Click "Create Web Service"
   
   Takes 2-3 minutes. You get:
   - Public URL (https://nse-scanner.onrender.com)
   - Real data (TradingView + yfinance)
   - Auto-refresh every 60 seconds
   - Free forever (if under 750 hrs/month)

## How to Use

### Local (Development)
```bash
python server_v2.py
# Open http://localhost:5000
# Refresh data manually with REFRESH button
# Auto-refreshes every 60 seconds
```

### Cloud (Production)
```bash
# After deploying to Render/Railway
# Open https://nse-scanner.onrender.com
# Same features as local
# Accessible from anywhere
```

## Features Overview

| Feature | Details |
|---------|---------|
| **Stocks** | 213 NSE F&O (complete universe) |
| **Strategies** | ORB, VWAP, NR7 (3-in-1) |
| **Signals** | BUY / SELL / NEUTRAL |
| **Data** | TradingView + yfinance (real-time) |
| **Entry** | Locked at signal time (won't change) |
| **Target** | 1:2 Risk:Reward |
| **Refresh** | Every 60 seconds auto |
| **Table** | Filter by signal, strategy, search |
| **Details** | Click stock → full analysis panel |
| **Cost** | FREE (no paid APIs) |

## API Endpoints

Once running, use these:

```bash
# All stocks
curl http://localhost:5000/api/scan | jq

# Indices
curl http://localhost:5000/api/indices | jq

# One stock
curl http://localhost:5000/api/stock/RELIANCE | jq

# Health
curl http://localhost:5000/api/status | jq
```

## Key Advantages

- ✅ **213 stocks** — complete coverage
- ✅ **Locked entries** — professional approach
- ✅ **Real data** — TradingView + yfinance
- ✅ **Free hosting** — Render.com
- ✅ **No authentication** — just open and use
- ✅ **Responsive UI** — works on mobile too
- ✅ **1:2 R:R** — proper risk management
- ✅ **MIT licensed** — use freely

## Important Warnings

⚠️ **Trading Risk**
- Signals are **educational only**
- Not financial advice
- Past performance ≠ future
- **Always use stop losses**
- **Never risk >2% per trade**
- **Paper trade first**

## Troubleshooting

**Problem**: `ModuleNotFoundError: No module named 'flask'`
```bash
pip install -r requirements.txt --break-system-packages
```

**Problem**: `Connection refused: http://localhost:5000`
- Is server running? `python server_v2.py`
- Is port 5000 free? `lsof -i :5000`

**Problem**: Only 88 stocks showing
- Are you using `server_v2.py`?
- Clear browser cache (Ctrl+Shift+Delete)
- Restart server

**Problem**: TradingView data not showing
- Works on Render (free tier)
- On local, yfinance fallback works
- Check internet connection

See **GITHUB_DEPLOYMENT.md** for detailed troubleshooting.

## Next Steps

1. ✅ **Setup locally** (5 minutes)
2. ✅ **Test it** (refresh, click stocks)
3. ✅ **Upload to GitHub** (2 minutes)
4. ✅ **Deploy to Render** (3 minutes)
5. ✅ **Share with others** (public URL)

## Files You Need to Keep

- `server_v2.py` (backend logic)
- `index.html` (frontend UI)
- `requirements.txt` (dependencies)
- `Procfile` (cloud deployment)

## Files That Are Optional

- `.gitignore` (Git configuration)
- `README.md` (Documentation)
- `GITHUB_DEPLOYMENT.md` (Detailed setup)
- `QUICK_START.md` (Quick reference)

## Version Info

- **Current**: v2.0
- **Stocks**: 213 NSE F&O
- **Strategies**: ORB, VWAP, NR7
- **Data**: Real-time (TradingView + yfinance)
- **Entry Locking**: YES ✅

## Support

- **Local issues**: See QUICK_START.md
- **GitHub setup**: See GITHUB_DEPLOYMENT.md
- **Trading questions**: Refer to README.md
- **Bugs**: File GitHub issue

## License

MIT — Use freely, no restrictions

---

**You're all set!** 

Start with local setup, then deploy to GitHub + Render in 10 minutes total.

Questions? Check the docs. Ready? Run `python server_v2.py` 🚀
