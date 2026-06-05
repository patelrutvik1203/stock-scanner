import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore')

st.set_page_config(page_title="Astro-Quant Pro", page_icon="🌌", layout="wide", initial_sidebar_state="collapsed")

st.write(
    """<style>
    .stApp { background-color: #0b1120; color: #f8fafc; }
    .gradient-text { background: linear-gradient(90deg, #3b82f6, #10b981); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.8rem; font-weight: 900; text-align: center; padding-top: 10px; margin-bottom: 0px; letter-spacing: 1px; }
    .sub-text { text-align: center; color: #94a3b8; font-size: 1.1rem; margin-bottom: 30px; }
    .index-ribbon { display: flex; justify-content: center; flex-wrap: wrap; gap: 20px; background: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155; margin-bottom: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.4); }
    .index-card { text-align: center; flex: 1; min-width: 150px; }
    .index-card:not(:last-child) { border-right: 1px solid #334155; }
    .index-name { font-size: 0.9rem; color: #94a3b8; text-transform: uppercase; font-weight: bold; margin-bottom: 5px; }
    .index-price { font-size: 1.6rem; font-weight: bold; color: #f8fafc; }
    .green { color: #10b981; } .red { color: #ef4444; }
    .section-title { font-size: 1.5rem; font-weight: 800; color: #e2e8f0; margin-top: 40px; margin-bottom: 5px; display: flex; align-items: center; gap: 10px; }
    .custom-table-container { background-color: #1e293b; border-radius: 12px; border: 1px solid #334155; padding: 20px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3); margin-bottom: 20px; overflow-x: auto; position: relative; }
    .border-top-index { border-top: 3px solid #8b5cf6; }
    .border-top-stock { border-top: 3px solid #3b82f6; }
    .border-top-swing { border-top: 3px solid #10b981; }
    table { width: 100%; border-collapse: collapse; text-align: left; font-size: 0.95rem; color: #f8fafc; }
    th { padding: 14px 10px; color: #cbd5e1; border-bottom: 1px solid #475569; text-transform: uppercase; font-size: 0.8rem; }
    td { padding: 14px 10px; border-bottom: 1px solid rgba(51, 65, 85, 0.5); }
    tr:hover { background-color: rgba(51, 65, 85, 0.3); }
    .badge { padding: 5px 12px; border-radius: 6px; font-size: 0.8rem; font-weight: 700; display: inline-block; text-align: center; }
    .b-green { background: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3); }
    .b-red { background: rgba(239, 68, 68, 0.15); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3); }
    .b-yellow { background: rgba(245, 158, 11, 0.15); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.3); }
    .b-dark { background: #334155; color: #94a3b8; }
    .metric-pill { background: #0f172a; border: 1px solid #334155; border-radius: 8px; padding: 10px 15px; display: inline-block; margin-right: 15px; margin-bottom: 15px;}
    .metric-pill span.title { color: #94a3b8; font-size: 0.75rem; text-transform: uppercase; display: block; margin-bottom: 2px;}
    .metric-pill span.value { color: #f8fafc; font-size: 1.1rem; font-weight: bold; }
    .explainer-box { background: rgba(59, 130, 246, 0.05); border-left: 4px solid #3b82f6; padding: 15px; margin-bottom: 20px; font-size: 0.9rem; color: #cbd5e1; }
    </style>""",
    unsafe_allow_html=True
)

def get_atm_strike(price, ticker, is_index=False):
    if is_index:
        if 'BANK' in ticker: step = 100
        elif 'SENSEX' in ticker or 'BSESN' in ticker: step = 100
        else: step = 50 
    else:
        if price < 500: step = 5
        elif price < 2000: step = 10
        elif price < 4000: step = 20
        else: step = 50
    return int(round(price / step) * step)

indices = {'^NSEI': 'NIFTY 50', '^NSEBANK': 'BANK NIFTY', '^BSESN': 'SENSEX'}
stocks = {'HDFCBANK.NS': 'Banking', 'ICICIBANK.NS': 'Banking', 'SBIN.NS': 'Banking', 'M&M.NS': 'Auto', 'HAL.NS': 'CapGoods', 'TCS.NS': 'IT', 'RELIANCE.NS': 'Energy', 'LT.NS': 'CapGoods', 'SUNPHARMA.NS': 'Pharma', 'TATASTEEL.NS': 'Metals', 'ITC.NS': 'FMCG'}
astro_weights = {'Banking': 90, 'Auto': 85, 'CapGoods': 85, 'Energy': 65, 'Metals': 80, 'Pharma': 45, 'IT': 30, 'FMCG': 25}

st.markdown('<div class="gradient-text">ASTRO-QUANT PRO SCANNER</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-text">Live Options & Swing Recommendations directly from the Algo Dashboard</div>', unsafe_allow_html=True)

st.markdown('<div style="background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 20px; margin-bottom: 30px; text-align:center;"><h4 style="color:#f8fafc; margin-top:0; margin-bottom:15px;">🔍 Market Scanner Controls</h4><p style="color:#94a3b8; font-size:0.9rem; margin-bottom:0;">Leave date as today for live scanning, or select a past date to backtest.</p></div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    selected_date = st.date_input("📅 Select Scan Date", datetime.today().date())
    is_live = (selected_date == datetime.today().date())
    if st.button("🚀 FORCE SCAN NOW", use_container_width=True, type="primary"):
        st.cache_data.clear() 
        st.success(f"Scanner Initiated! Downloading market data for {selected_date}...")

@st.cache_data(ttl=60 if is_live else 86400)
def fetch_market_data(target_date):
    if isinstance(target_date, datetime): target_date = target_date.date()
    end_date = target_date + timedelta(days=1)
    
    start_intraday = end_date - timedelta(days=5)
    start_swing = end_date - timedelta(days=365)
    
    idx_daily = yf.download(list(indices.keys()), start=start_intraday.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'), progress=False)
    idx_intraday = yf.download(list(indices.keys()), start=start_intraday.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'), interval='15m', progress=False)
    stock_intraday = yf.download(list(stocks.keys()), start=start_intraday.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'), interval='15m', progress=False)
    stock_swing = yf.download(list(stocks.keys()), start=start_swing.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'), progress=False)
    
    return idx_daily, idx_intraday, stock_intraday, stock_swing

with st.spinner(f"Synchronizing with NSE Servers..."):
    idx_daily, idx_intraday, stock_intraday, stock_swing = fetch_market_data(selected_date)

if idx_intraday.empty and not is_live:
    st.error(f"⚠️ Yahoo Finance limits Intraday (15-Minute) data to the last 60 days. You selected a date too far in the past, so the Intraday scanners cannot run. However, the Daily Swing Trading table at the bottom will still work!")

idx_html = '<div class="index-ribbon">'
for ticker, name in indices.items():
    try:
        close = float(idx_daily['Close'][ticker].iloc[-1]) if isinstance(idx_daily.columns, pd.MultiIndex) else float(idx_daily['Close'].iloc[-1])
        prev = float(idx_daily['Close'][ticker].iloc[-2]) if isinstance(idx_daily.columns, pd.MultiIndex) else float(idx_daily['Close'].iloc[-2])
        pct = ((close - prev)/prev)*100
        color, sign = ("green", "+") if pct >= 0 else ("red", "")
        idx_html += f'<div class="index-card"><div class="index-name">{name}</div><div class="index-price">₹{close:,.2f} <span class="{color}" style="font-size:1.1rem;">{sign}{pct:.2f}%</span></div></div>'
    except: pass
idx_html += '</div>'
st.markdown(idx_html, unsafe_allow_html=True)

# ---------------------------------------------------------
# 1. INDEX INTRADAY OPTIONS
# ---------------------------------------------------------
st.markdown('<div class="section-title">⚡ INDEX OPTIONS (INTRADAY SCALPING)</div>', unsafe_allow_html=True)
st.markdown("""
<div class="explainer-box">
    <b>📖 High Frequency Intraday Strategy:</b> Since index setups are rare, we have opened the filter to catch Momentum Pullbacks. <br>
    <b>🟢 BUY CE (Call):</b> Market is in an Uptrend (Price > 200 SMA) but briefly pulled back (15M RSI < 40). <br>
    <b>🔴 BUY PE (Put):</b> Market is in a Downtrend (Price < 200 SMA) but briefly pumped (15M RSI > 60).
</div>
""", unsafe_allow_html=True)

if not idx_intraday.empty:
    idx_table = "<div class='custom-table-container border-top-index'><table><thead><tr><th>INDEX</th><th>15M CMP</th><th>15M RSI</th><th>INDEX TARGET</th><th>INDEX SL</th><th>EXACT OPTION TO BUY</th></tr></thead><tbody>"
    for ticker, name in indices.items():
        try:
            df = idx_intraday.xs(ticker, axis=1, level=1).copy() if isinstance(idx_intraday.columns, pd.MultiIndex) else idx_intraday.copy()
            df = df.dropna()
            if len(df) < 20: continue
            close = float(df['Close'].iloc[-1])
            df['delta'] = df['Close'].diff()
            df['rsi'] = 100 - (100 / (1 + (df['delta'].clip(lower=0).rolling(14).mean() / -df['delta'].clip(upper=0).rolling(14).mean())))
            df['sma_200'] = df['Close'].rolling(200).mean()
            
            c_rsi = float(df['rsi'].iloc[-1])
            sma200 = float(df['sma_200'].iloc[-1])
            strike = get_atm_strike(close, ticker, is_index=True)
            action, act_class, tp, sl = "HOLD", "b-dark", "-", "-"
            
            # WIDENED LOGIC SO CALLS ACTUALLY TRIGGER
            if c_rsi < 40 and close > sma200:
                action, act_class = f"🔥 BUY {strike} CE", "b-green"
                tp, sl = f"₹{close*1.0025:,.0f}", f"₹{close*0.994:,.0f}"
            elif c_rsi > 60 and close < sma200:
                action, act_class = f"🩸 BUY {strike} PE", "b-red"
                tp, sl = f"₹{close*0.9975:,.0f}", f"₹{close*1.006:,.0f}"
                
            rsi_color = "color: #10b981;" if c_rsi < 40 else ("color: #ef4444;" if c_rsi > 60 else "color: #94a3b8;")
            tp_color = "color: #10b981; font-weight:bold;" if action != "HOLD" else "color:#475569;"
            sl_color = "color: #ef4444; font-weight:bold;" if action != "HOLD" else "color:#475569;"
            idx_table += f"<tr><td style='font-weight:bold;'>{name}</td><td>₹{close:,.0f}</td><td style='{rsi_color}; font-weight:bold;'>{c_rsi:.1f}</td><td style='{tp_color}'>{tp}</td><td style='{sl_color}'>{sl}</td><td><span class='badge {act_class}'>{action}</span></td></tr>"
        except: pass
    idx_table += "</tbody></table></div>"
    st.markdown(idx_table, unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. STOCK INTRADAY OPTIONS
# ---------------------------------------------------------
st.markdown('<div class="section-title">⚡ STOCK OPTIONS (INTRADAY SCALPING)</div>', unsafe_allow_html=True)

if not stock_intraday.empty:
    intra_html = "<div class='custom-table-container border-top-stock'><table><thead><tr><th>TICKER</th><th>SECTOR</th><th>15M CMP</th><th>15M RSI</th><th>ASTRO BIAS</th><th>STOCK TARGET</th><th>STOCK SL</th><th>EXACT OPTION TO BUY</th></tr></thead><tbody>"
    for ticker, sector in stocks.items():
        try:
            df = stock_intraday.xs(ticker, axis=1, level=1).copy() if isinstance(stock_intraday.columns, pd.MultiIndex) else stock_intraday.copy()
            df = df.dropna()
            if len(df) < 20: continue
            close = float(df['Close'].iloc[-1])
            df['delta'] = df['Close'].diff()
            df['rsi'] = 100 - (100 / (1 + (df['delta'].clip(lower=0).rolling(14).mean() / -df['delta'].clip(upper=0).rolling(14).mean())))
            df['sma_200'] = df['Close'].rolling(200).mean()
            
            c_rsi = float(df['rsi'].iloc[-1])
            sma200 = float(df['sma_200'].iloc[-1])
            a_score = astro_weights.get(sector, 50)
            strike = get_atm_strike(close, ticker, is_index=False)
            action, act_class, tp, sl = "HOLD", "b-dark", "-", "-"
            
            # WIDENED LOGIC FOR STOCKS
            if c_rsi < 40 and a_score >= 65 and close > sma200:
                action, act_class = f"🔥 BUY {strike} CE", "b-green"
                tp, sl = f"₹{close*1.005:,.1f}", f"₹{close*0.985:,.1f}"
            elif c_rsi > 60 and a_score <= 45 and close < sma200:
                action, act_class = f"🩸 BUY {strike} PE", "b-red"
                tp, sl = f"₹{close*0.995:,.1f}", f"₹{close*1.015:,.1f}"
                
            rsi_color = "color: #10b981;" if c_rsi < 40 else ("color: #ef4444;" if c_rsi > 60 else "color: #94a3b8;")
            tp_color = "color: #10b981; font-weight:bold;" if action != "HOLD" else "color:#475569;"
            sl_color = "color: #ef4444; font-weight:bold;" if action != "HOLD" else "color:#475569;"
            intra_html += f"<tr><td style='font-weight:bold;'>{ticker.replace('.NS','')}</td><td style='color:#94a3b8; font-size:0.8rem;'>{sector}</td><td>₹{close:,.1f}</td><td style='{rsi_color}; font-weight:bold;'>{c_rsi:.1f}</td><td>{a_score}/100</td><td style='{tp_color}'>{tp}</td><td style='{sl_color}'>{sl}</td><td><span class='badge {act_class}'>{action}</span></td></tr>"
        except: pass
    intra_html += "</tbody></table></div>"
    st.markdown(intra_html, unsafe_allow_html=True)


# ---------------------------------------------------------
# 3. MULTI-STRATEGY SWING TRADING
# ---------------------------------------------------------
st.markdown('<div class="section-title">🎯 MULTI-STRATEGY SWING TRADING (EQUITY)</div>', unsafe_allow_html=True)

if not stock_swing.empty:
    swing_html = "<div class='custom-table-container border-top-swing'><table><thead><tr><th>TICKER</th><th>SECTOR</th><th>CMP</th><th>STRATEGY TRIGGERED</th><th>TARGET (+6%)</th><th>STOP LOSS</th><th>ACTION</th></tr></thead><tbody>"
    for ticker, sector in stocks.items():
        try:
            df = stock_swing.xs(ticker, axis=1, level=1).copy() if isinstance(stock_swing.columns, pd.MultiIndex) else stock_swing.copy()
            df = df.dropna()
            if len(df) < 200: continue
            close = float(df['Close'].iloc[-1])
            df['delta'] = df['Close'].diff()
            df['rsi'] = 100 - (100 / (1 + (df['delta'].clip(lower=0).rolling(14).mean() / -df['delta'].clip(upper=0).rolling(14).mean())))
            df['sma_50'] = df['Close'].rolling(50).mean()
            df['sma_200'] = df['Close'].rolling(200).mean()
            df['lower_bb'] = df['Close'].rolling(20).mean() - (2 * df['Close'].rolling(20).std())
            
            c_rsi = float(df['rsi'].iloc[-1])
            c_sma50, c_sma200, c_lbb = float(df['sma_50'].iloc[-1]), float(df['sma_200'].iloc[-1]), float(df['lower_bb'].iloc[-1])
            a_score = astro_weights.get(sector, 50)
            
            sig, act_class, strat, tp, sl = "HOLD", "b-dark", "-", "-", "-"
            
            if a_score >= 80 and close > c_sma200 and c_rsi < 35 and close <= (c_lbb * 1.02): 
                sig, act_class = "STRONG BUY", "b-green"
                strat = "Sniper (Astro-Reversion)"
                tp, sl = f"₹{close*1.06:,.1f}", f"₹{close*0.88:,.1f}"
            
            elif a_score >= 65 and c_sma50 > c_sma200 and close > c_sma50 and float(df['Low'].iloc[-1]) <= c_sma50 and c_rsi > 40:
                sig, act_class = "BUY", "b-yellow"
                strat = "50-SMA Pullback"
                tp, sl = f"₹{close*1.06:,.1f}", f"₹{close*0.94:,.1f}"
                
            tp_c = "color: #10b981; font-weight:bold;" if "BUY" in sig else "color:#475569;"
            sl_c = "color: #ef4444; font-weight:bold;" if "BUY" in sig else "color:#475569;"
            swing_html += f"<tr><td style='font-weight:bold;'>{ticker.replace('.NS','')}</td><td style='color:#94a3b8; font-size:0.8rem;'>{sector}</td><td>₹{close:,.1f}</td><td style='color:#f8fafc;'>{strat}</td><td style='{tp_c}'>{tp}</td><td style='{sl_c}'>{sl}</td><td><span class='badge {act_class}'>{sig}</span></td></tr>"
        except: pass
    swing_html += "</tbody></table></div>"
    st.markdown(swing_html, unsafe_allow_html=True)
