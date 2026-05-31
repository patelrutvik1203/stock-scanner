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
    td { padding: 14px 
