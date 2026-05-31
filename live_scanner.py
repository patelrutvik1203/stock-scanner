import yfinance as yf
import pandas as pd
import json
import os
import requests
import warnings
from datetime import datetime

warnings.filterwarnings('ignore')

# NIFTY Sample - Expanded List for production
stocks = {
    'HDFCBANK.NS': 'Banking', 'ICICIBANK.NS': 'Banking', 'SBIN.NS': 'Banking', 
    'M&M.NS': 'Auto', 'TATAMOTORS.NS': 'Auto', 'HAL.NS': 'CapGoods', 
    'TCS.NS': 'IT', 'ITC.NS': 'FMCG', 'RELIANCE.NS': 'Energy', 
    'LT.NS': 'CapGoods', 'SUNPHARMA.NS': 'Pharma', 'TATASTEEL.NS': 'Metals',
    'INFY.NS': 'IT', 'BAJFINANCE.NS': 'Banking', 'MARUTI.NS': 'Auto'
}

astro_weights = {
    'Banking': 90, 'Auto': 85, 'CapGoods': 85, 'Metals': 80, 
    'Energy': 65, 'Pharma': 45, 'IT': 30, 'FMCG': 25
}

tp_pct = 0.06 # +6% Trend Rider
sl_pct = 0.12 # -12% Stop Loss

print("Running Daily Astro-Quant Scan...")
data = yf.download(list(stocks.keys()), period='1y', progress=False)

results = []
alert_messages = []

for ticker, sector in stocks.items():
    try:
        if isinstance(data.columns, pd.MultiIndex):
            df = data.xs(ticker, axis=1, level=1).copy()
        else:
            df = data.copy()
            
        df = df.dropna()
        if df.empty: continue
            
        close = float(df['Close'].iloc[-1])
        
        # Technicals
        df['delta'] = df['Close'].diff()
        df['gain'] = df['delta'].clip(lower=0)
        df['loss'] = -df['delta'].clip(upper=0)
        df['rs'] = df['gain'].rolling(14).mean() / df['loss'].rolling(14).mean()
        df['rsi'] = 100 - (100 / (1 + df['rs']))
        
        df['sma_200'] = df['Close'].rolling(200).mean()
        df['std'] = df['Close'].rolling(20).std()
        df['lower_bb'] = df['Close'].rolling(20).mean() - (2 * df['std'])
        
        current_rsi = float(df['rsi'].iloc[-1])
        current_sma200 = float(df['sma_200'].iloc[-1])
        current_lower_bb = float(df['lower_bb'].iloc[-1])
        a_score = astro_weights.get(sector, 50)
        
        # Calculate Base Score (UI Display)
        tech_score = 50
        if 55 <= current_rsi <= 70: tech_score += 40
        elif 45 <= current_rsi < 55: tech_score += 20
        elif current_rsi > 70: tech_score -= 10
        elif current_rsi < 35: tech_score += 30
        final_score = int((tech_score * 0.4) + (a_score * 0.6))
        
        # Sniper Setup Condition (Trend Rider)
        signal = "HOLD"
        if a_score >= 80 and close > current_sma200 and current_rsi < 35 and close <= (current_lower_bb * 1.02):
            signal = "STRONG BUY"
            alert_messages.append(f"🚀 *{ticker.replace('.NS','')}* ({sector})\nPrice: ₹{close:.2f}\nRSI: {current_rsi:.1f} (Oversold)\nAstro: {a_score}/100\nTarget: ₹{close*(1+tp_pct):.2f}\nStop: ₹{close*(1-sl_pct):.2f}")
        elif final_score >= 65:
            signal = "BUY"
        elif final_score < 45:
            signal = "AVOID/SELL"
            
        results.append({
            "ticker": ticker.replace('.NS', ''),
            "sector": sector,
            "price": round(close, 2),
            "rsi": round(current_rsi, 1),
            "astro": a_score,
            "score": final_score,
            "signal": signal
        })
    except Exception as e:
        pass

results.sort(key=lambda x: x['score'], reverse=True)

# Save to JSON for the website
with open('scan_results.json', 'w') as f:
    json.dump(results, f, indent=4)
print("Data saved to scan_results.json")

# Send Telegram Alert
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID and alert_messages:
    print("Sending Telegram Notification...")
    msg = "🔮 *Astro-Quant Daily Scan Triggered!*\n\n" + "\n\n".join(alert_messages)
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"}
    resp = requests.post(url, json=payload)
    if resp.status_code == 200:
        print("Telegram alert sent successfully!")
    else:
        print("Failed to send Telegram alert:", resp.text)
elif not TELEGRAM_TOKEN:
    print("No Telegram Token found. Skipping notifications.")
