# NSE Real-Time Intraday Scanner - Complete Setup & GitHub Deployment

## What's Fixed (v2)

✅ **213 stocks** (complete NSE F&O universe)  
✅ **Locked entry prices** (doesn't change when LTP changes)  
✅ **ORB, VWAP, NR7** strategies with real data  
✅ **TradingView + yfinance** data sources  

---

## Quick Start (Local)

### 1. Download Files
```bash
# Create a folder
mkdir nse-scanner
cd nse-scanner

# Copy these 2 files into the folder:
# - server_v2.py (rename to server.py or keep as is)
# - index.html
```

### 2. Install Dependencies
```bash
pip install flask flask-cors yfinance pandas numpy requests
```

### 3. Run Server
```bash
python server_v2.py
# or: python server.py
```

### 4. Open Browser
```
http://localhost:5000
```

---

## GitHub Deployment (Free Hosting)

### Option A: GitHub Pages (Static Only - No Backend)

GitHub Pages only hosts **static HTML/CSS/JS**. If you use this, the scanner will use **simulated data** (no real-time):

```bash
# 1. Create a new GitHub repo: https://github.com/new
#    Name it: "nse-scanner"

# 2. Clone it locally
git clone https://github.com/YOUR_USERNAME/nse-scanner.git
cd nse-scanner

# 3. Copy index.html into the repo
cp index.html .

# 4. Push to GitHub
git add .
git commit -m "Initial commit - NSE Scanner"
git push origin main

# 5. Enable GitHub Pages
# Go to Settings → Pages → Source: main branch → Save
# Your site: https://YOUR_USERNAME.github.io/nse-scanner/
```

**Problem**: No backend = no real TradingView/yfinance data  
**Solution**: See Option B or C

---

### Option B: Render.com (Free Tier - Backend Included) ⭐ RECOMMENDED

Render.com offers **free tier** with backend support:

```bash
# 1. Create account: https://render.com

# 2. Create a new GitHub repo (same as above)
git clone https://github.com/YOUR_USERNAME/nse-scanner.git
cd nse-scanner

# 3. Copy these 3 files:
cp server_v2.py server.py
cp index.html .
# Create requirements.txt:
```

Create `requirements.txt`:
```
flask==3.1.3
flask-cors==4.0.0
yfinance==0.2.33
pandas==3.0.1
numpy==2.4.3
requests==2.33.0
```

Create `Procfile`:
```
web: python server.py
```

Create `.gitignore`:
```
__pycache__/
*.py[cod]
venv/
.DS_Store
```

```bash
# 4. Push to GitHub
git add .
git commit -m "Add scanner with backend"
git push origin main

# 5. Create Render service
# - Go to https://render.com
# - Click "New +" → "Web Service"
# - Connect your GitHub repo
# - Name: nse-scanner
# - Runtime: Python 3
# - Build command: pip install -r requirements.txt
# - Start command: python server.py
# - Click "Create Web Service"

# Your site: https://nse-scanner.onrender.com (or custom name)
```

**Time to deploy**: 2-3 minutes  
**Real-time data**: YES (TradingView + yfinance)  
**Cost**: FREE (if under 750 hrs/month)

---

### Option C: Railway.app (Alternative Free Tier)

```bash
# 1. Create account: https://railway.app

# 2. Same setup as Option B (server.py, requirements.txt, Procfile)

# 3. Install Railway CLI
npm install -g @railway/cli
# or: brew install railway (macOS)

# 4. From repo folder:
railway login
railway init
railway up
```

Your site gets a public URL automatically.

---

### Option D: Heroku (Free Tier Removed - Paid Alternatives)

Heroku removed free tier in Nov 2022. Use Render or Railway instead.

---

## Environment Variables (If Needed)

If you want to limit API calls:

Create `.env`:
```
FLASK_ENV=production
FLASK_DEBUG=0
SCAN_INTERVAL=60
```

In `server.py`, add:
```python
import os
from dotenv import load_dotenv
load_dotenv()
SCAN_INTERVAL = int(os.getenv('SCAN_INTERVAL', 60))
```

---

## File Structure

```
nse-scanner/
├── server.py              # Flask backend (rename from server_v2.py)
├── index.html             # Frontend UI
├── requirements.txt       # Python dependencies
├── Procfile              # (For Render/Railway)
├── .gitignore            # (Optional)
└── README.md             # (This file)
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'flask'"
```bash
pip install -r requirements.txt --break-system-packages
# Or use virtual environment:
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### "Connection refused - localhost:5000"
- Make sure `python server.py` is running in another terminal
- Check `http://localhost:5000` is open

### "TradingView API returns 403"
- This happens in cloud environments with network restrictions
- Render/Railway usually bypass this
- If still blocked, add user-agent spoofing in server.py (already included)

### Entry price keeps changing
- Make sure you're running `server_v2.py` (or copy the `_entry_prices` logic)
- Entry is locked at signal generation, not current LTP

### Only seeing 88 stocks instead of 213
- Delete cached data, restart server
- Make sure you're using updated STOCKS list (v2)

---

## API Endpoints

Once running, these endpoints are available:

```bash
# All stocks with signals
curl http://localhost:5000/api/scan

# Market indices
curl http://localhost:5000/api/indices

# Single stock detail
curl http://localhost:5000/api/stock/RELIANCE

# Server health
curl http://localhost:5000/api/status
```

---

## Live Example

Deployed on Render:
```
https://nse-scanner.onrender.com
```
(Replace with your own Render/Railway URL)

---

## Custom Domain (Optional)

After deploying to Render:

1. Buy domain (GoDaddy, Namecheap, etc.)
2. Go to Render dashboard → your service → Settings → Custom Domain
3. Add your domain
4. Update DNS records as shown (CNAME pointing to Render)

---

## Security Notes

- **No authentication** — add if exposing publicly
- **Rate limiting** — Render has built-in limits
- **Data privacy** — scanner doesn't store personal data
- **CORS** — configured for localhost:5000, update for your domain

---

## Performance

- **Scan frequency**: Every 60 seconds
- **Response time**: <2 seconds (Render cold start ~10s)
- **Data freshness**: Real-time from TradingView (fast) + 5-min intraday from yfinance
- **Stock coverage**: 213 NSE F&O stocks

---

## Support & Contribution

Found a bug? Create an issue:
```
https://github.com/YOUR_USERNAME/nse-scanner/issues
```

Want to improve? Fork & PR:
```
https://github.com/YOUR_USERNAME/nse-scanner/compare
```

---

## License

MIT License - use freely for personal/commercial use

---

**Last Updated**: 2026-04-21  
**Version**: v2 (213 stocks, locked entries)
