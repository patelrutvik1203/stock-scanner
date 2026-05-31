import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore')

# --- PAGE CONFIG ---
st.set_page_config(page_title="Astro-Quant Pro", page_icon="🌌", layout="wide", initial_sidebar_state="collapsed")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0b1120; color: #f8fafc; }
    
    .gradient-text {
        background: linear-gradient(90deg, #3b82f6, #10b981);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem; font-weight: 900; text-align: center;
        padding-top: 10px; margin-bottom: 0px; letter-spacing: 1px;
    }
    .sub-text { text-align: center; color: #94a3b8; font-size: 1.1rem; margin-bottom: 30px; }
    
    .index-ribbon {
        display: flex; justify-content: center; flex-wrap: wrap; gap: 20px; 
        background: #1e293b; padding: 20px; border-radius: 12px;
        border: 1px solid #334155; margin-bottom: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.4);
    }
    .index-card { text-align: center; flex: 1; min-width: 150px; }
    .index-card:not(:last-child) { border-right: 1px solid #334155; }
    .index-name { font-size: 0.9rem; color: #94a3b8; text-transform: uppercase; font-weight: bold; margin-bottom: 5px; }
    .index-price { font-size: 1.6rem; font-weight: bold; color: #f8fafc; }
    .green { color: #10b981; } .red { color: #ef4444; }
    
    .section-title {
        font-size: 1.5rem; font-weight: 800; color: #e2e8f0; 
        margin-top: 40px; margin-bottom: 5px; display: flex; align-items: center; gap: 10px;
    }
    .section-desc { color: #94a3b8; font-size: 0.95rem; margin-bottom: 15px; }
    
    .custom-table-container {
        background-color: #1e293b; border-radius: 12px; border: 1px solid #334155;
        padding: 20px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3); margin-bottom: 20px;
        overflow-x: auto; position: relative;
    }
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
    .b-dark { background: #334155; color: #94a3b8; }
    
    .metric-pill { background: #0f172a; border: 1px solid #334155; border-radius: 8px; padding: 10px 15px; display: inline-block; margin-right: 15px; margin-bottom: 15px;}
    .metric-pill span.title { color: #94a3b8; font-size: 0.75rem; text-transform: uppercase; display: block; margin-bottom: 2px;}
    .metric-pill span.value { color: #f8fafc; font-size: 1.1rem; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- STRIKE PRICE CALCULATOR ---
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

# --- CONFIGURATIONS ---
indices = {'^NSEI': 'NIFTY 50', '^NSEBANK': 'BANK NIFTY', '^BSESN': 'SENSEX'}
stocks = {'HDFCBANK.NS': 'Banking', 'ICICIBANK.NS': 'Banking', 'SBIN.NS': 'Banking', 'M&M.NS': 'Auto', 'HAL.NS': 'CapGoods', 'TCS.NS': 'IT', 'RELIANCE.NS': 'Energy', 'LT.NS': 'CapGoods', 'SUNPHARMA.NS': 'Pharma', 'TATASTEEL.NS': 'Metals', 'ITC.NS': 'FMCG'}
astro_weights = {'Banking': 90, 'Auto': 85, 'CapGoods': 85, 'Energy': 65, 'Metals': 80, 'Pharma': 45, 'IT': 30, 'FMCG': 25}

st.markdown('<div class="gradient-text">ASTRO-QUANT PRO SCANNER</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-text">Live Options & Swing Recommendations directly from the Algo Dashboard</div>', unsafe_allow_html=True)


# --- SCANNER CONTROLS (DATE PICKER ADDED BACK!) ---
st.markdown("""
<div style="background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 20px; margin-bottom: 30px; text-align:center;">
    <h4 style="color:#f8fafc; margin-top:0; margin-bottom:15px;">🔍 Market Scanner Controls</h4>
    <p style="color:#94a3b8; font-size:0.9rem; margin-bottom:0;">Leave date as today for live scanning, or select a past date to backtest.</p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 
