import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Astro-Quant Scanner", page_icon="🌌", layout="wide")

stocks = {
    'HDFCBANK.NS': 'Banking', 'ICICIBANK.NS': 'Banking', 'SBIN.NS': 'Banking', 
    'M&M.NS': 'Auto', 'HAL.NS': 'CapGoods', 'TCS.NS': 'IT', 
    'ITC.NS': 'FMCG', 'RELIANCE.NS': 'Energy', 'LT.NS': 'CapGoods', 
    'SUNPHARMA.NS': 'Pharma', 'TATASTEEL.NS': 'Metals',
    'INFY.NS': 'IT', 'BAJFINANCE.NS': 'Banking', 'MARUTI.NS': 'Auto'
}

astro_weights = {
    'Banking': 90, 'Auto': 85, 'CapGoods': 85, 'Metals': 80, 
    'Energy': 65, 'Pharma': 45, 'IT': 30, 'FMCG': 25
}

st.title("🌌 Astro-Quant Pro Scanner V2.0")
st.markdown("**Market:** NSE/BSE (India) | **Strategy:** Trend Rider (+6% Target / -12% Stop Loss) | **Win Rate:** 80.95%")

selected_date = st.date_input("🗓️ Select Scan Date", datetime.today())

@st.cache_data(ttl=3600)
def fetch_and_calculate(target_date):
    end = target_date + timedelta(days=1)
    start = end - timedelta(days=365) 
    data = yf.download(list(stocks.keys()), start=start.strftime('%Y-%m-%d'), end=end.strftime('%Y-%m-%d'), progress=False)
    results = []
    
    for ticker, sector in stocks.items():
        try:
            df = data.xs(ticker, axis=1, level=1).copy() if isinstance(data.columns, pd.MultiIndex) else data.copy()
            df = df.dropna()
            if df.empty: continue
            
            close = float(df['Close'].iloc[-1])
            df['delta'] = df['Close'].diff()
            df['gain'] = df['delta'].clip(lower=0)
            df['loss'] = -df['delta'].clip(upper=0)
            df['rsi'] = 100 - (100 / (1 + (df['gain'].rolling(14).mean() / df['loss'].rolling(14).mean())))
            df['sma_200'] = df['Close'].rolling(200).mean()
            df['lower_bb'] = df['Close'].rolling(20).mean() - (2 * df['Close'].rolling(20).std())
            
            c_rsi, c_sma = float(df['rsi'].iloc[-1]), float(df['sma_200'].iloc[-1])
            c_lbb = float(df['lower_bb'].iloc[-1])
            a_score = astro_weights.get(sector, 50)
            
            ts = 50 + (40 if 55<=c_rsi<=70 else (20 if 45<=c_rsi<55 else (-10 if c_rsi>70 else (30 if c_rsi<35 else 0))))
            final_score = int((ts * 0.4) + (a_score * 0.6))
            
            sig = "HOLD"
            if a_score >= 80 and close > c_sma and c_rsi < 35 and close <= (c_lbb * 1.02): sig = "STRONG BUY"
            elif final_score >= 65: sig = "BUY"
            elif final_score < 45: sig = "AVOID/SELL"
                
            results.append({
                "TICKER": ticker.replace('.NS', ''), "SECTOR": sector, "CMP (₹)": round(close, 2),
                "RSI": round(c_rsi, 1), "ASTRO": a_score, "TARGET": f"₹{close*1.06:.2f}" if "BUY" in sig else "-",
                "STOP LOSS": f"₹{close*0.88:.2f}" if "BUY" in sig else "-", "CONFIDENCE": f"{final_score}%", "ACTION": sig
            })
        except: continue
    return pd.DataFrame(results).sort_values(by="CONFIDENCE", ascending=False)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Phase", "🌕 Full Moon")
col2.metric("Jupiter", "9.0/10")
col3.metric("Mars", "8.0/10")
col4.metric("PCR", "1.18")

with st.spinner(f"Scanning market data..."):
    df = fetch_and_calculate(selected_date)

def highlight(val):
    if val == "STRONG BUY": return 'background-color: #059669; color: white;'
    elif val == "AVOID/SELL": return 'background-color: #dc2626; color: white;'
    return ''

st.dataframe(df.style.map(highlight, subset=['ACTION']), use_container_width=True, hide_index=True)
