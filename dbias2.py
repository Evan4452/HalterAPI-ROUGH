# --- Core Python Libraries ---
import os
import re
import json
import time
import threading
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from colorsys import rgb_to_hls
import textwrap
from time import sleep

import streamlit as st

import uuid

# --- Web Scraping ---
import requests
from bs4 import BeautifulSoup

# --- Data Manipulation ---
import pandas as pd
import numpy as np

# --- Streamlit ---
import streamlit as st

# --- Plotting ---
import plotly.graph_objects as go
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode, ColumnsAutoSizeMode

# --- Technical Analysis ---
import talib

# --- Alpaca SDK ---
import alpaca_trade_api as tradeapi
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, OrderType, TimeInForce
from alpaca.trading.requests import MarketOrderRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.data.historical.stock import StockHistoricalDataClient, StockBarsRequest
from alpaca.data.historical.option import OptionHistoricalDataClient

# --- Indicators ---
import pandas as pd
import numpy as np

from ta.trend import EMAIndicator, ADXIndicator, MACD, PSARIndicator, IchimokuIndicator
from ta.volatility import AverageTrueRange, BollingerBands, DonchianChannel, KeltnerChannel
from ta.momentum import RSIIndicator, StochasticOscillator, ROCIndicator, WilliamsRIndicator
from ta.volume import OnBalanceVolumeIndicator
from ta.volume import ChaikinMoneyFlowIndicator
from ta.volume import AccDistIndexIndicator



from alpaca.data.historical.option import OptionHistoricalDataClient
from alpaca.data.requests import OptionSnapshotRequest


from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestTradeRequest


now = datetime.now().astimezone()



SETTINGS_FILE = "user_settings.json"
CREDENTIALS_FILE = "alpaca_credentials.json"

default_settings = {
    "primary_color": "#F5BF03",
    "secondary_color": "#21D2C6",
    "label_color": " #ffe899",
    "text_color": "#c0c0c0",
    "font_size": 12,
    "layout_option": "Moderate",
    "density": "Compact",
    "dark_bg_color": "#23272f",
    "light_bg_color": "#ffffff",
    "mode": "default",
    "theme": "Dark",
    "alpaca_api_key": "",
    "alpaca_api_secret": "",
    "alpaca_base_url": "https://paper-api.alpaca.markets",
}






import streamlit as st

# ---------- SIMPLE PASSWORD GATE ----------
PASSWORD = "hustletime"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("HalterAPI: Developer Access")
    pwd = st.text_input("Enter access code:", type="password")
    login = st.button("Unlock")

    if login:
        if pwd == PASSWORD:
            st.session_state.authenticated = True
            st.success("Access granted")
            st.rerun()  # reload app in authenticated state
        else:
            st.error("Incorrect code")
    st.stop()  # ❗ prevent rest of app from rendering



















import os
import json



def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            data = json.load(f)
        if isinstance(data, dict):
            # Ensure all keys exist
            for key, value in default_settings.items():
                if key not in data:
                    data[key] = value
            return data
        else:
            print("Settings file is not a dict. Resetting to defaults.")
    return default_settings.copy()

# Load settings
settings = load_settings()





# ---------------------------------------------------------
# 1. Define connect_alpaca() FIRST
# ---------------------------------------------------------
def connect_alpaca(api_key, api_secret, base_url):

    # 1 — Missing or empty keys
    if not api_key or not api_secret:
        print("Alpaca keys missing — running in NO_API mode.")
        return None, None, "no_api"

    # 2 — Developer placeholder detection
    if str(api_key).startswith("MISSING") or str(api_secret).startswith("MISSING"):
        print("Alpaca keys marked as MISSING — running in NO_API mode.")
        return None, None, "no_api"

    if api is not None:  # Only if connection succeeded
        st.session_state.api_key = ALPACA_API_KEY
        st.session_state.api_secret = ALPACA_API_SECRET
        st.session_state.alpaca_base_url = ALPACA_BASE_URL
        st.session_state.alpaca_mode = mode  # "paper" or "live"


    # 3 — Try connecting safely
    try:
        import alpaca_trade_api as tradeapi
        api = tradeapi.REST(api_key, api_secret, base_url=base_url)
        account = api.get_account()
        mode = "live" if getattr(account, "trading_enabled", False) else "paper"
        return api, account, mode



    except Exception as e:
        print(f"Alpaca connection failed safely: {e}")
        return None, None, "no_api"



# ---------------------------------------------------------
# 2. ENV + settings-based key resolution
# ---------------------------------------------------------

ALPACA_API_KEY = settings.get("alpaca_api_key") or os.getenv("APCA_API_KEY") or "MISSING_KEY"
ALPACA_API_SECRET = settings.get("alpaca_api_secret") or os.getenv("APCA_API_SECRET_KEY") or "MISSING_SECRET"
ALPACA_BASE_URL = settings.get("alpaca_base_url") or os.getenv("APCA_API_BASE_URL") or "https://paper-api.alpaca.markets"



# ---------------------------------------------------------
# 3. Connect once and persist across reruns
# ---------------------------------------------------------
if "api" not in st.session_state:
    api, account, mode = connect_alpaca(
        api_key=ALPACA_API_KEY,
        api_secret=ALPACA_API_SECRET,
        base_url=ALPACA_BASE_URL
    )
    st.session_state.api = api
    st.session_state.account = account
    st.session_state.mode = mode

# Easy references
api = st.session_state.api
account = st.session_state.account
alpaca_mode = st.session_state.mode



stock_data_client = StockHistoricalDataClient(ALPACA_API_KEY, ALPACA_API_SECRET)


def save_settings(settings):
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=4)
    except IOError as e:
        print(f"Error saving settings: {e}")

# --- Initialize session state ---
if "settings" not in st.session_state or not isinstance(st.session_state.settings, dict):
    st.session_state.settings = load_settings()

# Now assign variables from settings
settings = st.session_state.settings
primary_color = settings["primary_color"]
text_color = settings["text_color"]
theme = settings["theme"]

# --- Example usage ---
pl_display = 0
pl_color = "#2ace49" if pl_display > 0 else "#FF4B4B" if pl_display < 0 else text_color

 
# --- Theme palettes (unchanged) ---
dark_theme_palettes = {
    "Dark": {"background": "#23272f", "text": "#FFFFFF"},
    "Light": {"background": "#D1D1D1", "text": "#FF4B4B"},
    "Black": {"background": "#121212", "text": "#D6D5D5"},
    "Brown": {"background": "#474237", "text": "#CFC6C6"},
    "Indigo": {"background": "#292942", "text": "#FFFFFF"},
    "Seaweed": {"background": "#354230", "text": "#CFC6C6"}
}




# --- Portfolio P&L calculation ---
pl_display = 0
pl_percent = 0

def on_timeframe_change():
    st.session_state.settings["timeframe"] = st.session_state["timeframe"]
    save_settings(st.session_state.settings)  # or whatever your save function is called


# --- Color logic ---
pl_color = "#2ace49" if pl_display > 0 else "#FF4B4B" if pl_display < 0 else text_color


# --- Initialize session state ---
if "settings" not in st.session_state:
    st.session_state.settings = load_settings()

theme = st.session_state.settings.get("theme")
label_color = dark_theme_palettes.get(theme, {"text": "#000000"})["text"]

# Initialize missing keys in session state
if "font_size_slider" not in st.session_state:
    st.session_state.font_size_slider = st.session_state.settings["font_size"]
if "secondary_color_picker" not in st.session_state:
    st.session_state.secondary_color_picker = st.session_state.settings["secondary_color"]
if "layout_radio" not in st.session_state:
    st.session_state.layout_radio = st.session_state.settings["layout_option"]
if "density_radio" not in st.session_state:
    st.session_state.density_radio = st.session_state.settings["density"]
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Overview"  # Default active tab
# Initialize 'mode' in session state if it doesn't exist
if "mode" not in st.session_state.settings:
    st.session_state.settings["mode"] = default_settings["mode"]


# --- Update Settings Function ---
def update_settings(key, value):
    st.session_state.settings[key] = value
    save_settings(st.session_state.settings)


# --- Lists ---

if "Purchased_ETFs" not in st.session_state:
    st.session_state["Purchased_ETFs"] = []


# --- Running Loop ---
if "run_trading_loop" not in st.session_state:
    st.session_state.run_trading_loop = False




# --- Theme Variables ---
mode = st.session_state.settings["mode"]
theme = st.session_state.settings["theme"]
primary_color = st.session_state.settings["primary_color"]
font_size = st.session_state.settings["font_size"]  # Get font_size from settings

# Get theme colors from the palette

current_palette = dark_theme_palettes[theme] if theme in dark_theme_palettes else dark_theme_palettes["Dark"]
radio_text_color = "#FFFFFF"  # Light text for dark mode
radio_checked_bg_color = primary_color  # Use primary color when checked
radio_checked_text_color = "#FFFFFF"  # White text when checked
button_bg = "#23272f"  # Dark background for dark mode
button_text = "#FFFFFF"  # Light text for dark mode

background_color = current_palette["background"]
text_color = current_palette["text"]


primary_color = "#F5BF03"



st.markdown("""
    <style>
        /* Keep Streamlit header visible */
        header[data-testid="stHeader"] {
            display: block;
        }

        /* Remove top padding/margin from main app container */
        div[data-testid="stAppViewContainer"] {
            padding-top: 0 !important;
            margin-top: 0 !important;
        }

        /* Remove padding and margin from main content block */
        .block-container {
            padding-top: 0 !important;
            margin-top: -6rem !important;
        }

        /* Remove margin/padding from main section */
        section.main {
            padding-top: 0 !important;
            margin-top: 0 !important;
        }
    </style>
""", unsafe_allow_html=True)




import streamlit as st

st.set_page_config(
    page_title="HalterAPI",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    /* === 1. KEEP HEADER VISIBLE === */
    header[data-testid="stHeader"] {
        display: block !important;
    }



    /* === 3. DEFAULT LAYOUT – 90% centered === */
    .block-container {

        margin-left: auto !important;
        margin-right: auto !important;
        width: 90% !important;
        max-width: 1050px !important;
        padding: 0 1rem !important;
    }

    /* === 4. BASE LAYOUT – expands normally === */
    .main > div {
        width: 100% !important;
        max-width: 100% !important;
        overflow-x: visible !important;
        overflow-y: visible !important;
        transition: all 0.35s ease-out !important;
    }
    
    /* === 5. FREEZE AT 800PX WITH MARGINS + HORIZONTAL SCROLL === */
    @media (max-width: 855px) {

        /* ❗ Freeze outer container width */
        .main > div {
            width: 855px !important;
            max-width: 855px !important;
            overflow-x: auto !important;      /* horizontal scroll ON */
            overflow-y: visible !important;
        }

        /* ❗ Keep left/right margins EXACTLY how they were (not shrinking) */
        .block-container {
            width: 770px !important;          /* 800px - 2×20px margin effect */
            max-width: 770px !important;
            margin-left: auto !important;
            margin-right: auto !important;
            padding: 0 1rem !important;        /* padding stays same */
        }

        /* Optional scrollbar fade */
        .main > div::-webkit-scrollbar {
            height: 10px;
            opacity: 0;
            transition: opacity 0.4s ease;
        }
        .main > div:hover::-webkit-scrollbar {
            opacity: 1;
        }
    }

    /* === 6. COLUMN WRAPPING === */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-wrap: wrap !important;
        gap: 1rem !important;
    }
    [data-testid="column"] {
        flex: 1 1 auto !important;
        min-width: 260px !important;
    }

    /* === 7. GLOBAL SCROLLBAR STYLE === */
    ::-webkit-scrollbar {
        height: 10px;
        width: 10px;
    }
    ::-webkit-scrollbar-thumb {
        background: #555;
        border-radius: 5px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #777;
    }

    /* === 8. FULL-SCREEN ERROR BELOW 650PX === */
    #screen-too-thin {
        display: none;
        position: fixed;
        top: 0; left: 0;
        width: 100vw;
        height: 100vh;
        background: #000;
        color: #F5BF03;
        font-size: 4.5rem;
        font-weight: bold;
        text-align: center;
        justify-content: center;
        align-items: center;
        z-index: 999999;
        font-family: monospace;
        letter-spacing: 0.2em;
        text-shadow: 0 0 60px #ffe899;
    }
    @media (max-width: 640px) {
        body, .main, [data-testid="stAppViewContainer"], .block-container {
            visibility: hidden !important;
        }
        #screen-too-thin {
            display: flex !important;
            visibility: visible !important;
        }
    }

</style>

<div id="screen-too-thin">ERROR: SCREEN TOO THIN</div>
""", unsafe_allow_html=True)












# --- CSS Styling ---
st.markdown(f"""
<style>

/* Hides all anchor link icons injected in Streamlit headings */
h1 a, h2 a, h3 a, h4 a, h5 a, h6 a {{
    pointer-events: none !important;
    visibility: hidden !important;
    display: none !important;
}}

/* Theme toggle button */
div[data-testid="stButton"] > button {{
    background-color: {button_bg};
    color: {button_text};
    border: 1.5px solid {primary_color};
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 0.95rem;
    cursor: pointer;
    transition: 0.3s;
    margin-top: 1rem;
}}

div[data-testid="stButton"] > button:hover {{
    filter: brightness(1.1);
    border: 1.5px solid #F5BF03;
}}

/* Enlarge gear tab */
div[data-testid="stTabs"] div[role="tab"]:last-child span {{
    font-size: 1.3rem !important;
    display: flex;
    align-items: center;
    justify-content: center;
}}

/* Active tab styling */
div[data-testid="stTabs"] div[role="tab"][aria-selected="true"] {{
    background: {primary_color} !important;
    color: #fff !important;
    border-bottom: 3px solid {primary_color} !important;
    border-radius: 6px 6px 0 0;
}}

div[data-testid="stTabs"] div[role="tab"][aria-selected="true"] span {{
    color: #fff !important;
    font-weight: bold;
}}

/* Tab settings last child */
div[data-testid="stTabs"] div[role="tab"]:last-child[aria-selected="true"] {{
    background-color: #222 !important;
    color: {primary_color} !important;
    border-bottom: 3px solid #222 !important;
}}

/* General theme colors */
body {{
    background-color: {background_color};
    color: {text_color};
    font-size: {font_size}px !important;
}}

div[data-testid="stAppViewContainer"] {{
    background-color: {background_color};
    color: {text_color};
    font-size: {font_size}px !important;
}}

html, body, [class*="st-"] {{
    color: {text_color} !important;
    font-size: {font_size}px !important;
}}

div[data-testid="stTabs"] div[role="tab"]:focus {{
    box-shadow: none !important;
}}

/* Main select input */
div[data-baseweb="select"] > div {{
    color: {text_color} !important;
    border: 1.5px solid {primary_color} !important;
    border-radius: 6px !important;
    padding: 6px 12px !important;
    min-height: 38px !important;
    font-size: 0.95rem;
    transition: 0.3s;
    height: 38px !important;
    line-height: 38px;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
    display: flex;
    align-items: center;
}}

div[data-baseweb="menu"] {{
    border: 1.5px solid {primary_color} !important;
    border-radius: 6px !important;
    box-shadow: 0 2px 12px rgba(0,0,0,0.12) !important;
    margin-top: 2px !important;
}}

/* Radio button styling */
div[role="radiogroup"] {{
    display: flex;
    gap: 1em;
    align-items: center;
}}

div[role="radiogroup"] label {{
    background-color: transparent;
    border: none;
    padding: 0;
    margin: 0;
    color: {radio_text_color} !important;
    font-size: 0.95rem;
    cursor: pointer;
    transition: 0.3s;
    display: inline-block;
    position: relative;
    padding-left: 20px;
}}

div[role="radiogroup"] input[type="radio"] {{
    appearance: none;
    -webkit-appearance: none;
    -moz-appearance: none;
    position: absolute;
    left: 0;
    top: 2px;
    width: 12px;
    height: 12px;
    border: 1px solid {primary_color};
    border-radius: 50%;
    background-color: {background_color};
    outline: none;
    cursor: pointer;
}}

div[role="radiogroup"] input[type="radio"]:checked {{
    background-color: {radio_checked_bg_color};
    border: 1px solid {radio_checked_bg_color};
}}

div[role="radiogroup"] input[type="radio"]:checked::after {{
    content: '';
    position: absolute;
    top: 2px;
    left: 2px;
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background-color: {radio_checked_text_color};
    display: block;
}}

div[role="radiogroup"] label:hover {{
    color: #F5BF03 !important;
}}

div[role="radiogroup"] label:hover input[type="radio"] {{
    border-color: #F5BF03;
}}

div[role="radiogroup"] label:hover input[type="radio"]:checked {{
    border-color: #F5BF03;
}}

</style>
""", unsafe_allow_html=True)


# MAKE SELECTBOXES GLOW

st.markdown("""
<style>
/* Selectbox container */
div[data-baseweb="select"] > div {
    transition: box-shadow 0.3s ease-in-out;
    border-radius: 0.6rem !important;
    border: 1.5px solid #ccc !important;
    padding: 0.3rem 0.6rem !important;
    background-color: rgba(255,255,255,0.05) !important;
}

/* Glow on hover */
div[data-baseweb="select"]:hover > div {
    border-color: #F5BF03 !important;
}


/* Bounce keyframes */
@keyframes bounce {
  0% {
    transform: scale(1);
  }
  30% {
    transform: scale(1.08);
  }
  50% {
    transform: scale(0.95);
  }
  70% {
    transform: scale(1.03);
  }
  100% {
    transform: scale(1);
  }
}

/* Bounce animation on click with much slower speed */
div[data-testid="stButton"] > button:active {
    animation: bounce 1s ease forwards;
}


/* Style regular Streamlit buttons (exclude tabs) */
div[data-testid="stButton"] > button {
    border: 1.5px solid #ccc !important;
    border-radius: 0.6rem !important;
    background-color: rgba(255,255,255,0.05) !important;
    color: inherit !important;
    padding: 0.3rem 0.6rem !important;
    transition: box-shadow 0.3s ease-in-out, border-color 0.3s ease-in-out;
    cursor: pointer;
    /* Prevent transform jumps on hover/focus */
    transform-origin: center;
}

/* Glow on hover */
div[data-testid="stButton"]:hover > button {

    border-color: #F5BF03 !important;
}

/* Glow on focus (keyboard or click focus) */
div[data-testid="stButton"]:focus-within > button,
div[data-testid="stButton"]:focus > button {

    border-color: #F5BF03 !important;
    outline: none !important;
}

/* Bounce animation on click */
div[data-testid="stButton"] > button:active {
    animation: bounce 0.3s ease forwards;
}

</style>
""", unsafe_allow_html=True)


# FIX LAGGING UNDERLINE GLITCH

st.markdown(f"""
<style>

/* Remove underline from all tabs */
div[data-testid="stTabs"] div[role="tab"] {{
    border-bottom: none !important;
    box-shadow: none !important;
    transition: none !important;
}}

/* Remove Streamlit's default underline pseudo-element */
div[data-testid="stTabs"] div[role="tab"]::after {{
    border-bottom: none !important;
    box-shadow: none !important;
    transition: none !important;
    display: none !important;
    content: none !important;
}}

/* Only show underline for the active tab */
div[data-testid="stTabs"] div[role="tab"][aria-selected="true"] {{
    border-bottom: 3px solid {primary_color} !important;
    background: {primary_color} !important;
    color: #fff !important;
    border-radius: 6px 6px 0 0;
}}
</style>
""", unsafe_allow_html=True)


st.markdown(f"""
<style>
/* 🧼 Remove ALL native input glows, outlines and red/white effects */
input:focus,
textarea:focus,
select:focus,
button:focus,
div:focus,
div:focus-within,
.stTextInput:focus-within,
.stNumberInput:focus-within,
.stTextArea:focus-within,
div[data-baseweb="input"]:focus-within,
div[data-baseweb="select"]:focus-within,
div[data-baseweb="input"] > div:focus-within {{
    outline: none !important;
    box-shadow: none !important;
    border-color: #444d5f !important;  /* fallback gray */
}}

/* 🧯 Remove selectbox glow */
div[data-baseweb="select"][data-focus='true'] > div {{
    box-shadow: none !important;
    border-color: #444d5f !important;
}}

/* 🧯 Remove button glow */
div[data-testid="stButton"]:focus-within > button {{
    box-shadow: none !important;
    border-color: #444d5f !important;
}}

/* 🧯 Reset number input glow */
.stNumberInput > div:focus-within {{
    box-shadow: none !important;
    border-color: #444d5f !important;
}}

/* ✅ Apply YOUR glow (cyan tone) only where needed */
.stTextInput input:focus,
.stTextArea textarea:focus,
.stNumberInput input:focus {{
    border-color: {primary_color} !important;
    box-shadow: 0 0 0 2px {primary_color}55 !important;
    border-width: 2px !important;
    background-color: #181E25 !important;
    font-size: 1.07em !important;
}}

.stNumberInput > div:focus-within {{
    border-color: {primary_color} !important;
    box-shadow: 0 0 0 2px {primary_color}55 !important;
}}
</style>
""", unsafe_allow_html=True)


# SLIDERS





# MAKE SLIDERS PRIMARY COLOR
# MAKE THE DROPDOWN ARROW PRIMARY COLOR




# GOLD TITLES

st.markdown("""
<style>
.gold-title {
    position: relative;
    display: inline-block;
    font-size: 3.2rem;
    font-weight: 900;
    transform: translateY(-10px);
    line-height: 1.1;
}
.gold-title .front {
    position: relative;
    z-index: 2;
    display: inline-block;
    background: linear-gradient(180deg, #f5bf03 40%, #ffe899 73%, #dbad00 100%);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    color: transparent;
}
.gold-title .shadow {
    position: absolute;
    top: 19px;
    left: -5.5px;
    z-index: 1;
    color: black;
    user-select: none;
    pointer-events: none;
}
.gold-title .front::after {
    content: attr(data-text);
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background: linear-gradient(
        270deg,
        transparent 40%,
        rgba(255,255,255,0.95) 50%,
        transparent 60%
    );
    background-size: 200% 100%;
    background-repeat: no-repeat;
    background-position: -200% 0;
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    color: transparent;
    pointer-events: none;
    z-index: 3;
}
.gold-title .front:hover::after {
    animation: shimmer-right 2.4s linear forwards;
}
@keyframes shimmer-right {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}
</style>


""", unsafe_allow_html=True)













# SCAN BUTTONS CSS
st.markdown("""
<style>
.stFormSubmitButton > button {
    font-weight: bold;
    font-size: 20px !important;
    padding: 12px 40px !important;
    border-radius: 13px !important;  /* Corner curve 13px */
    transition: all 0.3s ease;

    background: linear-gradient(120deg, #3a3a3a 15%, #575757 50%, #7a7a7a 85%, #3a3a3a 100%) !important;
    border: 3px solid rgb(26, 27, 28) !important;  /* Black outline 3px */
    box-sizing: border-box;
}

/* Shadow on hover */
.stFormSubmitButton > button:hover {
    background: linear-gradient(120deg, #575757 15%,rgb(36, 22, 22) 50%, #909090 85%, #575757 100%) !important;
    color: black !important;
    box-shadow:
        0 0 3px 2px rgba(26, 27, 28, 0.4),
        0 6px 8px rgba(0, 0, 0, 0.45); /* Shadow on hover */
    transform: scale(1.05);
}

/* Focus effect */
.stFormSubmitButton > button:focus {
    background: linear-gradient(120deg, #7a7a7a 15%, #909090 50%, #adadad 85%, #c0c0c0 100%) !important;
    color: black !important;
    outline: none !important;
    box-shadow: 0 0 10px 3px #909090 !important;
    transform: scale(1.15);
}
</style>
""", unsafe_allow_html=True)








# ------------- CREDENTIALS LOGIC --------------

CREDENTIALS_FILE = "alpaca_credentials.json"


def load_credentials():
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, "r") as f:
            return json.load(f)
    # Default structure with empty creds and not connected
    return {
        "Account 1": {"api_key": "", "api_secret": "", "connected": False},
        "Account 2": {"api_key": "", "api_secret": "", "connected": False},
        "Account 3": {"api_key": "", "api_secret": "", "connected": False}
    }

def save_credentials(data):
    with open(CREDENTIALS_FILE, "w") as f:
        json.dump(data, f, indent=4)

def connect_alpaca(api_key, api_secret):
    # --- 1. Clean and validate inputs ---
    if not api_key or not api_secret:
        print("Alpaca keys missing — skipping connection.")
        return None, None, "no_api"

    api_key_s = str(api_key).strip()
    api_secret_s = str(api_secret).strip()

    # Block obvious placeholder keys
    invalid_markers = ["YOUR", "ENTER", "REPLACE", "SECRET", "KEY", "API", "MISSING"]
    if any(marker in api_key_s.upper() for marker in invalid_markers) or \
       any(marker in api_secret_s.upper() for marker in invalid_markers):
        print("Alpaca keys look like placeholders — skipping connection.")
        return None, None, "no_api"

    # --- 2. Try PAPER first (most users use paper) ---
    try:
        import alpaca_trade_api as tradeapi
        api = tradeapi.REST(
            api_key_s,
            api_secret_s,
            base_url="https://paper-api.alpaca.markets",
            api_version="v2"  # Always use v2
        )
        account = api.get_account()
        print("Connected to Alpaca PAPER account")
        return api, account, "paper"

    except Exception as e_paper:
        print(f"Paper connection failed: {e_paper}")

        # --- 3. If paper fails, try LIVE ---
        try:
            api = tradeapi.REST(
                api_key_s,
                api_secret_s,
                base_url="https://api.alpaca.markets",
                api_version="v2"
            )
            account = api.get_account()
            print("Connected to Alpaca LIVE account")
            return api, account, "live"

        except Exception as e_live:
            print(f"Live connection also failed: {e_live}")
            return None, None, "no_api"

    # This line will never be reached, but keeps Python happy
    return None, None, "no_api"

# Load saved credentials
credentials = load_credentials()



# ----------- SESSION STATE INIT ---------------
if "accounts_expanded" not in st.session_state:
    st.session_state.accounts_expanded = False

if "connected_account" not in st.session_state:
    st.session_state.connected_account = None
if "alpaca_connected" not in st.session_state:
    st.session_state.alpaca_connected = False
if "account_info" not in st.session_state:
    st.session_state.account_info = {}
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "api_secret" not in st.session_state:
    st.session_state.api_secret = ""

# On app load: try to restore connection state from saved credentials
def restore_connection_state():
    for acc, creds in credentials.items():
        if creds.get("connected") and creds.get("api_key") and creds.get("api_secret"):
            st.session_state.connected_account = acc
            st.session_state.alpaca_connected = True
            st.session_state.api_key = creds["api_key"]
            st.session_state.api_secret = creds["api_secret"]
            try:
                api, account, mode = connect_alpaca(creds["api_key"], creds["api_secret"])
                st.session_state.account_info = {
                    "mode": mode,
                    "status": account.status,
                    "equity": account.equity,
                    "buying_power": account.buying_power,
                }
                return
            except Exception:
                # Connection failed, clear connection
                st.session_state.alpaca_connected = False
                st.session_state.account_info = {}
                st.session_state.connected_account = None

restore_connection_state()








































import threading
import time
import streamlit as st




import threading
import time


if "trade_thread" not in st.session_state:
    st.session_state.trade_thread = None
if "trade_running" not in st.session_state:
    st.session_state.trade_running = False
if "trade_last_run" not in st.session_state:
    st.session_state.trade_last_run = None


def trading_loop(tickers, indicators, delay):
    while st.session_state.trade_running:
        try:
            # Call your trading function here
            scan_and_trade_etf_stocks(tickers, indicators)
            st.session_state.trade_last_run = time.time()
        except Exception as e:
            # Log errors safely
            if "trade_logs" not in st.session_state:
                st.session_state.trade_logs = []
            st.session_state.trade_logs.append(f"{time.strftime('%H:%M:%S')} Error: {str(e)}")
        # Sleep loop for delay seconds in 1-sec increments to allow early breaks
        for _ in range(delay):
            if not st.session_state.trade_running:
                break
            time.sleep(1)

def start_trading(tickers, indicators, delay):
    if not st.session_state.trade_running:
        st.session_state.trade_running = True
        th = threading.Thread(target=trading_loop, args=(tickers, indicators, delay), daemon=True)
        st.session_state.trade_thread = th
        th.start()

def stop_trading():
    st.session_state.trade_running = False
    st.session_state.trade_thread = None






































import streamlit as st

st.markdown("""
<style>
/* ----------------------------- */
/* 🚀 Top Tab Bar Wrapper        */
/* ----------------------------- */
#tabbar-wrapper {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    z-index: 999;
    background-color: white;
    transition: opacity 0.4s ease, margin-top 0.4s ease;
    opacity: 0;                 /* Hidden by default */
    pointer-events: none;
    margin-top: 0px;
    padding-top: 2px;
    padding-bottom: 2px;

}

/* ✅ Show tab bar when hovered or cursor near top */
#tabbar-wrapper.visible,
#tabbar-wrapper:hover {
    opacity: 1;
    pointer-events: auto;
    margin-top: 0px;
}

/* 🔧 Clear default tab visuals */
div[data-baseweb="tab-highlight"] {
    background-color: transparent !important;
}
div[data-baseweb="tab-border"] {
    display: none !important;
}

/* 🎨 Tab List Styling */
.stTabs [data-baseweb="tab-list"] {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    position: relative;
    padding: 0 1rem;
    margin-bottom: 0;
    z-index: 0;
}

/* 🔳 Grey base line */
.stTabs [data-baseweb="tab-list"]::after {
    content: "";
    position: absolute;
    bottom: 0;
    left: 13px;
    right: 13px;
    height: 4px;
    background-color: #444444;
    border-radius: 4px;
    z-index: 0;
}

/* ✨ Base Tab Styling (bold all tabs) */
.stTabs [data-baseweb="tab"],
.stTabs [data-baseweb="tab"] * {
    font-size: 14px;
    font-weight: 700 !important;     /* 🔥 Force bold for all tabs */
    color: #999999;
    background: transparent;
    border: none;
    padding: 8px 4px;
    margin: 0;
    position: relative;
    transition: all 0.3s ease;
    z-index: 1;
}


/* 🟨 Yellow underline – appears over grey line */
.stTabs [data-baseweb="tab"]::after {
    content: "";
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 4px;
    background-color: #ffe899;
    border-radius: 999px;
    transform: scaleX(0);
    transition: transform 0.3s ease;
    transform-origin: center;
    z-index: 2;
}
.stTabs [aria-selected="true"]::after {
    transform: scaleX(1);
}

/* 🌟 Selected tab: bigger + yellow + bolder */
.stTabs [aria-selected="true"],
.stTabs [aria-selected="true"] * {
    color: #ffe899 !important;
    font-weight: 800 !important;
    font-size: 16px !important;   /* ✅ slightly larger font */
}


</style>




<script>
/* 🎯 JS to make tab bar appear when mouse near top */
document.addEventListener("mousemove", function(e) {
    const tabbar = document.getElementById("tabbar-wrapper");
    if (e.clientY < 80) {
        tabbar.classList.add("visible");
    } else {
        tabbar.classList.remove("visible");
    }
});

</script>
""", unsafe_allow_html=True)






st.markdown("""
<style>
.stTabs [data-baseweb="tab-list"] > * > [data-baseweb="tab"]:nth-child(n+6):nth-child(-n+10),
.stTabs [data-baseweb="tab-list"] > [data-baseweb="tab"]:nth-child(n+6):nth-child(-n+10) {
    pointer-events: none;
    cursor: default;
    color: transparent !important;
    user-select: none;
}
</style>
""", unsafe_allow_html=True)


















# -----------------------------
# ✅ Tabs: Define & Render
# -----------------------------
left_tabs = ["Overview", "Options", "Equity", "ETFs", "Crypto"]
center_tabs = [" "," "," "," "," "]
right_tabs = ["🌐", "📁"]
tab_names = left_tabs + center_tabs + right_tabs

with st.container():
    st.markdown('<div id="tabbar-wrapper">', unsafe_allow_html=True)
    tabs = st.tabs(tab_names)
    st.markdown('</div>', unsafe_allow_html=True)


# When you switch tabs, update the query param:
for i, tab in enumerate(tab_names):
    if tabs[i].__dict__.get("_active", False):  # Not officially supported, but works
        st.query_params["tab"] = str(i)
        break




with tabs[0]:

    col1, col2 = st.columns([1, 2])


    with col1:
        st.markdown("""<div style="margin-top: 10px;"></div>""", unsafe_allow_html=True)
        st.markdown(
            '<h1 class="gold-title" style="font-size: 36px;">'
            '<span class="front" data-text="Overview">Overview</span>'
            '<span class="shadow">Overview</span>'
            '</h1>',
            unsafe_allow_html=True
        )








    with col2:
        st.markdown("""<div style="margin-top: 10px;"></div>""", unsafe_allow_html=True)
        with st.expander("Accounts") as expander:
            selected_account = st.selectbox(
                "Select Account",
                list(credentials.keys()),
                index=(list(credentials.keys()).index(st.session_state.connected_account)
                    if st.session_state.connected_account in credentials else 0),
                key="account_select"
            )

            saved_key = credentials[selected_account].get("api_key", "")
            saved_secret = credentials[selected_account].get("api_secret", "")

            # Use connected keys if account matches and connected
            if st.session_state.alpaca_connected and st.session_state.connected_account == selected_account:
                current_key = st.session_state.api_key
                current_secret = st.session_state.api_secret
            else:
                current_key = saved_key
                current_secret = saved_secret

            api_key = st.text_input("API Key", value=current_key, type="default", key="api_key_input")
            api_secret = st.text_input("API Secret", value=current_secret, type="password", key="api_secret_input")

            # Detect changes to keys or account selection
            inputs_changed = (
                api_key != st.session_state.api_key or
                api_secret != st.session_state.api_secret or
                selected_account != st.session_state.connected_account
            )

            # If keys changed and you're connected, disconnect and clear state
            if inputs_changed and st.session_state.alpaca_connected:
                st.session_state.alpaca_connected = False
                st.session_state.account_info = {}
                st.session_state.connected_account = None
                credentials[selected_account]["connected"] = False
                save_credentials(credentials)

            # Auto-connect when switching accounts with valid saved creds
            if not st.session_state.alpaca_connected and api_key and api_secret:
                try:
                    api, account, mode = connect_alpaca(api_key, api_secret)
                    st.session_state.alpaca_connected = True
                    st.session_state.connected_account = selected_account
                    st.session_state.api_key = api_key
                    st.session_state.api_secret = api_secret
                    st.session_state.account_info = {
                        "mode": mode,
                        "status": account.status,
                        "equity": account.equity,
                        "buying_power": account.buying_power,
                    }

                    # Mark this account as connected and others as not
                    for acc in credentials:
                        credentials[acc]["connected"] = acc == selected_account
                    credentials[selected_account]["api_key"] = api_key
                    credentials[selected_account]["api_secret"] = api_secret
                    save_credentials(credentials)

                    st.rerun()

                except Exception as e:
                    st.error(f"Auto-connection failed--Make sure keys are correct.")
                    st.session_state.alpaca_connected = False
                    st.session_state.account_info = {}
                    credentials[selected_account]["connected"] = False
                    save_credentials(credentials)

            # Display connection info
            if st.session_state.alpaca_connected:
                info = st.session_state.account_info
                if info:
                    st.markdown(f"**Mode:** {info.get('mode', '')}")
                    st.write("**Account Status:**", info.get("status", ""))
                    st.write("**Equity:**", info.get("equity", ""))
                    st.write("**Buying Power:**", info.get("buying_power", ""))
            else:
                if st.button("Connect"):
                    try:
                        credentials[selected_account]["api_key"] = api_key
                        credentials[selected_account]["api_secret"] = api_secret
                        credentials[selected_account]["connected"] = True
                        save_credentials(credentials)

                        api, account, mode = connect_alpaca(api_key, api_secret)

                        st.session_state.alpaca_connected = True
                        st.session_state.connected_account = selected_account
                        st.session_state.api_key = api_key
                        st.session_state.api_secret = api_secret
                        st.session_state.account_info = {
                            "mode": mode,
                            "status": account.status,
                            "equity": account.equity,
                            "buying_power": account.buying_power,
                        }
                        st.session_state.accounts_expanded = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"Connection failed: {e}")
                        st.session_state.alpaca_connected = False
                        st.session_state.account_info = {}
                        credentials[selected_account]["connected"] = False
                        save_credentials(credentials)


    if st.session_state.alpaca_connected:
        # --- Theme settings ---
        theme = st.session_state.settings["theme"]
        text_color = "#eee" if theme == "Dark" else "#111"
        primary_color = st.session_state.settings['primary_color']
        secondary_color = st.session_state.settings['secondary_color']
        label_color = "#eee" if theme == "Dark" else "#111"

        # --- Timeframe options ---


        # --- Layout ---
        col1, col1_2, col2 = st.columns([4, 0.2,1])

        try:
            # --- Connect to Alpaca REST client ---
            mode = st.session_state.account_info.get("mode", "").lower()

            if mode == "paper":
                base_url = "https://paper-api.alpaca.markets"
            elif mode == "live":
                base_url = "https://api.alpaca.markets"
            else:
                base_url = "https://paper-api.alpaca.markets"  # default to paper

            # Clean keys again (safety first)
            api_key = st.session_state.api_key.strip()
            api_secret = st.session_state.api_secret.strip()

            # Reconnect with correct endpoint
            api = tradeapi.REST(
                api_key,
                api_secret,
                base_url=base_url,
                api_version="v2"
            )

            with col2:
                timeframe_options = ["Day", "Week", "Month", "Quarter", "Year", "All"]
                timeframe_map = {
                    "Day": "1H", "Week": "1H", "Month": "1D",
                    "Quarter": "1D", "Year": "1D", "All": "1D"
                }
                period_map = {
                    "Day": "1D", 
                    "Week": "1W", 
                    "Month": "1M",
                    "Quarter": "3M", 
                    "Year": "12M", 
                    "All": "all"
                    
                }

                # Initialize session state for timeframe if needed
                if "timeframe" not in st.session_state:
                    st.session_state["timeframe"] = st.session_state.settings.get("timeframe", "Day")



                st.markdown(
                    "<div style='font-weight:800; font-size:1.1em; margin-bottom:0em;'>Timeframe</div>",
                    unsafe_allow_html=True,
                )
                selected_timeframe = st.selectbox(
                    "",
                    options=timeframe_options,
                    key="timeframe",
                    on_change=on_timeframe_change,
                    label_visibility="collapsed",
                )



                

                # Save the selected timeframe to settings if changed
                if selected_timeframe != st.session_state.settings.get("timeframe", "Day"):
                    st.session_state.settings["timeframe"] = selected_timeframe
                    save_settings(st.session_state.settings)

            # --- Portfolio history ---
            history = api.get_portfolio_history(
                timeframe=timeframe_map[selected_timeframe],
                period=period_map[selected_timeframe]
            )

            if history is None or not hasattr(history, "timestamp") or not hasattr(history, "equity"):
                timestamps = []
                equity = []
            else:
                timestamps = [datetime.fromtimestamp(ts) for ts in history.timestamp if ts is not None]
                equity = [e or 0.0 for e in history.equity]  # ensure no None values



            # --- Plot line chart ---
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=timestamps,
                y=equity,
                mode="lines",
                name="Equity",
                line=dict(color=secondary_color, width=3)
            ))

            fig.update_layout(
                margin=dict(l=0, r=0, t=0, b=0),
                height=300,
                xaxis_title=None,
                yaxis_title=None,
                showlegend=False,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color=text_color),
                xaxis=dict(showgrid=False, showline=False, zeroline=False),
                yaxis=dict(
                    showgrid=True,
                    gridcolor="#444" if theme == "Dark" else "#ddd",
                    zeroline=False
                )
            )











            with col1:






                import streamlit as st
                import time

                # Initialize delay flag in session state
                if 'positions_table_delayed' not in st.session_state:
                    st.session_state.positions_table_delayed = False

                if not st.session_state.positions_table_delayed:
                    time.sleep(0)  # Wait 0.5 seconds with blank page (nothing renders here)
                    st.session_state.positions_table_delayed = True
                    st.rerun()  # Correct rerun call to refresh layout and content
                else:
                    # --- Positions Table ---
                    
                    def format_number(n):
                        s = f"{n:.2f}"
                        if '.' in s:
                            s = s.rstrip('0').rstrip('.')
                        return s

                    # Assuming `api` is already defined and authenticated
                    positions = api.list_positions()
                    data = []
                    sold_today = []


                    def is_option(symbol):
                        return len(symbol) > 10

                    for pos in positions:
                        qty = int(pos.qty)
                        symbol = pos.symbol
                        avg_price_float = round(float(pos.avg_entry_price or 0), 2)
                        current_price_float = round(float(getattr(pos, "current_price", getattr(pos, "market_price", 0)) or 0), 2)
                        multiplier = 100 if is_option(symbol) else 1
                        unrealized_pl_value = round((current_price_float - avg_price_float) * qty * multiplier, 2)

                        if qty == 0:
                            sold_today.append(symbol)
                            continue

                        if len(symbol) > 10:
                            stripped = symbol[4:]
                            if 'C' in stripped:
                                direction = "Call"
                            elif 'P' in stripped:
                                direction = "Put"
                            else:
                                direction = "Option"
                        else:
                            direction = "Long" if qty > 0 else "Short"

                        data.append({
                            "Symbol": symbol,
                            "Direction": direction,
                            "Quantity": abs(qty),
                            "Avg Entry Price": avg_price_float,
                            "Current Price": current_price_float,
                            "Unrealized P&L": unrealized_pl_value,
                        })

                    positions_df = pd.DataFrame(data)
                    positions_df.index = positions_df.index + 1







                    

                    gb = GridOptionsBuilder.from_dataframe(positions_df)
                    gb.configure_default_column(filter=False)

                    gb.configure_column("Symbol", cellStyle={'textAlign': 'left'}, filter=False)
                    gb.configure_column("Direction", cellStyle={'textAlign': 'center'}, filter=False)
                    gb.configure_column("Quantity", cellStyle={'textAlign': 'right'}, filter=False)
                    gb.configure_column("Avg Entry Price", cellStyle={'textAlign': 'right'}, filter=False)
                    gb.configure_column("Current Price", cellStyle={'textAlign': 'left'}, filter=False)
                    gb.configure_column(
                        "Unrealized P&L",
                        type=["numericColumn"],
                        valueFormatter=JsCode("""
                            function(params) {
                                return params.value.toFixed(2);
                            }
                        """),
                        cellStyle=JsCode(f"""
                            function(params) {{
                                if (params.value > 0) {{
                                    return {{color: '#2ace49', fontWeight: 'bold', textAlign: 'right'}};
                                }} else if (params.value < 0) {{
                                    return {{color: '#FF4B4B', fontWeight: 'bold', textAlign: 'right'}};
                                }} else {{
                                    return {{color: '{text_color}', textAlign: 'right'}};
                                }}
                            }}
                        """),
                        filter=False
                    )





                import streamlit as st
                import time

                # === Your original code with delayed chart rendering ===

                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

                # === Rest of your original code (unchanged) ===
                grid_options = gb.build()
                custom_css = {
                    ".ag-root-wrapper": {
                        "background-color": "#23272f !important",
                        "border-radius": "1rem !important",
                        "border": f"2px solid transparent !important",
                        "box-shadow": f"0 0 48px 12px transparent !important",
                        "--ag-wrapper-border-radius": "1rem",
                        "overflow": "hidden !important",
                        "transition": "box-shadow 0.25s ease, border-color 0.25s ease",
                    },
                    ".ag-root-wrapper:hover": {
                        "border-color": "#ffe899 !important",
                    },
                    ".ag-header": {
                        "background-color": "#23272f !important",
                        "color": f"{label_color} !important",
                        "font-weight": "bold !important",
                        "border-bottom": "2px solid #ffe899 !important",
                    },
                    ".ag-header-cell-label": {
                        "justify-content": "center !important",
                        "text-align": "center !important",
                        "width": "100% !important",
                    },
                    ".ag-row": {
                        "background-color": "#292c36 !important",
                        "color": "#f4f4f4 !important",
                        "font-size": "1em !important",
                        "transition": "background-color 0.25s ease",
                    },
                    ".ag-row-hover, .ag-row-focus": {
                        "background-color": "#393e4b !important",
                    },
                    ".ag-cell": {
                        "border-color": "#353535 !important",
                        "font-size": "1em !important",
                    },
                    ".ag-center-cols-container": {
                        "background-color": "#292c36 !important",
                    },
                }
                st.markdown('<div style="height:40px"></div>', unsafe_allow_html=True)
                st.markdown('<h2 style="color:#white;">Positions</h1>', unsafe_allow_html=True)

                # === Dynamic height calculation ===
                row_height = 28  # adjust if needed
                header_height = 35
                padding = 10
                num_rows = len(positions_df)
                if num_rows == 0:
                    grid_height = 50  # minimal height when no data
                else:
                    grid_height = header_height + (row_height * num_rows) + padding

                if not positions_df.empty:
                    AgGrid(
                        positions_df,
                        gridOptions=grid_options,
                        custom_css=custom_css,
                        allow_unsafe_jscode=True,
                        fit_columns_on_grid_load=True,
                        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_ALL_COLUMNS_TO_VIEW,
                        height=grid_height,
                        theme=None,
                        suppressRowGroupPanel=True,
                        suppressAggFuncInHeader=True,
                        sideBar=False,
                    )
                else:
                    st.markdown(f"<p style='color:{label_color};'>No open positions.</p>", unsafe_allow_html=True)

                # === SOLD TODAY SECTION ===
                if sold_today:
                    st.markdown(f"""
                        <div style='margin-top: 1.5rem; font-size: 1.1em; color: {label_color}; text-decoration: underline;'>
                            <b>Sold Today</b>
                        </div>
                    """, unsafe_allow_html=True)
                    for sym in sold_today:
                        try:
                            # Fetch closed trade info
                            closed = api.get_activities(activity_types="FILL", until=datetime.now()).filter(
                                lambda x: x.symbol == sym and x.side in ["sell", "cover"]
                            )
                            # Compute P&L (gross, not including fees/slippage)
                            total_pl = 0
                            for fill in closed:
                                qty = float(fill.qty or 0)
                                price = float(fill.price or 0)
                                total_pl += float(fill.net_amount) if hasattr(fill, "net_amount") else 0
                            # Decide color
                            color = "#2ace49" if total_pl > 0 else "#FF4B4B" if total_pl < 0 else text_color
                            pl_str = f"${total_pl:,.2f}"
                            st.markdown(f"""
                                <div style='color:{label_color}; padding-left: 0.5rem; font-size: 1em; margin-top: 0.25em;'>
                                    <span style='font-weight: 500;'>{sym}</span> — <span style='color:{color}; font-weight: bold;'>{pl_str}</span>
                                </div>
                            """, unsafe_allow_html=True)
                        except Exception as e:
                            st.markdown









            # --- P&L and account info ---
            pl_total = equity[-1] - equity[0]
            account = api.get_account()
            
                        
            eq = float(account.equity) if account.equity is not None else 0.0
            last_eq = float(account.last_equity) if account.last_equity is not None else 0.0
            buying_power = float(account.buying_power) if account.buying_power is not None else 0.0
            cash = float(account.cash) if account.cash is not None else 0.0
            pl_day = eq - last_eq


            if selected_timeframe == "Day":
                pl_display = pl_day
            else:
                pl_display = pl_total

            pl_color = "#2ace49" if pl_display >= 0 else "#FF4B4B"
            percent_change = (pl_display / equity[0] * 100) if equity[0] != 0 else 0

            with col2:
                st.markdown(
                    f"<div style='font-size:1.1em; color:{label_color}; margin-bottom:0.1em; margin-top:0.25em;font-weight: bold;'>"
                    f"{selected_timeframe} P&amp;L</div>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"<div style='font-size:2.05em; font-weight:bold; color:{pl_color}; margin-top:0; margin-bottom:0.5rem;'>"
                    f"${pl_display:,.2f}</div>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"<div style='font-size:1.1em; color:{pl_color}; margin-top:-0.8em; margin-bottom:0.75rem;'><b>{percent_change:+.2f}%</b></div>",
                    unsafe_allow_html=True,
                )


                day_pl_color = "#2ace49" if pl_day >= 0 else "#FF4B4B"

                # space above Account Info. box
                st.markdown("<div style='height: 2.5rem;'></div>", unsafe_allow_html=True)

                st.markdown(f"""
                <style>
                .grouped-metric {{
                    border-radius: 2.5rem;
                    padding: 1.25rem;
                    margin-top: 1rem;
                    margin-bottom: 1.75rem;
                    box-shadow: none;
                    transition: 0.3s ease-in-out;
                    text-align: center;
                }}
                .grouped-metric:hover {{
                    box-shadow: 0 0 30px {secondary_color}cc;
                    transform: scale(1.03);
                }}
                .metric-row {{
                    display: flex;
                    justify-content: space-between;
                    padding: 0.25rem 0;
                    font-size: 0.93rem;
                    color: inherit !important;
                }}
                .metric-row span:first-child {{
                    text-align: left;
                    width: 50%;
                }}
                .metric-row span:last-child {{
                    text-align: right;
                    width: 50%;
                    font-weight: bold;
                }}
                .metric-header {{
                    font-size: 1rem;
                    font-weight: 600;
                    color: {label_color};
                    margin-bottom: 0.75rem;
                }}

                """, unsafe_allow_html=True)



                import streamlit as st

                st.markdown(
                    f"""
                    <div class="grouped-metric" style="color: {label_color}; display: flex; flex-direction: column; align-items: center; justify-content: center;">
                        <div class="metric-header" style="font-size: 16px; font-weight: bold; text-align: center; border-bottom: 1px solid grey; padding-bottom: 4px;padding-top: 4px;">Account Overview</div>
                        <div class="metric-row" style="margin-top: 8px; margin-bottom: -10px; text-align: center;"><span style="font-size: 12px; font-weight: normal; color: grey;">Buying Power</span></div>
                        <div class="metric-row" style="margin-bottom: 8px; text-align: center;"><span style="font-size: 18px;">${buying_power:,.2f}</span></div>
                        <div class="metric-row" style="margin-top: 2px; margin-bottom: -10px; text-align: center;"><span style="font-size: 12px; font-weight: normal; color: grey;">Cash</span></div>
                        <div class="metric-row" style="margin-bottom: 8px; text-align: center;"><span style="font-size: 18px;">${cash:,.2f}</span></div>
                        <div class="metric-row" style="margin-top: 2px; margin-bottom: -10px; text-align: center;"><span style="font-size: 12px; font-weight: normal; color: grey;">Day P&L</span></div>
                        <div class="metric-row" style="text-align: center;"><span style="font-size: 18px; color: {day_pl_color};">${pl_day:,.2f}</span></div>
                    </div>
                    <style>
                        .grouped-metric .metric-row span {{
                            white-space: nowrap;
                        }}
                    </style>
                    """,
                    unsafe_allow_html=True,
                )


                # space below Account Info. box
                st.markdown("<div style='height: 2.5rem;'></div>", unsafe_allow_html=True)

                # PDT warning and Day Trades block (conditionally displayed)
                if float(account.equity) < 25000:
                    try:
                        day_trade_count = int(account.daytrade_count)
                        st.markdown(
                            f"""
                            <style>
                            .tooltip-container {{
                                position: relative;
                                width: 100%;
                                display: block;
                            }}
                            .tooltip-box {{
                                background-color: rgba(255, 255, 255, 0.1);
                                border-radius: 0.5rem;
                                padding: 0.75rem 1rem;
                                margin-top: 0.5rem;
                                color: {label_color};
                                border: 1px solid rgba(255, 255, 255, 0.15);
                                width: 100%;
                                box-sizing: border-box;
                                text-align: center;
                            }}
                            .tooltip-container .tooltip-text {{
                                visibility: hidden;
                                background-color: rgba(0, 0, 0, 0.85);
                                color: {text_color};
                                text-align: left;
                                padding: 6px 10px;
                                border-radius: 6px;
                                position: absolute;
                                z-index: 1;
                                top: 125%;
                                left: 50%;
                                transform: translateX(-50%);
                                opacity: 0;
                                transition: none;
                                font-size: 0.75rem;
                                white-space: nowrap;
                            }}
                            .tooltip-container:hover .tooltip-text {{
                                visibility: visible;
                                opacity: 1;
                            }}
                            </style>
                            <div class="tooltip-container">
                                <div class="tooltip-box">
                                    Day Trades: {day_trade_count}/3
                                </div>
                                <div class="tooltip-text">PDT count over 5 business days</div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    except Exception as e:
                        st.warning(f"Could not fetch day trade count: {e}")

                # Always display account logo and name under the day trades block


                col1, col2, col3 = st.columns([1, 6, 1])    
                with col2:
                    
                    st.markdown('<div style="height:65px"></div>', unsafe_allow_html=True)


                    import base64

                    st.set_page_config(layout="wide")

                    def get_base64_of_bin_file(bin_file):
                        with open(bin_file, "rb") as f:
                            data = f.read()
                        return base64.b64encode(data).decode()

                    img_base64 = get_base64_of_bin_file("images/LOGO2.png")

                    st.markdown(
                        f"""
                        <style>
                        .full-width-image img {{
                            margin-top: -27px;
                            padding: 0;
                            width: 100%;
                            display: block;
                        }}
                        </style>
                        <div class="full-width-image">
                            <img src="data:image/png;base64,{img_base64}" />
                        </div>
                        """,
                        unsafe_allow_html=True
                    )


         

                    # Display Name as Status

                    st.markdown("<h4 style='text-align:center;margin-top: -16px;color:white;'>HalterAPI</h4>", unsafe_allow_html=True)




                st.markdown("<div style='height:30px;'></div>", unsafe_allow_html=True)




                # ---------------------------------------
                # READ INITIAL VALUE FROM URL (only once)
                # ---------------------------------------
                params = st.query_params
                initial_value = int(params.get("max_pct", 90))

                # ---------------------------------------
                # Initialize session_state only once
                # ---------------------------------------
                if "max_pct" not in st.session_state:
                    st.session_state.max_pct = initial_value

                # ---------------------------------------
                # Callback to update URL ONLY AFTER SLIDER STOP MOVING
                # ---------------------------------------
                def save_to_url():
                    st.query_params["max_pct"] = str(st.session_state.max_pct)

                # ---------------------------------------
                # SLIDER (smooth, no lag)
                # ---------------------------------------
                pct = st.slider(
                    "Maximum % of Portfolio to Invest",
                    min_value=1,
                    max_value=100,
                    step=1,
                    key="max_pct",
                    help="Sets the maximum portion of your portfolio that can be invested.",
                    on_change=save_to_url,  # <--- ONLY triggers after user stops sliding
                )

                # ---------------------------------------
                # Dollar calculations
                # ---------------------------------------
                cash = float(account.cash)
                max_dollars = cash * (pct / 100)
                min_reserve = cash - max_dollars

                st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

                st.write(f"Maximum invested amount: **${max_dollars:,.2f}**")
                st.write(f"Minimum cash reserve: **${min_reserve:,.2f}**")





        except Exception as e:
            st.error(f"Failed to fetch portfolio data: {e}")

    else:
        st.warning("Please connect your Alpaca account to view portfolio performance.")





















with tabs[1]:
    st.markdown(f"<h2 style='color: {primary_color};'>Options</h2>", unsafe_allow_html=True)
    st.write("Option trades for stocks.")
    if st.session_state.active_tab == "Options":
        st.session_state.active_tab = "Options"




    col1, col2 = st.columns([4, 1])  # adjust ratios for good spacing

    with col1:
        st.markdown(
            """
            <label style="font-weight:normal; white-space: nowrap;">
                Skip Earnings
                <span style="
                    display: inline-block;
                    background-color: #F5BF03;
                    color: white;
                    font-weight: bold;
                    padding: 2px 8px;
                    border-radius: 12px;
                    font-size: 0.75rem;
                    vertical-align: middle;
                    font-family: sans-serif;
                    user-select: none;
                    margin-left: 8px;
                ">
                    BETA
                </span>
            </label>
            <div style="font-size: small; color: gray; margin-top: 4px;">
                Skips tickers with earnings in the selected timeframe
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        skip_earnings = st.toggle(label="", value=False, key="skip_earnings", help=None)

    if skip_earnings:
        st.slider(
            "Earnings Avoidance",
            1,
            15,
            value=5,
            key="earnings_days",
            help="Tickers with earnings in this many days will be skipped",
        )




















# -------- ALPACA CLIENT HELPERS --------------

def get_trade_client():
    # Assumes st.session_state.api_key/secret already set (after user connects)
    if not st.session_state.get('api_key') or not st.session_state.get('api_secret'):
        st.error("No Alpaca credentials found in session.")
        st.stop()
    paper_mode = True if st.session_state.account_info.get("mode") == "paper" else False
    return TradingClient(
        st.session_state.api_key,
        st.session_state.api_secret,
        paper=paper_mode,
    )

def get_data_client():
    if not st.session_state.get('api_key') or not st.session_state.get('api_secret'):
        st.error("No Alpaca credentials found in session.")
        st.stop()
    return StockHistoricalDataClient(
        st.session_state.api_key,
        st.session_state.api_secret
    )

def get_option_data_client():
    if not st.session_state.get('api_key') or not st.session_state.get('api_secret'):
        st.error("No Alpaca credentials found in session.")
        st.stop()
    return OptionHistoricalDataClient(
        st.session_state.api_key,
        st.session_state.api_secret
    )

trade_client = get_trade_client()
data_client = get_data_client()
option_data_client = get_option_data_client()




# ------------------------
# DAILY BIAS -------------
# ------------------------

def fetch_data(symbol, start_date, end_date, timeframe=TimeFrame.Day):
    try:
        request = StockBarsRequest(
            symbol_or_symbols=[symbol],
            timeframe=timeframe,
            start=start_date,
            end=end_date
        )
        bars = data_client.get_stock_bars(request)

        # Some Alpaca versions return a tuple-like object, not a DataFrame
        if hasattr(bars, "df"):
            df = bars.df
        elif isinstance(bars, tuple):
            # Convert tuple to DataFrame explicitly
            df = pd.DataFrame(bars)
        else:
            df = pd.DataFrame(bars)

        if df.empty:
            print(f"[DEBUG] No data returned for {symbol}")
            return pd.DataFrame()

        # Handle MultiIndex (symbol + datetime) case
        if isinstance(df.index, pd.MultiIndex):
            df.index = df.index.get_level_values(1)
        df.index = pd.to_datetime(df.index)

        # Ensure required OHLCV columns exist
        required_cols = {"open", "high", "low", "close", "volume"}
        missing = required_cols - set(df.columns)
        if missing:
            print(f"[WARNING] Missing columns for {symbol}: {missing}")
            return pd.DataFrame()

        return df

    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return pd.DataFrame()


def calculate_rsi(df, period=14):
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_moving_averages(df):
    df['50_MA'] = df['close'].rolling(window=50).mean()
    df['100_MA'] = df['close'].rolling(window=100).mean()

def calculate_bias(df):
    if df is None or df.empty or len(df) < 100:
        return "Insufficient Data"
    calculate_moving_averages(df)
    df['RSI'] = calculate_rsi(df)
    df.dropna(subset=['50_MA', '100_MA', 'RSI'], inplace=True)
    if df.empty:
        return "Insufficient Data"
    latest = df.iloc[-1]
    trend = "Bullish" if latest['50_MA'] > latest['100_MA'] else "Bearish" if latest['50_MA'] < latest['100_MA'] else "Neutral"
    rsi_cond = "Overbought - Bearish" if latest['RSI'] > 70 else "Oversold - Bullish" if latest['RSI'] < 30 else "Neutral RSI"
    price_action = "Bullish" if latest['close'] > latest['open'] else "Bearish" if latest['close'] < latest['open'] else "Neutral Action"
    signals = [trend, rsi_cond, price_action]
    bull_score = signals.count("Bullish") + signals.count("Oversold - Bullish")
    bear_score = signals.count("Bearish") + signals.count("Overbought - Bearish")
    if bull_score >= 2:
        return "Bullish"
    elif bear_score >= 2:
        return "Bearish"
    else:
        return "Neutral"

def calculate_overall_bias(biases):
    bull_count = sum(1 for bias in biases.values() if bias == "Bullish")
    bear_count = sum(1 for bias in biases.values() if bias == "Bearish")
    if bull_count > bear_count:
        return "Bullish"
    elif bear_count > bull_count:
        return "Bearish"
    return "Neutral"

def daily_bias(return_details=False, show_instruments=True):
    symbols = ['SPY', 'QQQ', 'DIA', 'UUP']
    start = datetime.now() - timedelta(days=200)
    end = datetime.now()

    raw_biases = {}

    for symbol in symbols:
        data = fetch_data(symbol, start, end)
        bias = calculate_bias(data)
        raw_biases[symbol] = bias

    # Use a copy for market calculation
    biases_for_market = raw_biases.copy()
    if 'UUP' in biases_for_market:
        if biases_for_market['UUP'] == "Bullish":
            biases_for_market['UUP'] = "Bearish"
        elif biases_for_market['UUP'] == "Bearish":
            biases_for_market['UUP'] = "Bullish"

    overall = calculate_overall_bias(biases_for_market)

    if return_details:
        return overall, raw_biases  # show real UUP bias in UI!
    else:
        return overall
def daily_bias(return_details=False, show_instruments=True):
    symbols = ['SPY', 'QQQ', 'DIA', 'UUP']
    start = datetime.now() - timedelta(days=200)
    end = datetime.now()

    raw_biases = {}

    for symbol in symbols:
        data = fetch_data(symbol, start, end)
        bias = calculate_bias(data)
        raw_biases[symbol] = bias

    # Use a copy for market calculation
    biases_for_market = raw_biases.copy()
    if 'UUP' in biases_for_market:
        if biases_for_market['UUP'] == "Bullish":
            biases_for_market['UUP'] = "Bearish"
        elif biases_for_market['UUP'] == "Bearish":
            biases_for_market['UUP'] = "Bullish"

    overall = calculate_overall_bias(biases_for_market)

    if return_details:
        return overall, raw_biases  # show real UUP bias in UI!
    else:
        return overall
def daily_bias(return_details=False, show_instruments=True):
    symbols = ['SPY', 'QQQ', 'DIA', 'UUP']
    start = datetime.now() - timedelta(days=200)
    end = datetime.now()

    raw_biases = {}

    for symbol in symbols:
        data = fetch_data(symbol, start, end)
        bias = calculate_bias(data)
        raw_biases[symbol] = bias

    # Use a copy for market calculation
    biases_for_market = raw_biases.copy()
    if 'UUP' in biases_for_market:
        if biases_for_market['UUP'] == "Bullish":
            biases_for_market['UUP'] = "Bearish"
        elif biases_for_market['UUP'] == "Bearish":
            biases_for_market['UUP'] = "Bullish"

    overall = calculate_overall_bias(biases_for_market)

    if return_details:
        return overall, raw_biases  # show real UUP bias in UI!
    else:
        return overall







































# BULLISH SIGNALS




# Timeframe mapping
TIMEFRAME_MAP = {
    '15min': '15T',
    '30min': '30T',
    '1h': '1H',
    '1d': '1D',
    '1w': '1W'
}

# Resampling
def resample_data_bullish(df, timeframe):
    tf = TIMEFRAME_MAP.get(timeframe.lower())
    if not tf:
        raise ValueError(f"Unsupported timeframe: {timeframe}")
    df = df.copy()
    df.index = pd.to_datetime(df.index)
    return df.resample(tf).agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }).dropna()

# ----- Indicator Calculations -----

def calculate_ema_bullish(df):
    ema = EMAIndicator(df['close'], window=20).ema_indicator()
    df['EMA_20'] = ema
    df['EMA_Bullish'] = (df['close'] > ema) & (df['close'].shift(1) <= ema.shift(1))
    return df

def calculate_macd_bullish(df):
    macd = MACD(df['close'])
    df['MACD'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()
    df['MACD_Bullish'] = (df['MACD'] > df['MACD_signal']) & (df['MACD'].shift(1) <= df['MACD_signal'].shift(1))
    return df

def calculate_adx_bullish(df):
    adx = ADXIndicator(df['high'], df['low'], df['close'], window=14)
    df['ADX'] = adx.adx()
    df['+DI'] = adx.adx_pos()
    df['-DI'] = adx.adx_neg()
    df['ADX_Bullish'] = (df['+DI'] > df['-DI']) & (df['ADX'] > 20)
    return df

def calculate_parabolic_sar_bullish(df):
    psar = PSARIndicator(df['high'], df['low'], df['close'], step=0.02, max_step=0.2)
    df['SAR'] = psar.psar()
    df['SAR_Bullish'] = (df['close'] > df['SAR']) & (df['close'].shift(1) <= df['SAR'].shift(1))
    return df

def calculate_ichimoku_bullish(df):
    ichi = IchimokuIndicator(df['high'], df['low'], window1=9, window2=26, window3=52)
    df['tenkan_sen'] = ichi.ichimoku_conversion_line()
    df['kijun_sen'] = ichi.ichimoku_base_line()
    df['Ichimoku_Bullish'] = (df['tenkan_sen'] > df['kijun_sen']) & (df['tenkan_sen'].shift(1) <= df['kijun_sen'].shift(1))
    return df

def calculate_supertrend_bullish(df, period=10, multiplier=3):
    atr = AverageTrueRange(df['high'], df['low'], df['close'], window=period).average_true_range()
    hl2 = (df['high'] + df['low']) / 2
    upperband = hl2 + multiplier * atr
    lowerband = hl2 - multiplier * atr

    trend = [True]
    supertrend = [np.nan]

    for i in range(1, len(df)):
        if df['close'][i] > upperband[i - 1]:
            trend.append(True)
        elif df['close'][i] < lowerband[i - 1]:
            trend.append(False)
        else:
            trend.append(trend[-1])
            if trend[-1] and lowerband[i] < lowerband[i - 1]:
                lowerband[i] = lowerband[i - 1]
            elif not trend[-1] and upperband[i] > upperband[i - 1]:
                upperband[i] = upperband[i - 1]
        supertrend.append(lowerband[i] if trend[-1] else upperband[i])

    df['SuperTrend'] = supertrend
    df['SuperTrend_Bullish'] = trend
    return df

def calculate_rsi_bullish(df):
    rsi = RSIIndicator(df['close'], window=14).rsi()
    df['RSI'] = rsi
    df['RSI_Bullish'] = (rsi > 30) & (rsi.shift(1) <= 30)
    return df

def calculate_stochastic_bullish(df):
    sto = StochasticOscillator(df['high'], df['low'], df['close'], window=14, smooth_window=3)
    k = sto.stoch()
    d = sto.stoch_signal()
    df['Stoch_K'] = k
    df['Stoch_D'] = d
    df['Stochastic_Bullish'] = (k > d) & (k.shift(1) <= d.shift(1)) & (k < 20)
    return df

def calculate_roc_bullish(df):
    roc = ROCIndicator(df['close'], window=12).roc()
    df['ROC'] = roc
    df['ROC_Bullish'] = (roc > 0) & (roc.shift(1) <= 0)
    return df

def calculate_williams_r_bullish(df):
    willr = WilliamsRIndicator(df['high'], df['low'], df['close'], lbp=14).williams_r()
    df['Williams_%R'] = willr
    df['WilliamsR_Bullish'] = (willr > -80) & (willr.shift(1) <= -80)
    return df

def calculate_cci_bullish(df, window=20, constant=0.015):
    # Typical Price
    tp = (df['high'] + df['low'] + df['close']) / 3
    # Simple Moving Average of Typical Price
    sma_tp = tp.rolling(window=window, min_periods=window).mean()
    # Mean Deviation
    mean_dev = tp.rolling(window=window, min_periods=window).apply(lambda x: (abs(x - x.mean())).mean(), raw=True)
    # CCI Calculation
    cci = (tp - sma_tp) / (constant * mean_dev)
    df['CCI'] = cci
    # Bullish signal: CCI crosses above -100
    df['CCI_Bullish'] = (cci > -100) & (cci.shift(1) <= -100)
    return df

def calculate_bollinger_bands_bullish(df):
    bb = BollingerBands(close=df['close'], window=20, window_dev=2)
    df['BB_lower'] = bb.bollinger_lband()
    df['BB_upper'] = bb.bollinger_hband()
    df['BB_MA'] = bb.bollinger_mavg()
    df['BB_Bullish'] = (df['close'] > df['BB_lower']) & (df['close'].shift(1) <= df['BB_lower'].shift(1))
    return df

def calculate_atr_bullish(df):
    atr = AverageTrueRange(df['high'], df['low'], df['close'], window=14)
    df['ATR'] = atr.average_true_range()
    df['ATR_Bullish'] = df['ATR'] > df['ATR'].shift(1)
    return df

def calculate_donchian_bullish(df):
    dc = DonchianChannel(df['high'], df['low'], window=20)
    df['Donchian_Upper'] = dc.donchian_channel_hband()
    df['Donchian_Lower'] = dc.donchian_channel_lband()
    df['Donchian_Bullish'] = (df['close'] > df['Donchian_Upper']) & (df['close'].shift(1) <= df['Donchian_Upper'].shift(1))
    return df

def calculate_keltner_bullish(df):
    kc = KeltnerChannel(df['high'], df['low'], df['close'], window=20)
    df['Keltner_Upper'] = kc.keltner_channel_hband()
    df['Keltner_Lower'] = kc.keltner_channel_lband()
    df['Keltner_Mid'] = kc.keltner_channel_mband()
    df['Keltner_Bullish'] = (df['close'] > df['Keltner_Mid']) & (df['close'].shift(1) <= df['Keltner_Mid'].shift(1))
    return df

def calculate_obv_bullish(df):
    obv = OnBalanceVolumeIndicator(close=df['close'], volume=df['volume']).on_balance_volume()
    df['OBV'] = obv
    df['OBV_Bullish'] = df['OBV'] > df['OBV'].shift(1)
    return df

def calculate_vwap_bullish(df):
    # Intraday VWAP (resets daily)
    df['cum_vol'] = df['volume'].cumsum()
    df['cum_vol_price'] = (df['close'] * df['volume']).cumsum()
    df['VWAP'] = df['cum_vol_price'] / df['cum_vol']
    df['VWAP_Bullish'] = (df['close'] > df['VWAP']) & (df['close'].shift(1) <= df['VWAP'].shift(1))
    return df

def calculate_cmf_bullish(df):
    cmf = ChaikinMoneyFlowIndicator(high=df['high'], low=df['low'], close=df['close'], volume=df['volume'], window=20)
    df['CMF'] = cmf.chaikin_money_flow()
    df['CMF_Bullish'] = df['CMF'] > 0
    return df

def calculate_ad_line_bullish(df):
    ad = AccDistIndexIndicator(high=df['high'], low=df['low'], close=df['close'], volume=df['volume'])
    df['AD_Line'] = ad.acc_dist_index()
    df['AD_Bullish'] = df['AD_Line'] > df['AD_Line'].shift(1)
    return df

def calculate_high_volume_bullish(df, factor=1.5, window=20):
    avg_vol = df['volume'].rolling(window=window).mean()
    df['HighVolume_Bullish'] = (df['volume'] > factor * avg_vol) & (df['close'] > df['open'])
    return df

def calculate_pivot_points_bullish(df):
    df['Pivot'] = (df['high'].shift(1) + df['low'].shift(1) + df['close'].shift(1)) / 3
    df['R1'] = 2 * df['Pivot'] - df['low'].shift(1)
    df['S1'] = 2 * df['Pivot'] - df['high'].shift(1)

    # Bullish: close crosses above R1 or bounces from S1
    df['Pivot_Bullish'] = (
        (df['close'] > df['R1']) & (df['close'].shift(1) <= df['R1']) |
        (df['close'] > df['S1']) & (df['close'].shift(1) <= df['S1'])
    )
    return df

def calculate_fibonacci_bounce_bullish(df, lookback=20):
    high = df['high'].rolling(window=lookback).max()
    low = df['low'].rolling(window=lookback).min()

    df['Fib_50'] = low + 0.5 * (high - low)
    df['Fib_618'] = low + 0.618 * (high - low)

    # Bullish: close bounces up off 50% or 61.8% retracement
    df['Fibonacci_Bullish'] = (
        (df['close'] > df['Fib_50']) & (df['close'].shift(1) <= df['Fib_50']) |
        (df['close'] > df['Fib_618']) & (df['close'].shift(1) <= df['Fib_618'])
    )
    return df

def calculate_tema_bullish(df, window=20):
    # Calculate EMAs
    ema1 = df['close'].ewm(span=window, adjust=False).mean()
    ema2 = ema1.ewm(span=window, adjust=False).mean()
    ema3 = ema2.ewm(span=window, adjust=False).mean()
    # Calculate TEMA
    tema = 3 * (ema1 - ema2) + ema3
    df['TEMA'] = tema
    # Bullish signal: close crosses above TEMA
    df['TEMA_Bullish'] = (df['close'] > tema) & (df['close'].shift(1) <= tema.shift(1))
    return df

def calculate_hull_moving_average_bullish(df, period=21):
    wma_half = df['close'].rolling(window=period // 2).mean()
    wma_full = df['close'].rolling(window=period).mean()
    raw_hma = 2 * wma_half - wma_full
    hma = raw_hma.rolling(window=int(np.sqrt(period))).mean()
    df['HMA'] = hma
    df['HMA_Bullish'] = hma > hma.shift(1)
    return df

def calculate_elders_force_index_bullish(df):
    df['EFI'] = (df['close'] - df['close'].shift(1)) * df['volume']
    df['EFI_Bullish'] = (df['EFI'] > 0) & (df['EFI'].shift(1) <= 0)
    return df

def calculate_zscore_bullish(df, window=20):
    mean = df['close'].rolling(window).mean()
    std = df['close'].rolling(window).std()
    z = (df['close'] - mean) / std
    df['ZScore'] = z
    df['ZScore_Bullish'] = (z > -1.5) & (z.shift(1) <= -1.5)
    return df

def calculate_selected_indicators(df, selected_indicators, timeframe='1h'):
    df = resample_data(df, timeframe)

    indicator_map = {
        'EMA Bullish': calculate_ema_bullish,
        'MACD Bullish': calculate_macd_bullish,
        'ADX Bullish': calculate_adx_bullish,
        'Parabolic SAR Bullish': calculate_parabolic_sar_bullish,
        'Ichimoku Bullish': calculate_ichimoku_bullish,
        'SuperTrend Bullish': calculate_supertrend_bullish,
        'RSI Bullish': calculate_rsi_bullish,
        'Stochastic Bullish': calculate_stochastic_bullish,
        'ROC Bullish': calculate_roc_bullish,
        'Williams %R Bullish': calculate_williams_r_bullish,
        'CCI Bullish': calculate_cci_bullish,
        'Bollinger Bands Bullish': calculate_bollinger_bands_bullish,
        'ATR Bullish': calculate_atr_bullish,
        'Donchian Channels Bullish': calculate_donchian_bullish,
        'Keltner Channels Bullish': calculate_keltner_bullish,
        'OBV Bullish': calculate_obv_bullish,
        'VWAP Bullish': calculate_vwap_bullish,
        'CMF Bullish': calculate_cmf_bullish,
        'Accumulation/Distribution Bullish': calculate_ad_line_bullish,
        'High Volume Bullish': calculate_high_volume_bullish,
        'Pivot Points Bullish': calculate_pivot_points_bullish,
        'Fibonacci Retracement Bullish': calculate_fibonacci_bounce_bullish,
        'TEMA Bullish': calculate_tema_bullish,
        'Hull MA Bullish': calculate_hull_moving_average_bullish,
        'Elder Force Index Bullish': calculate_elders_force_index_bullish,
        'Z-Score Bullish': calculate_zscore_bullish
    }

    for ind in selected_indicators:
        if ind in indicator_map:
            df = indicator_map[ind](df)

    return df




#------------------- BULLISH SMART MONEY -------------------#







def _swing_high_indices(swings, df):
    """
    Return an Index of swing-high row labels, regardless of how `find_swings`
    structures its output (DataFrame, dict, tuple/list of indices, boolean mask, etc.).
    """
    import numpy as np
    import pandas as pd

    # DataFrame with a 'swing_high' column (bools or NaNs)
    if isinstance(swings, pd.DataFrame):
        if 'swing_high' in swings.columns:
            col = swings['swing_high']
            if col.dtype == bool:
                return swings.index[col]
            return col.dropna().index
        raise KeyError("swings DataFrame missing 'swing_high' column")

    # Dict-like
    if isinstance(swings, dict) and 'swing_high' in swings:
        sh = swings['swing_high']
    # Tuple/list: assume first element corresponds to swing highs
    elif isinstance(swings, (tuple, list)) and len(swings) > 0:
        sh = swings[0]
    else:
        # Already an index/series/mask/positions
        sh = swings

    # Normalize various types into an Index of df labels
    if isinstance(sh, pd.Series):
        if sh.dtype == bool:
            return sh.index[sh]
        return sh.dropna().index
    if isinstance(sh, pd.Index):
        return sh
    if isinstance(sh, (list, np.ndarray)):
        if len(sh) == 0:
            return pd.Index([])
        first = sh[0]
        # integer positions
        if isinstance(first, (int, np.integer)):
            return df.index.take(np.asarray(sh, dtype=int))
        # boolean mask
        if isinstance(first, (bool, np.bool_)):
            mask = np.asarray(sh, dtype=bool)
            return df.index[mask]
        # already labels
        return pd.Index(sh)

    raise TypeError(f"Unsupported swing_high structure: {type(sh)}")



def find_swings_bullish(df, left=2, right=2):
    highs = df['high']
    lows = df['low']
    swing_high = highs[(highs.shift(left) < highs) & (highs.shift(-right) < highs)]
    swing_low = lows[(lows.shift(left) > lows) & (lows.shift(-right) > lows)]
    swings = pd.DataFrame(index=df.index)
    swings['swing_high'] = swing_high
    swings['swing_low'] = swing_low
    return swings

def calculate_bos_bullish(df, lookback=20):

    df = df.copy()
    df['RollingMax'] = df['high'].rolling(window=lookback).max()
    df['BOS_Bullish'] = (df['close'] > df['RollingMax'].shift(1))
    df.drop(columns=['RollingMax'], inplace=True)  # Remove temporary column
    return df



def calculate_liquidity_sweep_bullish(df, lookback=5):
    df['Liquidity_Sweep_Bullish'] = False
    for i in range(lookback, len(df)):
        window = df.iloc[i - lookback:i]
        low = window['low'].min()
        if df['low'].iat[i] < low and df['close'].iat[i] > window['close'].iat[-2]:
            df['Liquidity_Sweep_Bullish'].iat[i] = True
    return df

def calculate_order_blocks_bullish(df):

    df = df.copy()
    df['OrderBlock_Bullish'] = False
    df['BreakerBlock_Bullish'] = False

    for i in range(1, len(df)):
        if df['BOS_Bullish'].iloc[i]:
            # Check if the previous candle was bearish
            if df['close'].iloc[i - 1] < df['open'].iloc[i - 1]:
                df.at[df.index[i], 'OrderBlock_Bullish'] = True
                # Check if the current candle breaks the high of the order block
                if df['close'].iloc[i] > df['high'].iloc[i - 1]:
                    df.at[df.index[i], 'BreakerBlock_Bullish'] = True

    return df


def calculate_fvg_bullish(df):
    df['FVG_Bullish'] = False
    df['IFVG_Bullish'] = False
    for i in range(2, len(df)):
        a = df.iloc[i - 2]   # previous row-2
        b = df.iloc[i - 1]   # previous row-1
        c = df.iloc[i]       # current row
        if b['low'] > a['high'] and b['low'] > c['high']:
            df.at[df.index[i], 'FVG_Bullish'] = True
        if b['high'] < a['low'] and c['close'] > b['high']:
            df.at[df.index[i], 'IFVG_Bullish'] = True
    return df


def calculate_discount_bullish(df, swing_window=20):
    df['Discount_Bullish'] = False
    rolling_high = df['high'].rolling(swing_window).max()
    rolling_low = df['low'].rolling(swing_window).min()
    equilibrium = (rolling_high + rolling_low) / 2
    df['Discount_Bullish'] = df['close'] < equilibrium
    return df


def calculate_smc_signals_bullish(df):
    df = calculate_bos_bullish(df)
    df = calculate_liquidity_sweep_bullish(df)
    df = calculate_order_blocks_bullish(df)
    df = calculate_fvg_bullish(df)
    df = calculate_discount_bullish(df)
    return df






# BEARISH SIGNALS





# Timeframe mapping
TIMEFRAME_MAP = { 
    '15min':'15T',
    '30min':'30T',
    '1h':'1H',
    '1d':'1D',
    '1w':'1W' }

def resample_data(df, timeframe):
    tf = TIMEFRAME_MAP.get(timeframe.lower())
    if not tf: raise ValueError(f"Unsupported timeframe: {timeframe}")
    df = df.copy()
    df.index = pd.to_datetime(df.index)
    return df.resample(tf).agg({
        'open':'first','high':'max','low':'min','close':'last','volume':'sum'
    }).dropna()

### Technical Indicators – Bearish Signals Only

def calculate_ema_bearish(df):
    ema = EMAIndicator(df['close'], window=20).ema_indicator()
    df['EMA_20'] = ema
    df['EMA_Bearish'] = (df['close'] < ema) & (df['close'].shift(1) >= ema.shift(1))
    return df

def calculate_macd_bearish(df):
    macd = MACD(df['close'])
    df['MACD'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()
    df['MACD_Bearish'] = (df['MACD'] < df['MACD_signal']) & (df['MACD'].shift(1) >= df['MACD_signal'].shift(1))
    return df

def calculate_adx_bearish(df):
    adx = ADXIndicator(df['high'], df['low'], df['close'], window=14)
    df['ADX'] = adx.adx()
    df['+DI'] = adx.adx_pos()
    df['-DI'] = adx.adx_neg()
    df['ADX_Bearish'] = (df['-DI'] > df['+DI']) & (df['ADX'] > 20)
    return df

def calculate_parabolic_sar_bearish(df):
    psar = PSARIndicator(df['high'], df['low'], df['close'], step=0.02, max_step=0.2)
    df['SAR'] = psar.psar()
    df['SAR_Bearish'] = (df['close'] < df['SAR']) & (df['close'].shift(1) >= df['SAR'].shift(1))
    return df

def calculate_ichimoku_bearish(df):
    ichi = IchimokuIndicator(df['high'], df['low'], window1=9, window2=26, window3=52)
    df['tenkan_sen'] = ichi.ichimoku_conversion_line()
    df['kijun_sen'] = ichi.ichimoku_base_line()
    df['Ichimoku_Bearish'] = (df['tenkan_sen'] < df['kijun_sen']) & (df['tenkan_sen'].shift(1) >= df['kijun_sen'].shift(1))
    return df

def calculate_supertrend_bearish(df, period=10, multiplier=3):
    atr = AverageTrueRange(df['high'], df['low'], df['close'], window=period).average_true_range()
    hl2 = (df['high'] + df['low'])/2
    ub = hl2 + multiplier*atr; lb = hl2 - multiplier*atr
    trend=[True]; st=[np.nan]
    for i in range(1,len(df)):
        if df['close'][i] > ub[i-1]:
            trend.append(True)
        elif df['close'][i] < lb[i-1]:
            trend.append(False)
        else:
            trend.append(trend[-1])
        st.append(lb[i] if trend[-1] else ub[i])
    df['SuperTrend']=st
    df['SuperTrend_Bearish']=[not t for t in trend]
    return df

def calculate_rsi_bearish(df):
    rsi = RSIIndicator(df['close'], window=14).rsi()
    df['RSI']=rsi
    df['RSI_Bearish'] = (rsi < 70) & (rsi.shift(1) >= 70)
    return df

def calculate_stochastic_bearish(df):
    sto = StochasticOscillator(df['high'], df['low'], df['close'], window=14, smooth_window=3)
    k=sto.stoch(); d=sto.stoch_signal()
    df['Stoch_K']=k; df['Stoch_D']=d
    df['Stochastic_Bearish'] = (k < d)&(k.shift(1)>=d.shift(1))&(k>80)
    return df

def calculate_roc_bearish(df):
    roc = ROCIndicator(df['close'], window=12).roc()
    df['ROC']=roc
    df['ROC_Bearish']=(roc<0)&(roc.shift(1)>=0)
    return df

def calculate_williams_r_bearish(df):
    willr = WilliamsRIndicator(df['high'], df['low'], df['close'], lbp=14).williams_r()
    df['Williams_%R']=willr
    df['WilliamsR_Bearish']=(willr<-20)&(willr.shift(1)>=-20)
    return df

def calculate_cci_bearish(df, window=20, constant=0.015):
    tp = (df['high'] + df['low'] + df['close']) / 3
    sma_tp = tp.rolling(window=window, min_periods=window).mean()
    mean_dev = tp.rolling(window=window, min_periods=window).apply(lambda x: (abs(x - x.mean())).mean(), raw=True)
    cci = (tp - sma_tp) / (constant * mean_dev)
    df['CCI'] = cci
    df['CCI_Bearish'] = (cci < 100) & (cci.shift(1) >= 100)
    return df

def calculate_bollinger_bands_bearish(df):
    bb = BollingerBands(df['close'],window=20,window_dev=2)
    df['BB_lower'] = bb.bollinger_lband()
    df['BB_upper'] = bb.bollinger_hband()
    df['BB_MA']= bb.bollinger_mavg()
    df['BB_Bearish'] = (df['close'] < df['BB_upper']) & (df['close'].shift(1) >= df['BB_upper'].shift(1))
    return df

def calculate_atr_bearish(df):
    atr = AverageTrueRange(df['high'],df['low'],df['close'],window=14).average_true_range()
    df['ATR']=atr
    df['ATR_Bearish']=atr<atr.shift(1)
    return df

def calculate_donchian_bearish(df):
    dc = DonchianChannel(df['high'],df['low'],window=20)
    df['Donchian_Upper']=dc.donchian_channel_hband()
    df['Donchian_Lower']=dc.donchian_channel_lband()
    df['Donchian_Bearish']=(df['close']<df['Donchian_Lower'])&(df['close'].shift(1)>=df['Donchian_Lower'].shift(1))
    return df

def calculate_keltner_bearish(df):
    kc = KeltnerChannel(df['high'],df['low'],df['close'],window=20)
    df['Keltner_Mid']=kc.keltner_channel_mband()
    df['Keltner_Bearish']=(df['close']<df['Keltner_Mid'])&(df['close'].shift(1)>=df['Keltner_Mid'].shift(1))
    return df

def calculate_obv_bearish(df):
    obv=OnBalanceVolumeIndicator(df['close'],df['volume']).on_balance_volume()
    df['OBV']=obv
    df['OBV_Bearish']=obv<obv.shift(1)
    return df

def calculate_vwap_bearish(df):
    df['cum_vol']=df['volume'].cumsum()
    df['cum_vol_price']=(df['close']*df['volume']).cumsum()
    df['VWAP']=df['cum_vol_price']/df['cum_vol']
    df['VWAP_Bearish']=(df['close']<df['VWAP'])&(df['close'].shift(1)>=df['VWAP'].shift(1))
    return df

def calculate_cmf_bearish(df):
    cmf = ChaikinMoneyFlowIndicator(df['high'],df['low'],df['close'],df['volume'], window=20).chaikin_money_flow()
    df['CMF']=cmf
    df['CMF_Bearish']=cmf<0
    return df

def calculate_ad_line_bearish(df):
    ad=AccDistIndexIndicator(df['high'],df['low'],df['close'],df['volume']).acc_dist_index()
    df['AD_Line']=ad
    df['AD_Bearish']=ad<ad.shift(1)
    return df

def calculate_high_volume_bearish(df,factor=1.5,window=20):
    avg=df['volume'].rolling(window).mean()
    df['HighVolume_Bearish']=(df['volume']>factor*avg)&(df['close']<df['open'])
    return df

def calculate_pivot_points_bearish(df):
    df['Pivot']=(df['high'].shift(1)+df['low'].shift(1)+df['close'].shift(1))/3
    df['R1']=2*df['Pivot']-df['low'].shift(1)
    df['S1']=2*df['Pivot']-df['high'].shift(1)
    df['Pivot_Bearish'] = (
        (df['close'] < df['S1']) & (df['close'].shift(1) >= df['S1']) |
        (df['close'] < df['R1']) & (df['close'].shift(1) >= df['R1'])
    )
    return df

def calculate_fibonacci_bounce_bearish(df,lookback=20):
    high=df['high'].rolling(lookback).max()
    low=df['low'].rolling(lookback).min()
    df['Fib_50']=low+0.5*(high-low)
    df['Fib_618']=low+0.618*(high-low)
    df['Fibonacci_Bearish']=(
        (df['close']<df['Fib_50'])&(df['close'].shift(1)>=df['Fib_50'])|
        (df['close']<df['Fib_618'])&(df['close'].shift(1)>=df['Fib_618'])
    )
    return df

def calculate_tema_bearish(df,window=20):
    ema1=df['close'].ewm(span=window,adjust=False).mean()
    ema2=ema1.ewm(span=window,adjust=False).mean()
    ema3=ema2.ewm(span=window,adjust=False).mean()
    tema=3*(ema1-ema2)+ema3
    df['TEMA']=tema
    df['TEMA_Bearish']=(df['close']<tema)&(df['close'].shift(1)>=tema.shift(1))
    return df

def calculate_hull_moving_average_bearish(df,period=21):
    wma_half=df['close'].rolling(period//2).mean()
    wma_full=df['close'].rolling(period).mean()
    raw=2*wma_half-wma_full
    hma=raw.rolling(int(np.sqrt(period))).mean()
    df['HMA']=hma
    df['HMA_Bearish']=hma<hma.shift(1)
    return df

def calculate_elders_force_index_bearish(df):
    df['EFI']=(df['close']-df['close'].shift(1))*df['volume']
    df['EFI_Bearish']=(df['EFI']<0)&(df['EFI'].shift(1)>=0)
    return df

def calculate_zscore_bearish(df,window=20):
    mean=df['close'].rolling(window).mean()
    std=df['close'].rolling(window).std()
    z=(df['close']-mean)/std
    df['ZScore']=z
    df['ZScore_Bearish']=(z<1.5)&(z.shift(1)>=1.5)
    return df

import pandas as pd
import numpy as np
import ta
from ta.volatility import AverageTrueRange, DonchianChannel, KeltnerChannel

# Make sure you have a resample_data(df, timeframe) function in your code
# And find_swings(df) defined properly

def calculate_selected_indicators_bullish(df: pd.DataFrame, selected_indicators: list, timeframe: str = "1h") -> pd.DataFrame:
    import ta
    import numpy as np

    df = resample_data(df, timeframe)
    df = df.copy()

    # Ensure numeric types
    df["close"] = df["close"].astype(float)
    df["open"] = df["open"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["volume"] = df["volume"].astype(float)




    # BOS
    if "BOS Bullish" in selected_indicators:
            df = calculate_bos_bullish(df)




    # RSI
    if "RSI Bullish" in selected_indicators:
        df["RSI"] = ta.momentum.RSIIndicator(close=df["close"], window=14).rsi()
        df["RSI_Bullish"] = (df["RSI"] < 30)

    # MACD Histogram
    if "MACD Bullish" in selected_indicators:
        macd = ta.trend.MACD(close=df["close"])
        df["MACD_Histogram"] = macd.macd_diff()
        df["MACD_Bullish"] = df["MACD_Histogram"] > 0

    # Bollinger Bands
    if "Bollinger Bands Bullish" in selected_indicators:
        bb = ta.volatility.BollingerBands(close=df["close"], window=20, window_dev=2)
        df["BB_Upper"] = bb.bollinger_hband()
        df["BB_Lower"] = bb.bollinger_lband()
        df["BB_Middle"] = bb.bollinger_mavg()
        df["BB_Bullish"] = df["close"] <= df["BB_Lower"]

    # SMA 50 and 200
    if "SMA Bullish" in selected_indicators:
        df["SMA_50"] = df["close"].rolling(window=50).mean()
        df["SMA_200"] = df["close"].rolling(window=200).mean()
        df["SMA_Bullish"] = df["SMA_50"] > df["SMA_200"]

    # EMA 8 and 21
    if "EMA Bullish" in selected_indicators:
        df["EMA_8"] = df["close"].ewm(span=8, adjust=False).mean()
        df["EMA_21"] = df["close"].ewm(span=21, adjust=False).mean()
        df["EMA_Bullish"] = df["EMA_8"] > df["EMA_21"]

    # OBV
    if "OBV Bullish" in selected_indicators:
        df["OBV"] = ta.volume.OnBalanceVolumeIndicator(close=df["close"], volume=df["volume"]).on_balance_volume()
        df["OBV_Bullish"] = df["OBV"] > df["OBV"].shift(1)

    # CCI
    if "CCI Bullish" in selected_indicators:
        df["CCI"] = ta.trend.CCIIndicator(high=df["high"], low=df["low"], close=df["close"]).cci()
        df["CCI_Bullish"] = df["CCI"] > 0

    # MFI
    if "MFI Bullish" in selected_indicators:
        df["MFI"] = ta.volume.MFIIndicator(high=df["high"], low=df["low"], close=df["close"], volume=df["volume"]).money_flow_index()
        df["MFI_Bullish"] = df["MFI"] < 20

    # Stochastic RSI
    if "Stochastic Bullish" in selected_indicators:
        stoch = ta.momentum.StochRSIIndicator(close=df["close"])
        df["StochRSI"] = stoch.stochrsi()
        df["StochRSI_Bullish"] = df["StochRSI"] < 0.2

    # TEMA
    if "TEMA Bullish" in selected_indicators:
        ema1 = df['close'].ewm(span=20, adjust=False).mean()
        ema2 = ema1.ewm(span=20, adjust=False).mean()
        ema3 = ema2.ewm(span=20, adjust=False).mean()
        df['TEMA'] = 3 * (ema1 - ema2) + ema3
        df['TEMA_Bullish'] = (df['close'] > df['TEMA'])

    # Hull MA
    if "Hull MA Bullish" in selected_indicators:
        wma_half = df['close'].rolling(window=21 // 2).mean()
        wma_full = df['close'].rolling(window=21).mean()
        raw_hma = 2 * wma_half - wma_full
        df['HMA'] = raw_hma.rolling(window=int(np.sqrt(21))).mean()
        df['HMA_Bullish'] = df['HMA'] > df['HMA'].shift(1)

    # ATR
    if "ATR Bullish" in selected_indicators:
        atr = AverageTrueRange(df['high'], df['low'], df['close'], window=14)
        df['ATR'] = atr.average_true_range()
        df['ATR_Bullish'] = df['ATR'] > df['ATR'].shift(1)

    # Donchian
    if "Donchian Channels Bullish" in selected_indicators:
        dc = DonchianChannel(high=df['high'], low=df['low'], close=df['close'], window=20)
        df['Donchian_Upper'] = dc.donchian_channel_hband()
        df['Donchian_Lower'] = dc.donchian_channel_lband()
        df['Donchian_Bullish'] = (df['close'] > df['Donchian_Upper']) & (df['close'].shift(1) <= df['Donchian_Upper'].shift(1))

    # Keltner
    if "Keltner Channels Bullish" in selected_indicators:
        kc = KeltnerChannel(high=df['high'], low=df['low'], close=df['close'], window=20)
        df['Keltner_Upper'] = kc.keltner_channel_hband()
        df['Keltner_Lower'] = kc.keltner_channel_lband()
        df['Keltner_Mid'] = kc.keltner_channel_mband()
        df['Keltner_Bullish'] = (df['close'] > df['Keltner_Mid']) & (df['close'].shift(1) <= df['Keltner_Mid'].shift(1))

    # High Volume
    if "High Volume Bullish" in selected_indicators:
        factor = 1.5
        window = 20
        avg_vol = df['volume'].rolling(window=window).mean()
        df['HighVolume_Bullish'] = (df['volume'] > factor * avg_vol) & (df['close'] > df['open'])

    # Pivot Points
    if "Pivot Points Bullish" in selected_indicators:
        df['Pivot'] = (df['high'].shift(1) + df['low'].shift(1) + df['close'].shift(1)) / 3
        df['R1'] = 2 * df['Pivot'] - df['low'].shift(1)
        df['S1'] = 2 * df['Pivot'] - df['high'].shift(1)
        df['Pivot_Bullish'] = (
            ((df['close'] > df['R1']) & (df['close'].shift(1) <= df['R1'])) |
            ((df['close'] > df['S1']) & (df['close'].shift(1) <= df['S1']))
        )



    if "Williams %R Bullish" in selected_indicators:
        df = calculate_williams_r_bullish(df)


    if "Z-Score Bullish" in selected_indicators:
        df = calculate_zscore_bullish(df)




    # ROC Bullish
    if "ROC Bullish" in selected_indicators:
        df = calculate_roc_bullish(df)



    # Fibonacci
    if "Fibonacci Retracement Bullish" in selected_indicators:
        lookback = 20
        high = df['high'].rolling(window=lookback).max()
        low = df['low'].rolling(window=lookback).min()
        df['Fib_50'] = low + 0.5 * (high - low)
        df['Fib_618'] = low + 0.618 * (high - low)
        df['Fibonacci_Bullish'] = (
            ((df['close'] > df['Fib_50']) & (df['close'].shift(1) <= df['Fib_50'])) |
            ((df['close'] > df['Fib_618']) & (df['close'].shift(1) <= df['Fib_618']))
        )



    # Liquidity Sweep
    if "Liquidity Sweep Bullish" in selected_indicators:
        lookback = 5
        df['Liquidity_Sweep_Bullish'] = False
        for i in range(lookback, len(df)):
            window = df.iloc[i - lookback:i]
            low = window['low'].min()
            if df['low'].iat[i] < low and df['close'].iat[i] > window['close'].iat[-2]:
                df.at[df.index[i], 'Liquidity_Sweep_Bullish'] = True

    # Order Block
    if "Order Block Bullish" in selected_indicators:
        if "BOS Bullish" not in selected_indicators:
            df = calculate_bos_bullish(df)  # Ensure BOS is calculated if Order Block is selected
        df = calculate_order_blocks_bullish(df)

    # FVG - Fixed!
    if "FVG Bullish" in selected_indicators:
        df['FVG_Bullish'] = False
        df['IFVG_Bullish'] = False
        for i in range(2, len(df)):
            a = df.iloc[i - 2]
            b = df.iloc[i - 1]
            c = df.iloc[i]
            if b['low'] > a['high'] and b['low'] > c['high']:
                df.at[df.index[i], 'FVG_Bullish'] = True
            if b['high'] < a['low'] and c['close'] > b['high']:
                df.at[df.index[i], 'IFVG_Bullish'] = True

    # Discount
    if "Discount Bullish" in selected_indicators:
        swing_window = 20
        rolling_high = df['high'].rolling(swing_window).max()
        rolling_low = df['low'].rolling(swing_window).min()
        equilibrium = (rolling_high + rolling_low) / 2
        df['Discount_Bullish'] = df['close'] < equilibrium





    if "BOS Bullish" in selected_indicators:
        df = calculate_bos_bullish(df)

    if "Order Block Bullish" in selected_indicators:
        if "BOS Bullish" not in selected_indicators:
            df = calculate_bos_bullish(df)  # Ensure BOS is calculated if Order Block is selected
        df = calculate_order_blocks_bullish(df)



    # Clean up
    df.dropna(subset=['open', 'high', 'low', 'close', 'volume'], inplace=True)
    print(f"[DEBUG] Data shape after dropping NaNs in price columns: {df.shape}")

    return df



def calculate_selected_indicators_bearish(df: pd.DataFrame, selected_indicators: list, timeframe: str = "1h") -> pd.DataFrame:
    df = resample_data(df, timeframe)
    df = df.copy()

    # Ensure numeric types
    df["close"] = df["close"].astype(float)
    df["open"] = df["open"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["volume"] = df["volume"].astype(float)

    # ------------------------
    # (All the other bearish indicators remain same as your code)
    # ------------------------

    # FIXED FVG Bearish
    if "FVG Bearish" in selected_indicators:
        df['FVG_Bearish'] = False
        df['IFVG_Bearish'] = False
        for i in range(2, len(df)):
            a = df.iloc[i - 2]
            b = df.iloc[i - 1]
            c = df.iloc[i]
            if b['high'] < a['low'] and b['high'] < c['low']:
                df.at[df.index[i], 'FVG_Bearish'] = True
            if b['low'] > a['high'] and c['close'] < b['low']:
                df.at[df.index[i], 'IFVG_Bearish'] = True

    # Finish with cleanup
    df.dropna(subset=['open', 'high', 'low', 'close', 'volume'], inplace=True)
    print(f"[DEBUG] Data shape after dropping NaNs in price columns: {df.shape}")

    return df









#------------------- BEARISH SMART MONEY -------------------#





def calculate_bos_bearish(df, lookback=20):
    df = df.copy()
    df['RollingMin'] = df['low'].rolling(window=lookback).min()
    df['BOS_Bearish'] = (df['close'] < df['RollingMin'].shift(1))
    df.drop(columns=['RollingMin'], inplace=True)  # Remove temporary column
    return df




def calculate_liquidity_sweep_bearish(df, lookback=5):
    df['Liquidity_Sweep_Bearish'] = False
    for i in range(lookback,len(df)):
        window=df.iloc[i-lookback:i]
        high = window['high'].max()
        if df['high'].iat[i] > high and df['close'].iat[i] < window['close'].iat[-2]:
            df['Liquidity_Sweep_Bearish'].iat[i] = True
    return df

def calculate_order_blocks_bearish(df):
    df['OrderBlock_Bearish'] = False
    df['BreakerBlock_Bearish'] = False
    for i in range(1,len(df)):
        if df['BOS_Bearish'].iat[i]:
            blk = df.iloc[i-1]
            if blk['close'] > blk['open']:
                df['OrderBlock_Bearish'].iat[i]=True
                if df['close'].iat[i] < blk['low']:
                    df['BreakerBlock_Bearish'].iat[i]=True
    return df

def calculate_fvg_bearish(df):
    df['FVG_Bearish'] = False
    df['IFVG_Bearish'] = False
    for i in range(2, len(df)):
        a = df.iloc[i - 2]
        b = df.iloc[i - 1]
        c = df.iloc[i]
        if b['high'] < a['low'] and b['high'] < c['low']:
            df.at[df.index[i], 'FVG_Bearish'] = True
        if b['low'] > a['high'] and c['close'] < b['low']:
            df.at[df.index[i], 'IFVG_Bearish'] = True
    return df


def calculate_discount_bearish(df,swing_window=20):
    df['Discount_Bearish']=False
    r_high=df['high'].rolling(swing_window).max()
    r_low=df['low'].rolling(swing_window).min()
    eq = (r_high+r_low)/2
    df['Discount_Bearish']=df['close']>eq
    return df



def calculate_smc_signals_bearish(df):
    df = calculate_bos_bearish(df)
    df = calculate_liquidity_sweep_bearish(df)
    df = calculate_order_blocks_bearish(df)
    df = calculate_fvg_bearish(df)
    df = calculate_discount_bearish(df)
    return df



    

















with tabs[2]:
    st.markdown(f"<h2 style='color: {primary_color};'>Equity</h2>", unsafe_allow_html=True)
    st.write("Not Available in Beta.")
    if st.session_state.active_tab == "Equity":
        st.session_state.active_tab = "Equity"













def recompute_indicator_limits():
    selected = st.session_state.get("selected_indicators", [])
    bullish = [i for i in selected if "Bullish" in i]
    bearish = [i for i in selected if "Bearish" in i]
    total_bullish = len(bullish)
    total_bearish = len(bearish)

    st.session_state.total_bullish = total_bullish
    st.session_state.total_bearish = total_bearish
    st.session_state.settings["total_bullish"] = total_bullish
    st.session_state.settings["total_bearish"] = total_bearish


    save_settings(st.session_state.settings)  # This is your main save



# ------------------------------------------------------------------
# 1. PERSISTENCE: Load & Save to JSON File
# ------------------------------------------------------------------
STATE_FILE = "user_state.json"

def load_persistent_state():
    """Load saved state from JSON file into session_state."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                data = json.load(f)
            for k, v in data.items():
                st.session_state[k] = v
        except Exception as e:
            st.warning(f"Failed to load state: {e}")

            

def save_persistent_state():
    """Save ALL desired keys from session_state to JSON file."""
    keys_to_save = [
        # Your original keys
        "ETF_max_size", "ETF_min_size",
        "ETF_stop_loss", "ETF_take_profit",
        "buy_min_indicators", "sell_min_indicators",
        "exp_from", "exp_to",
        # Toggle checkboxes
        "etf_options_mode", "fallback_bias", "day_trade",
        "bias_only", "bullish_only", "bearish_only",
    ]
    data = {k: st.session_state.get(k) for k in keys_to_save if k in st.session_state}
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        st.error(f"Failed to save state: {e}")

# Load state only once per session
if "persistent_state_loaded" not in st.session_state:
    load_persistent_state()
    st.session_state.persistent_state_loaded = True





with tabs[3]:

# 1. Load everything that lives in user_state.json
    load_persistent_state()

    # 2. Make sure we have *defaults* (only the first run)
    for k, default in {
        "buy_min_indicators": 1,
        "sell_min_indicators": 1,
        "total_bullish": 1,
        "total_bearish": 1,
    }.items():
        if k not in st.session_state:
            st.session_state[k] = default



    # 4. (Optional) push the clamped values back to the UI file
    save_settings(st.session_state.settings)

    # -------------------------------------------------
    # 1. Helper: auto‑save any key to SETTINGS_FILE
    # -------------------------------------------------
    def _save_key(key: str):
        """Write the current value of st.session_state[key] into settings."""
        if key in st.session_state:
            st.session_state.settings[key] = st.session_state[key]
            save_settings(st.session_state.settings)




    # -------------------------------------------------
    # 2. Initialise EVERY default (run once per rerun)
    # -------------------------------------------------
    if "settings" not in st.session_state:
        st.session_state.settings = load_settings()

    # Call only after settings + indicators loaded

    settings = st.session_state.settings

    # ----- ALL DEFAULTS (add any you missed) -----
    defaults = {

        # new ones – add *every* widget key you use
        "ETF_take_profit": 30,
        "buy_min_indicators": 1,
        "sell_min_indicators": 1,
        "exp_from": 7, "exp_to": 14,
        "etf_options_mode": True, "bias_only": False,
        "fallback_bias": True, "bullish_only": False,
        "bearish_only": False, "day_trade": False,
        # indicator dialog
        "selected_indicators": [], "checkbox_states": {}
    }
    for k, v in defaults.items():
        if k not in settings:
            settings[k] = v
        # push into session_state so widgets can read it
        if k not in st.session_state:
            st.session_state[k] = settings[k]
        # Optional: debounce rapid saves (e.g. sliders that fire on every pixel)
        import functools, time
        _last_save = {}
        def save_key(key: str, debounce_sec: float = 0.5):
            now = time.time()
            if _last_save.get(key, 0) + debounce_sec > now:
                return
            _last_save[key] = now
            _save_key(key)



    col1, col2, col3_1, col3_2, col3_25, col3_3 = st.columns([2.7, 0.3, 2.1753, 0.2813, 0.1, 1.8753])

    with col1:
        st.markdown("""<div style="margin-top: 10px;"></div>""", unsafe_allow_html=True)
        st.session_state.active_tab = "ETFs"
        st.markdown(
            '<h1 class="gold-title" style="font-size: 36px;z-index: 8000;">'
            '<span class="front" data-text="ETFs">ETFs</span>'
            '<span class="shadow">ETFs</span>'
            '</h1>',
            unsafe_allow_html=True
        )


        # --- Load / Save Settings ---
        def load_settings():
            if os.path.exists(SETTINGS_FILE):
                try:
                    with open(SETTINGS_FILE, "r") as f:
                        return json.load(f)
                except Exception:
                    pass
            return {}


        def save_settings(settings):
            with open(SETTINGS_FILE, "w") as f:
                json.dump(settings, f, indent=2)


        # --- Initialize settings in session ---
        if "settings" not in st.session_state:
            st.session_state.settings = load_settings()


 
        for k, v in defaults.items():
            if k not in settings:
                settings[k] = v








        st.markdown(
            """
            <style>
            /* Ensure forms and interactive elements are above the background boxes */
            form, .stForm, div[data-testid="stForm"] {
                position: relative !important;
                z-index: 1000 !important;
            }

            /* Ensure other interactive widgets (buttons, sliders) also stack on top */
            div[data-testid="stButton"],
            div[data-testid="stSlider"],
            div[data-testid="stToggle"],
            div[data-testid="stTextInput"] {
                position: relative !important;
                z-index: 1000 !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )







        import streamlit as st

        # ================================
        # 1️⃣ Technique Data
        # ================================
        techniques = {
            "Moving Averages": [
                "EMA Bullish", "EMA Bearish", "TEMA Bullish", "TEMA Bearish", 
                "Hull MA Bullish", "Hull MA Bearish"
            ],
            "Momentum Indicators": [
                "MACD Bullish", "MACD Bearish", "RSI Bullish", "RSI Bearish",
                "Stochastic Bullish", "Stochastic Bearish", "ROC Bullish", "ROC Bearish",
                "Williams %R Bullish", "Williams %R Bearish", "Z-Score Bullish", "Z-Score Bearish"
            ],
            "Volatility Indicators": [
                "ATR Bullish", "ATR Bearish", "Bollinger Bands Bullish", "Bollinger Bands Bearish",
                "Donchian Channels Bullish", "Donchian Channels Bearish", "Keltner Channels Bullish", 
                "Keltner Channels Bearish", "Pivot Points Bullish", "Pivot Points Bearish", 
                "Fibonacci Retracement Bullish", "Fibonacci Retracement Bearish"
            ],
            "Volume Indicators": [
                "OBV Bullish", "OBV Bearish", "CMF Bullish", "CMF Bearish", 
                "Accumulation/Distribution Bullish", "Accumulation/Distribution Bearish",
                "High Volume Bullish", "High Volume Bearish", "Elder Force Index Bullish", 
                "Elder Force Index Bearish"
            ],
            "Smart Money Concepts": [
                "BOS Bullish", "Liquidity Sweep Bullish", "Order Block Bullish", "FVG Bullish", 
                "Discount Bullish", "BOS Bearish", "Liquidity Sweep Bearish", "Order Block Bearish", 
                "FVG Bearish", "Discount Bearish"
            ]
        }

        def get_signals_by_type(side, category):
            return [c for c in techniques[category] if side in c]

        bullish_categories = {
            "Moving Averages": get_signals_by_type("Bullish", "Moving Averages"),
            "Momentum": get_signals_by_type("Bullish", "Momentum Indicators"),
            "Volatility": get_signals_by_type("Bullish", "Volatility Indicators"),
            "Volume": get_signals_by_type("Bullish", "Volume Indicators"),
            "Smart Money": get_signals_by_type("Bullish", "Smart Money Concepts")
        }

        bearish_categories = {
            "Moving Averages": get_signals_by_type("Bearish", "Moving Averages"),
            "Momentum": get_signals_by_type("Bearish", "Momentum Indicators"),
            "Volatility": get_signals_by_type("Bearish", "Volatility Indicators"),
            "Volume": get_signals_by_type("Bearish", "Volume Indicators"),
            "Smart Money": get_signals_by_type("Bearish", "Smart Money Concepts")
        }



        # ================================
        # 2️⃣ Streamlit App
        # ================================
        st.set_page_config(page_title="Signal Indicator Selector", layout="wide")

        st.markdown("""
            <style>
            .indicator-form-title {
                text-align: center;
                font-size: 28px;
                font-weight: 700;
                color: #ffe899;
                margin-bottom: 26px;
                margin-top: 8px;
            }
            /* Remove column gap for perfectly contiguous buttons */
            .fullwidth-button-row .block-container > div { 
                gap: 0 !important; 
            }
            .fullwidth-buttons .stButton > button {
                width: 100% !important;
                display: block;
                margin: 0;
                background: linear-gradient(135deg, #f5bf03 40%, #ffe899 73%, #dbad00 100%);
                color: #2b3e56;
                padding: 15px 30px;
                font-size: 20px;
                border-radius: 50px;
                border: none;
                box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
                cursor: pointer;
                transition: all 0.3s ease;
            }
            .fullwidth-buttons .stButton > button:hover {
                box-shadow: 0 8px 26px rgba(0, 0, 0, 0.5);
                transform: scale(1.03);
            }





            .stButton > button {
                background: linear-gradient(135deg, #f5bf03 40%, #ffe899 73%, #dbad00 100%);
                color: #2b3e56;
                padding: 15px 30px;
                font-size: 20px;
                border-radius: 50px;
                border: none;
                box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
                cursor: pointer;
                transition: all 0.3s ease;
            }
            .stButton > button:hover {
                box-shadow: 0 8px 26px rgba(0, 0, 0, 0.5);
                transform: scale(1.04);
            }
            .signal-modal-header {
                display: flex;
                justify-content: center;
                align-items: center;
                border-bottom: 2px solid #444444;
                margin-bottom: 25px;
                padding-bottom: 12px;
            }
            .signal-modal-header h2 {
                margin: 0;
                font-size: 26px;
                color: #ffe899;
            }
            .signal-columns {
                display: flex;
                gap: 30px;
                justify-content: space-between;
            }
            .signal-column {
                flex: 1;
                min-width: 0;
            }
            .signal-section-title {
                text-align: center;
                font-weight: bold;
                margin-bottom: 12px;
                font-size: 20px;
                color: #ffe899;
            }
            .signal-bullish { color: #62ad50; }
            .signal-bearish { color: #d8483e; }
            .signal-subtitle {
                margin-top: 18px;
                font-weight: bold;
                font-size: 16px;
                color: #ffe899;
            }
            .signal-checkbox-group {
                display: flex;
                flex-direction: column;
                gap: 6px;
                margin-top: 6px;
            }
            .signal-submit-container {
                display: flex;
                justify-content: center;
                margin-top: 30px;
            }
            .signal-submit {
                background: #ffe899;
                color: #2b3e56;
                padding: 14px 30px;
                font-size: 18px;
                border-radius: 40px;
                border: none;
                box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
                cursor: pointer;
                transition: all 0.3s ease;
            }
            .signal-submit:hover {
                box-shadow: 0 8px 26px rgba(0, 0, 0, 0.5);
                transform: scale(1.03);
            }
            .success-message {
                background: #1c1c1c;
                border-radius: 20px;
                padding: 40px;
                text-align: center;
                color: #d3d3d3;
                box-shadow: 0 12px 60px rgba(0, 0, 0, 0.6);
                max-width: 500px;
                margin: auto;
            }
            .success-message h2 {
                margin: 0 0 20px 0;
                font-size: 24px;
                color: #ffe899;
            }
            </style>
        """, unsafe_allow_html=True)


        col1, col2 = st.columns([5, 1])
        with col1:
            
            import streamlit as st

            # [Previous code for techniques, get_signals_by_type, bullish_categories, bearish_categories remains unchanged]

            # Initialize session state
            if 'selected_indicators' not in st.session_state:
                st.session_state.selected_indicators = []
            if 'checkbox_states' not in st.session_state:
                st.session_state.checkbox_states = {}
            if 'submitted' not in st.session_state:
                st.session_state.submitted = False
            if 'form_type' not in st.session_state:
                st.session_state.form_type = None

            @st.dialog(" ", width="large")
            def signal_dialog(side):
                st.markdown(f"<div class='signal-modal-header'><h2>Select {side} Indicators</h2></div>", unsafe_allow_html=True)
                
                # Get categories based on side
                categories = bullish_categories if side == "Bullish" else bearish_categories
                
                # Initialize checkbox states for this side if not already present
                if side not in st.session_state.checkbox_states:
                    st.session_state.checkbox_states[side] = {}
                            

                # Define which categories go in which columns
                col1_cats = ["Moving Averages", "Momentum", "Volatility"]
                col2_cats = ["Volume", "Smart Money"]

                col1, col2 = st.columns(2)



                with col1:
                    for category in col1_cats:
                        if category in categories:
                            st.markdown(f"<div class='signal-subtitle signal-{side.lower()}'>{category}</div>", unsafe_allow_html=True)
                            for item in categories[category]:
                                checkbox_key = f"{side.lower()}_{item.replace(' ', '_')}"
                                if checkbox_key not in st.session_state.checkbox_states[side]:
                                    normalized_item = item
                                    st.session_state.checkbox_states[side][checkbox_key] = normalized_item in st.session_state.selected_indicators
                                is_checked = st.checkbox(item, value=st.session_state.checkbox_states[side][checkbox_key], key=checkbox_key)
                                st.session_state.checkbox_states[side][checkbox_key] = is_checked

                with col2:
                    for category in col2_cats:
                        if category in categories:
                            st.markdown(f"<div class='signal-subtitle signal-{side.lower()}'>{category}</div>", unsafe_allow_html=True)
                            for item in categories[category]:
                                checkbox_key = f"{side.lower()}_{item.replace(' ', '_')}"
                                if checkbox_key not in st.session_state.checkbox_states[side]:
                                    normalized_item = item
                                    st.session_state.checkbox_states[side][checkbox_key] = normalized_item in st.session_state.selected_indicators
                                is_checked = st.checkbox(item, value=st.session_state.checkbox_states[side][checkbox_key], key=checkbox_key)
                                st.session_state.checkbox_states[side][checkbox_key] = is_checked

                
                # Update selected_indicators based on all checkbox states
                selected_indicators = []
                for side_key in st.session_state.checkbox_states:
                    for checkbox_key, is_checked in st.session_state.checkbox_states[side_key].items():
                        if is_checked:
                            # Extract indicator name from checkbox_key (remove side prefix)
                            indicator = '_'.join(checkbox_key.split('_')[1:]).replace('_', ' ')
                            if indicator not in selected_indicators:  # Avoid duplicates
                                selected_indicators.append(indicator)
                st.session_state.selected_indicators = selected_indicators



                # Close button to exit dialog
                if st.button("Close", key=f"dialog_close_{side}", use_container_width=True):
                    # 1. Persist the whole list
                    st.session_state.settings["selected_indicators"] = st.session_state.selected_indicators
                    st.session_state.settings["checkbox_states"] = st.session_state.checkbox_states
                    save_settings(st.session_state.settings)

                    # 2. Re-compute limits and clamp the min-indicators
                    recompute_indicator_limits()
                    st.session_state.buy_min_indicators = max(
                        1, min(st.session_state.get("buy_min_indicators", 1), st.session_state.total_bullish)
                    )
                    st.session_state.sell_min_indicators = max(
                        1, min(st.session_state.get("sell_min_indicators", 1), st.session_state.total_bearish)
                    )
                    st.session_state.settings.update({
                        "buy_min_indicators": st.session_state.buy_min_indicators,
                        "sell_min_indicators": st.session_state.sell_min_indicators,
                    })

                    st.session_state.submitted = True
                    st.session_state.form_type = side
                    st.rerun()

            # Rest of the Streamlit app
            with st.form(key="indicators_form"):
                st.markdown("<div class='indicator-form-title'>Indicators</div>", unsafe_allow_html=True)
                with st.container():
                    st.markdown('<div class="fullwidth-buttons">', unsafe_allow_html=True)
                    if st.form_submit_button("Bullish", use_container_width=True):
                        signal_dialog("Bullish")
                    if st.form_submit_button("Bearish", use_container_width=True):
                        signal_dialog("Bearish")
                    st.markdown('</div>', unsafe_allow_html=True)



            if st.session_state.submitted:
                with st.container():
                    st.markdown("<div class='success-message'>", unsafe_allow_html=True)
                    st.markdown(f"<h2>{st.session_state.form_type} Indicators Updated</h2>", unsafe_allow_html=True)
                    if st.session_state.selected_indicators:
                        st.write("Selected Indicators:")
                        for indicator in st.session_state.selected_indicators:
                            st.write(f"- {indicator}")
                    else:
                        st.write("No indicators selected.")
                    if st.button("Proceed", key="proceed", use_container_width=True):
                        st.session_state.submitted = False
                        st.session_state.form_type = None
                        st.session_state.selected_indicators = []  # Clear selections on Proceed
                        st.session_state.checkbox_states = {}     # Clear checkbox states
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

            # [Your CSS styles remain unchanged]




        st.markdown("""
        <style>
        .stCheckbox > label > span:has(+ input[type='checkbox']) {
            accent-color: rgb(255, 255, 128) !important;
        }
        .stCheckbox > label > span:has(+ input[type='checkbox']:checked) {
            background-color: rgb(255, 200, 0) !important;
            border-color: rgb(255, 255, 128) !important;
        }
        .stCheckbox > label:hover > span:has(+ input[type='checkbox']) {
            border-color: rgb(255, 255, 128) !important;
        }
        </style>
        """, unsafe_allow_html=True)







        # --- STEP 1: Save total indicators count ---
        # --- STEP 1: Calculate bullish and bearish indicator counts ---
        selected_indicators = st.session_state.get("selected_indicators", [])
        bullish_indicators = [ind for ind in selected_indicators if "Bullish" in ind]
        bearish_indicators = [ind for ind in selected_indicators if "Bearish" in ind]
        total_bullish_indicators = max(len(bullish_indicators), 2)  # Min max of 2 to avoid errors
        total_bearish_indicators = max(len(bearish_indicators), 2)  # Min max of 2 to avoid errors




   

        # === Custom CSS for expander positioning and slider styling ===
        # (Kept same as before for consistent styling)
        st.markdown("""
        <style>
        /* Wrapper to move expander upwards without causing layout jumps */
        .expander-wrapper {
            margin-top: -50px;  /* Adjust this value to move expander higher or lower */
            position: relative;
        }

        /* Reset margin-top on expander OUTER container to avoid jump */
        /* Since expander removed, this affects general details styling */
        details {
            background-color: #2a2a2a !important;
            border-radius: 12px !important;
            border: 1px solid #444 !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.4);
            margin-bottom: 1rem;
            color: #eee;
            margin-top: 0 !important;
        }

        /* Expander summary header text */
        details > summary {
            font-weight: 600;
            font-size: 16px;
            padding: 12px 18px;
            color: #ffde48 !important;
            border-bottom: 1px solid #444;
            border-radius: 12px !important;
            background-color: #2a2a2a !important;
            list-style: none;
        }

        /* Remove default triangle icon */
        details summary::-webkit-details-marker {
            display: none;
        }

        /* Expander inner content */
        details > div {
            background-color: #1e1e1e !important;
            padding: 20px;
            border-radius: 0 0 12px 12px;
            color: #eee;
            margin-top: 0 !important;
        }



        /* Margins for inner divs to keep spacing consistent */
        details > div > div:first-of-type {
            margin-top: 0px !important;
        }


        /* Add shadow to Streamlit form */
        .stForm {
            box-shadow: none !important;
            border-radius: 12px !important; /* optional: match your border radius */
        }
                    
        </style>
        """, unsafe_allow_html=True)






        # ---- ONLY BOX CSS, EACH WITH INDIVIDUAL CLASS ----
        black_box_css = """
        <style>
        .custom-black-box {
            position: absolute;
            top: -568px;           /* Moves box up by 100px */
            left: 152.5%;             /* Moves box 20% to the right from centered 50% */
            width: 100%;
            height: 405px;
            background-color: rgb(42, 42, 42);
            border: 4px solid rgb(26, 27, 28);
            border-radius: 20px;
            pointer-events: none;
            user-select: none;
            z-index: 2;
            transform: translateX(-50%); /* Keeps it horizontally centered relative to left */
            margin-bottom: -500 !important;
            bottom: auto !important;
        }
        </style>
        """


        st.markdown(black_box_css, unsafe_allow_html=True)
        st.markdown('<div class="custom-black-box"></div>', unsafe_allow_html=True)









    with col3_1: 

            







        import json
        import os
        import streamlit as st


        # ------------------------------------------------------------------
        # 2. Set defaults (only once)
        # ------------------------------------------------------------------



        # ------------------------------------------------------------------
        # 3. Save on release
        # ------------------------------------------------------------------
        def _save_on_release():
            save_persistent_state()

        # ------------------------------------------------------------------
        # 4. UI: Sliders (NO `value=`, only `key=`)
        # ------------------------------------------------------------------
        st.markdown('<div style="height: 100px;"></div>', unsafe_allow_html=True)

        # — Max Size —
        st.slider(
            "Max Position Size (%)",
            min_value=0.1,
            max_value=30.0,
            step=0.01,
            key="ETF_max_size",           # ← binds to session_state
            on_change=_save_on_release,
            help="Maximum percent of portfolio per order."
        )




        st.markdown("<div style='width:5px; display:inline-block;'></div>", unsafe_allow_html=True)



        # — Min Size —
        st.slider(
            "Min Position Size (%)",
            min_value=0.1,
            max_value=10.0,
            step=0.01,
            key="ETF_min_size",           # ← ONLY key, NO value=
            on_change=_save_on_release,
            help="Minimum percent of portfolio per order."
        )



        st.markdown("<div style='width:5px; display:inline-block;'></div>", unsafe_allow_html=True)



        # — Stop Loss —
        st.slider(
            "Stop Loss (%)",
            min_value=1.0,
            max_value=200.0,
            step=0.01,
            key="ETF_stop_loss",
            on_change=_save_on_release,
            help="Percent loss to trigger exit."
        )



        st.markdown("<div style='width:5px; display:inline-block;'></div>", unsafe_allow_html=True)


        # — Take Profit —
        st.slider(
            "Take Profit (%)",
            min_value=1.0,
            max_value=500.0,
            step=0.01,
            key="ETF_take_profit",
            on_change=_save_on_release,
            help="Percent gain to trigger exit."
        )



        # ------------------------------------------------------------------
        # 5. Use the values safely
        # ------------------------------------------------------------------
        max_size     = st.session_state.ETF_max_size
        min_size     = st.session_state.ETF_min_size
        stop_loss    = st.session_state.ETF_stop_loss
        take_profit  = st.session_state.ETF_take_profit





















        import streamlit as st
        from datetime import datetime, timedelta
        import streamlit as st
        from datetime import datetime, timedelta

        # --- Ensure account object exists ---
        if st.session_state.get('alpaca_connected') and st.session_state.get('account_info'):
            account_obj = st.session_state['account_info']  # dictionary from session state
        else:
            # fallback: connect to Alpaca API
            api, account_obj, mode = connect_alpaca(
                st.session_state.get('api_key', ''),
                st.session_state.get('api_secret', '')
            )

        # --- Safe float conversion ---
        def safe_float(value):
            try:
                return float(value)
            except (TypeError, ValueError):
                return 0.0

        # --- Robust account cash getter ---
        def get_account_cash(account_obj):
            # Handles REST object with .cash, dictionary with ['cash'], and None-safety
            if hasattr(account_obj, 'cash'):
                cash_value = getattr(account_obj, 'cash', 0.0)
            elif isinstance(account_obj, dict):
                cash_value = account_obj.get('cash', 0.0)
            else:
                cash_value = 0.0
            if cash_value is None:
                cash_value = 0.0
            return safe_float(cash_value)

        # --- Get account value safely ---
        account_value = get_account_cash(account_obj)

        # --- Current time ---
        now = datetime.now()




        st.markdown('<div style="height: 88px;"></div>', unsafe_allow_html=True)



        day_trade = False


        if not day_trade:
            exp_range = st.slider(
                "Expiration Date Range (days from today)",
                min_value=1, max_value=60,
                value=(st.session_state.get("exp_from", 7), st.session_state.get("exp_to", 14)),
                key="exp_range",
                on_change=lambda: (
                    st.session_state.update({
                        "exp_from": st.session_state.exp_range[0],
                        "exp_to":   st.session_state.exp_range[1]
                    }),
                    save_key("exp_from"),
                    save_key("exp_to")
                )
            )
            st.session_state["exp_from"], st.session_state["exp_to"] = exp_range





        with col2: 
            st.markdown(
                """
                <div style="
                    border-left: 1px solid #4f5158; 
                    height: 255px;      /* fixed height since 100% won't work */
                    margin: 0 auto;     /* centers horizontally */
                    width: 0;           /* no width, border is visible */
                "></div>
                """,
                unsafe_allow_html=True
            )




        with col1:

            import streamlit as st

            # ✅ Session state defaults
            for k, v in {"buy": 1, "sell": 1}.items():
                if k not in st.session_state:
                    st.session_state[k] = v

            # Layout with 1 column
            col1 = st.columns(1)[0]

            # ✅ Clean + functional slider CSS with fixed 50% fill and smooth fades
            css = """
            <style>
            /* ====== TRACKS ====== */

            /* Bullish Track with fixed 50% fill from #ffe899 to #444444 */
            div[data-testid="stSlider"]:nth-of-type(1) div[data-baseweb="slider"] > div > div {
            background: linear-gradient(to right,
                #ffe899 0%,
                #ffe899 24%,
                #444444 56%,
                #444444 100%
            ) !important;


                height: 6px !important;
                border-radius: 3px !important;
                box-shadow: inset 0 1px 2px rgba(0,0,0,0.2);
            }

            /* Bearish Track with fixed 50% fill from #EF4444 to #DC2626 */
            div[data-testid="stSlider"]:nth-of-type(2) div[data-baseweb="slider"] > div > div {
                background: linear-gradient(to right,
                    #EF4444 0%,
                    #EF4444 34%,
                    #DC2626 66%,
                    #DC2626 100%
                ) !important;
                height: 6px !important;
                border-radius: 3px !important;
                box-shadow: inset 0 1px 2px rgba(0,0,0,0.2);
            }

            /* ====== THUMBS ====== */

            div[data-testid="stSlider"] div[role="slider"] {
                background: #fff !important;
                border: 2px solid transparent !important;
                width: 14px !important;
                height: 14px !important;
                border-radius: 50% !important;
                margin-top: 0px !important;
                box-shadow:
                    0 2px 4px rgba(0,0,0,0.25),
                    0 0 0 2px rgba(255,255,255,0.9) inset !important;
                transition: box-shadow 0.15s ease-in-out;
                cursor: pointer !important;
                outline: none !important;
            }

            /* Thumb border colors */
            div[data-testid="stSlider"]:nth-of-type(1) div[role="slider"] {
                border-color: #ffe899 !important;
            }

            div[data-testid="stSlider"]:nth-of-type(2) div[role="slider"] {
                border-color: #EF4444 !important;
            }

            /* Hover and active states */
            div[data-testid="stSlider"] div[role="slider"]:hover {
                box-shadow:
                    0 3px 6px rgba(0,0,0,0.35),
                    0 0 0 3px rgba(255,255,255,0.9) inset !important;
            }

            div[data-testid="stSlider"] div[role="slider"]:active {
                box-shadow:
                    0 4px 8px rgba(0,0,0,0.4),
                    0 0 0 3px rgba(255,255,255,0.9) inset !important;
            }

            /* Hide tick bar */
            div[data-testid="stTickBar"] > div {
                background: transparent !important;
            }
            </style>
            """




            st.markdown(css, unsafe_allow_html=True)




            with col1:  # or wherever your sliders are
                recompute_indicator_limits()



                # Prevent StreamlitValueAboveMaxError by clamping saved values
                st.session_state.buy_min_indicators = max(
                    1, 
                    min(st.session_state.get("buy_min_indicators", 1), st.session_state.total_bullish or 1)
                )
                st.session_state.sell_min_indicators = max(
                    1, 
                    min(st.session_state.get("sell_min_indicators", 1), st.session_state.total_bearish or 1)
                )


                # Ensure defaults exist
                if "buy_min_indicators" not in st.session_state:
                    st.session_state.buy_min_indicators = 1
                if "sell_min_indicators" not in st.session_state:
                    st.session_state.sell_min_indicators = 1



                st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)


                # === BULLISH SLIDER ===
                st.slider(
                    "Minimum Bullish Indicators",
                    min_value=1,
                    max_value=st.session_state.total_bullish,
                    step=1,
                    key="buy_min_indicators",  # This binds to session_state
                    on_change=lambda: [
                        # Save to settings file
                        st.session_state.settings.__setitem__("buy_min_indicators", st.session_state.buy_min_indicators),
                        save_settings(st.session_state.settings),
                        # Optional: also save to persistent state if you want double backup
                        save_persistent_state()
                    ],
                    help="Requires this many bullish signals to enter a long position."
                )



                st.markdown("<div style='height: 27px;'></div>", unsafe_allow_html=True)


                # === BEARISH SLIDER ===
                st.slider(
                    "Minimum Bearish Indicators",
                    min_value=1,
                    max_value=st.session_state.total_bearish,
                    step=1,
                    key="sell_min_indicators",
                    on_change=lambda: [
                        st.session_state.settings.__setitem__("sell_min_indicators", st.session_state.sell_min_indicators),
                        save_settings(st.session_state.settings),
                        save_persistent_state()
                    ],
                    help="Requires this many bearish signals to enter a short position."
                )









                     
                                                                    

    with col3_3:
        import streamlit as st
        from datetime import datetime

        instrument_symbols = ['SPY', 'QQQ', 'DIA', 'UUP']
        bias_colors = {
            "Bullish": "#62ad50",
            "Neutral": "#dbb930",
            "Bearish": "#d8483e"
        }

        bias_bg = {
            "Bullish": "linear-gradient(120deg, #1b3e1e 15%, #467a44 50%, #1e5b28 85%, #0e1c10 100%)",
            "Neutral": "linear-gradient(120deg, #403a1a 15%, #7c744c 50%, #725c2e 85%, #262110 100%)",
            "Bearish": "linear-gradient(120deg, #4a181d 15%, #784946 50%, #682528 85%, #1e0c0b 100%)"
        }

        def update_bias():
            market, details = daily_bias(return_details=True, show_instruments=True)
            st.session_state.bias_market = market
            st.session_state.bias_details = details
            st.session_state.last_refresh = datetime.now().astimezone()
            

        # Call update_bias unconditionally at the beginning
        if "bias_market" not in st.session_state or "bias_details" not in st.session_state:
            update_bias()
        if 'last_refresh' not in st.session_state:
            st.session_state.last_refresh = datetime.now().astimezone()

        now = datetime.now().astimezone()
        tz_str = now.strftime('%Z')
        dt_str = now.strftime('%B %d, %Y, %I:%M:%S %p')
        primary_gradient = primary_color

        st.markdown(f"""
        <style>
        .right-column {{
            width: 320px;
            margin-left: auto;
            margin-top: 10px;
            font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
            text-align: right;
        }}
        .etf-header-row {{
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            margin-bottom: 8px;
            padding-bottom: 0;
            direction: rtl;
        }}
        .etf-gradient-text {{
            font-size: 1.3rem;
            font-weight: 800;
            letter-spacing: 1.2px;
            background: {primary_gradient};
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-fill-color: transparent;
            margin: 0;
            padding: 0;
            border: none;
            box-shadow: none;
            display: inline-block;
            line-height: 1.05;
        }}
        .etf-refresh-time {{
            font-size: 11px;
            color: #bbbbbb;
            padding: 0 3px 0 0;
            font-weight: 500;
            line-height: 1.6rem;
            margin: 0;
            white-space: nowrap;
            vertical-align: baseline;
        }}

        /* ⬛ Base box style (bias + market bias) */
        .bias-box, .market-bias-box {{
            border-radius: 13px;
            border: 3px solid rgb(26, 27, 28);
            position: relative;
            overflow: hidden;
            z-index: 1;
            background: none;
            box-shadow:
                0 4px 6px rgba(0, 0, 0, 0.4);  /* 🖤 Default black shadow */
            transition:
                box-shadow 0.20s cubic-bezier(.4,0,.2,1),
                border-color 0.19s,
                transform 0.14s cubic-bezier(.5,0,.4,1);
            cursor: default;
            height: 40px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            min-width: 82px;
            max-width: 115px;
            margin-bottom: 8px;
        }}

        /* 🌟 Special styling for Market Bias Box */
        .market-bias-box {{
            min-width: 170px;
            max-width: 255px;
            height: 42px;
            display: flex;
            flex-direction: row;
            justify-content: space-around;
            align-items: center;
            padding: 0 12px;
            margin-bottom: 8px;
            margin-top: -20px;
        }}

        .bias-box:hover,
        .market-bias-box:hover {{
            position: relative;
            z-index: 10;
            box-shadow:
                0 0 3px 2px var(--glow-color, transparent), /* ✨ Muted color glow on top */
                0 6px 8px rgba(0, 0, 0, 0.45);             /* 🖤 Stronger black shadow below */
            transform: scale(1.05);
        }}

        /* ✨ Glow color variable */
        .market-bias-box {{
            --glow-color: rgba(26, 27, 28, 0.4); /* Optional black base */
        }}

        /* 🧊 Subtle shine animation (restored) */
        .bias-box::after,
        .market-bias-box::after {{
            content:'';
            position:absolute;
            left:-72%;
            top:0;
            height:100%;
            width:61%;
            border-radius:14px;
            background: linear-gradient(
                107deg,
                rgba(255,255,255,0) 0%,
                rgba(255,255,255,0.008) 34%,
                rgba(255,255,255,0.03) 47%,
                rgba(255,255,255,0.008) 67%,
                rgba(255,255,255,0) 100%
            );
            z-index:1;
            pointer-events:none;
        }}
        .bias-box:hover::after {{
            animation: shine-slide 1.28s cubic-bezier(.44,.2,.47,1) forwards;
        }}
        .market-bias-box:hover::after {{
            animation: shine-slide 1.9s cubic-bezier(.44,.2,.47,1) forwards;
        }}
        @keyframes shine-slide {{
            from {{ left:-72%; }}
            to   {{ left:127%; }}
        }}

        /* 🧾 Label styling inside boxes */
        .bias-box .label {{
            font-size: 13px;
            font-weight: 700;
            text-align: center;
            color: #ddd;
            z-index: 4;
        }}
        .bias-box .subtext {{
            color: #aaa;
            font-size: 10px;
            font-weight: 500;
            margin-top: -5px;
            width: 100%;
            text-align: center;
            z-index: 4;
        }}
        .market-bias-box > div:first-child {{
            font-weight: 600;
            font-size: 11px;
            color: #bbb;
        }}
        .market-bias-box > div:last-child {{
            font-size: 16px;
            font-weight: 700;
            color: var(--market-color);
        }}

        .bias-box.uup-hover-zone:{{
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(30,30,60,0.97);
            border-radius: 10px;
            color: #ffeebb;
            box-shadow: 0 8px 22px 0 rgba(24,22,34,0.13), 0 0 16px 3px #dbb930;
            font-size: 10px !important;
            text-align: center;
            padding: 5px 8px;
            z-index: 50;
        }}

        /* Circle refresh button */
        .custom-refresh-button {{
            background: transparent;
            border: none;
            font-size: 1.6rem;
            color: #F5BF03;
            cursor: pointer;
            padding: 0; /* Remove padding */
            width: 2.5rem; /* Fixed width */
            height: 2.5rem; /* Fixed height */
            border-radius: 50%; /* Make it a circle */
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s ease;
            margin: 0;
            position: relative;
        }}

        .custom-refresh-button:hover {{
            background: rgba(255, 215, 0, 0.1);
            transform: scale(1.05);
        }}

        .custom-refresh-button:active {{
            transform: scale(0.95);
        }}

        .custom-refresh-button.spinning {{
            animation: spin 0.5s linear;
        }}

        /* Tooltip styling like dot buttons */
        .custom-refresh-button:hover::after {{
            content: "Refresh bias";
            position: absolute;
            bottom: 125%;
            left: 50%;
            transform: translateX(-50%);
            background-color: #333;
            color: #fff;
            padding: 4px 8px;
            border-radius: 4px;
            white-space: nowrap;
            font-size: 0.8rem;
            pointer-events: none;
            z-index: 15;
        }}

        .custom-refresh-button:hover::before {{
            content: "";
            position: absolute;
            bottom: 115%;
            left: 50%;
            transform: translateX(-50%);
            border-width: 5px;
            border-style: solid;
            border-color: #333 transparent transparent transparent;
            pointer-events: none;
            z-index: 15;
        }}

        @keyframes spin {{
            from {{ transform: rotate(0deg); }}
            to {{ transform: rotate(360deg); }}
        }}
        </style>
        """, unsafe_allow_html=True)


        with st.container():
            col_button, col_time = st.columns([1, 5])

            with col_button:
                if st.button("↻ Refresh bias", key="refresh_button"):
                    with st.spinner("Refreshing market bias..."):
                        update_bias()
                    st.session_state.settings["last_refresh"] = datetime.now().astimezone().isoformat()
                    save_settings(st.session_state.settings)

                st.markdown("""
                    <style>
                    div.stButton > button {
                        position: relative;
                        font-size: 1.6rem !important;
                        color: #F5BF03 !important;
                        background: rgba(0, 0, 0, 0.5) !important;
                        border-radius: 100px;
                        border: 2px solid #F5BF03 !important;
                        padding: 8px 16px;
                        margin-bottom: 12px; /* give spacing below */
                        cursor: pointer;
                        transition: all 0.2s ease;
                        z-index: 2;
                    }
                    div.stButton > button:hover {
                        background: rgba(255, 215, 0, 0.4) !important;
                        transform: scale(1.05);
                    }

                    /* ↻ overlay */
                    .button-overlay {
                        position: absolute;
                        bottom: -33px;  /* closer to bottom edge */
                        left: 16px;
                        font-size: 1.6rem;
                        color: #F5BF03;
                        pointer-events: none;
                        z-index: 2;
                        user-select: none;
                        transition: transform 0.3s ease, color 0.3s ease;
                        will-change: transform, color;
                    }

                    /* Hover effect -> blue */
                    .button-overlay.hover-blue {
                        color: #1E90FF;
                    }

                    /* Click animation (pop + rotate + shrink) */
                    .button-overlay.animate {
                        animation: popRotate 0.5s ease forwards;
                    }
                    @keyframes popRotate {
                        0%   { transform: scale(1) rotate(0deg);   }
                        40%  { transform: scale(0.6) rotate(-180deg);}
                        70%  { transform: scale(1.3) rotate(-270deg);}
                        100% { transform: scale(1) rotate(-360deg);}
                    }
                    </style>

                    <div id="spin-icon" class="button-overlay">↻</div>

                    <script>
                    const icon = document.getElementById('spin-icon');
                    const button = document.querySelector('div.stButton > button');

                    // Animate on click
                    button.addEventListener('click', () => {
                        icon.classList.remove('animate'); // reset if repeated
                        void icon.offsetWidth;           // force reflow (restarts animation)
                        icon.classList.add('animate');
                    });

                    // Hover color
                    button.addEventListener('mouseenter', () => {
                        icon.classList.add('hover-blue');
                    });
                    button.addEventListener('mouseleave', () => {
                        icon.classList.remove('hover-blue');
                    });
                    </script>
                """, unsafe_allow_html=True)

                if st.button("↻ Refresh bias"):
                    update_bias()
                

            with col_time:
                st.markdown(f"""
                <style>
                .etf-refresh-time {{
                    font-size: 11px;
                    color: #bbbbbb;
                    font-weight: 500;
                    white-space: nowrap;
                    text-align: right;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    padding-top: 2px;
                    margin-bottom: 12px;
                }}
                .etf-refresh-time .label {{
                    font-weight: 500;
                    font-size: 11px;
                    color: #bbbbbb;
                    margin-bottom: 1px;
                }}
                .etf-refresh-time .time {{
                    font-weight: 700;
                    font-size: 12px;
                    color: #bbbbbb;
                }}
                </style>

                <div class="etf-refresh-time">
                    <div class="label">Last refresh:</div>
                        <div class="time">{now.strftime('%I:%M:%S %p %Z')}</div>
                        <div class="date">{now.strftime('%B %d, %Y')}</div>

                </div>
                """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)





        with st.container():
            market_bias = st.session_state.bias_market
            bias_details = st.session_state.bias_details

            main_color = bias_colors[market_bias]
            market_bg = bias_bg[market_bias]

            market_html = f"""
            <div class="market-bias-box" style="--market-color:{main_color}; background: {market_bg}; max-width: 100%;">
                <div>Market Daily Bias</div>
                <div>{market_bias}</div>
            </div>
            """
            st.markdown(market_html, unsafe_allow_html=True)

            def bias_box_html(symbol, bias):
                color = bias_colors[bias]
                bg = bias_bg[bias]
                return f"""
                <div class="bias-box" style="--glow-color:{color}; background:{bg};max-width: 100%;">
                    <div class="label">{symbol}</div>
                    <div class="subtext">{bias}</div>
                </div>
                """

            col_left, col_right = st.columns(2)
            with col_left:
                st.markdown(bias_box_html('SPY', bias_details['SPY']), unsafe_allow_html=True)
                st.markdown(bias_box_html('DIA', bias_details['DIA']), unsafe_allow_html=True)
            with col_right:
                st.markdown(bias_box_html('QQQ', bias_details['QQQ']), unsafe_allow_html=True)
                st.markdown(bias_box_html('UUP', bias_details['UUP']), unsafe_allow_html=True)

        st.markdown('<div style="margin-bottom: 30px;"></div>', unsafe_allow_html=True)






        import streamlit as st

        # Global CSS for cool toggles
        st.markdown("""
        <style>
        .toggle-container {
            display: flex;
            align-items: center;
            cursor: pointer;
            margin: 10px 0;
        }

        .cool-toggle {
            width: 50px;        /* smaller */
            height: 28px;       /* smaller */
            background-color: #333;
            border-radius: 28px;
            position: relative;
            transition: all 0.4s;
            box-shadow: 0 0 3px #111;  /* dark shadow instead of glow */
        }

        .cool-toggle.active {
            background-color: #F5BF03;  /* yellow when active */
            box-shadow: 0 0 3px #111;   /* dark shadow, no glow */
        }

        .cool-toggle::before {
            content: "";
            position: absolute;
            height: 22px;       /* smaller circle */
            width: 22px;        /* smaller circle */
            left: 3px;
            bottom: 3px;
            background-color: white;
            border-radius: 50%;
            transition: transform 0.4s;
            box-shadow: 0 0 3px #111;  /* dark shadow around circle */
        }

        .cool-toggle.active::before {
            transform: translateX(22px);  /* moves according to smaller size */
        }

        .toggle-label {
            margin-left: 8px;
            color: #F5BF03;   /* label in yellow */
            font-family: Arial, sans-serif;
            font-size: 14px;
        }

        .tooltip {
            position: relative;
            display: inline-block;
            margin-left: 6px;
        }

        .tooltip .tooltiptext {
            visibility: hidden;
            width: 200px;
            background-color: #333;
            color: #fff;
            text-align: left;
            border-radius: 5px;
            padding: 6px;
            position: absolute;
            z-index: 1000;
            bottom: 125%;
            left: 50%;
            margin-left: -100px;
            opacity: 0;
            transition: opacity 0.3s;
            font-size: 12px;
            pointer-events: none;
        }

        .tooltip:hover .tooltiptext {
            visibility: visible;
            opacity: 1;
        }

        .tooltip .tooltip-icon {
            background-color: #F5BF03;   /* yellow icon */
            border-radius: 50%;
            color: black;
            font-weight: bold;
            font-family: Arial, sans-serif;
            font-size: 14px;
            width: 18px;
            height: 18px;
            line-height: 18px;
            text-align: center;
            user-select: none;
        }

        /* Hide the button visually */
        button[data-baseweb="button"] {
            position: absolute;
            left: -9999px; /* Move off-screen */
        }
        </style>
        """, unsafe_allow_html=True)


        st.markdown("""
            <hr style="margin-top: -20px;">
        """, unsafe_allow_html=True)
        

        st.markdown('<h3 style="color:#ffe899;">Direction Settings</h3>', unsafe_allow_html=True)


        st.markdown(
            "<span style='color: gray; font-size: 0.9em;'>Bias will alternate each loop by default, starting with the current market bias.</span>",
            unsafe_allow_html=True
        )



        import streamlit as st
        import os
        import json

        # ------------------------------------------------------------------
        # 1. PERSISTENCE: Load & Save to JSON File
        # ------------------------------------------------------------------

        # ------------------------------------------------------------------
        # 2. DEFAULT VALUES (only if missing)
        # ------------------------------------------------------------------
        toggles_defaults = {
            "etf_options_mode": True,
            "fallback_bias": True,
            "day_trade": False,
            "bias_only": False,
            "bullish_only": False,
            "bearish_only": False,
        }
        for key, default in toggles_defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default

        # ------------------------------------------------------------------
        # 3. CALLBACKS
        # ------------------------------------------------------------------
        def save_on_change():
            """Simple save — no args."""
            save_persistent_state()

        def bias_callback(selected: str):
            """Mutual exclusivity + save."""
            if st.session_state[selected]:  # Only when turned ON
                for mode in ["bias_only", "bullish_only", "bearish_only"]:
                    st.session_state[mode] = (mode == selected)
            save_persistent_state()

        # ------------------------------------------------------------------
        # 4. LAYOUT: Two Columns
        # ------------------------------------------------------------------


        col_left, col_right = st.columns(2)

        
        # ------------------- LEFT COLUMN -------------------
        with col_left:
            st.markdown("<div style='height:30px;'></div>", unsafe_allow_html=True)

            # Options
            st.checkbox(
                "Options",
                key="etf_options_mode",
                help="When Options is off, only ETF shares will be purchased.",
                on_change=save_on_change  # No args → no error
            )

            # Bullish on Neutral
            st.checkbox(
                "Bullish on Neutral",
                key="fallback_bias",
                on_change=save_on_change
            )

            # Day Trade
            account_value = st.session_state.get("account_value", 0)
            st.checkbox(
                "Day Trade",
                key="day_trade",
                disabled=account_value < 25_000,
                help="Enable day trading mode (requires $25k+ account).",
                on_change=save_on_change
            )
            if st.session_state.day_trade:
                st.info("Day Trade mode is ON. Expiration sliders hidden.")

        # ------------------- RIGHT COLUMN -------------------
        with col_right:
            c1, c2 = st.columns([2, 1])
            with c1:
                st.markdown("**Bias Mode**")
            with c2:
                if not st.session_state.fallback_bias:


                    st.markdown(
                        """
                        <style>
                        .custom-tooltip-2 {
                            position: relative;
                            display: inline-block;
                            cursor: help;
                            margin-left: 8px;
                        }
                        .custom-tooltip-2 .tooltiptext-2 {
                            visibility: hidden;
                            width: 240px;
                            background-color: #ffe899; /* bright yellow background */
                            color: black;
                            text-align: center;
                            border-radius: 10px;
                            border: 2px solid #444444;
                            padding: 4px 10px;
                            position: absolute;
                            z-index: 4000;
                            top: 50%;
                            right: 150%;  /* appear on right side */
                            transform: translateY(-50%);
                            box-shadow: 0 2px 8px #ffe8990033;
                            font-size: 0.8em;
                            pointer-events: none;
                            opacity: 0;
                            transition: opacity 0.15s;
                            white-space: normal;
                            user-select: none;
                        }
                        .custom-tooltip-2:hover .tooltiptext-2 {
                            visibility: visible;
                            opacity: 1;
                            pointer-events: all;
                        }
                        .custom-tooltip-2 > span.icon-2 {
                            display: inline-block;
                            width: 16px;
                            height: 16px;
                            background: #ffe899;  /* yellow */
                            color: black;
                            border-radius: 50%;
                            text-align: center;
                            line-height: 16px;
                            font-weight: bold;
                            font-size: 12px;
                            user-select: none;
                        }
                        </style>
                        <span class="custom-tooltip-2">
                            <span class="icon-2">i</span>
                            <span class="tooltiptext-2">
                                Bearish on Neutral because “Bullish on Neutral” is off
                            </span>
                        </span>
                        """,
                        unsafe_allow_html=True,
                    )


            # Bias Only
            st.checkbox(
                "Bias Only",
                key="bias_only",
                help="Trades in direction of Daily Bias; does not trade when neutral.",
                on_change=bias_callback,
                args=("bias_only",)  # Pass selected mode
            )

            # Bullish Only
            st.checkbox(
                "Bullish Only",
                key="bullish_only",
                help="Trade only bullish positions.",
                on_change=bias_callback,
                args=("bullish_only",)
            )

            # Bearish Only
            st.checkbox(
                "Bearish Only",
                key="bearish_only",
                help="Trade only bearish positions.",
                on_change=bias_callback,
                args=("bearish_only",)
            )


        # ------------------------------------------------------------------
        # 6. FINAL SAVE (safety net)
        # ------------------------------------------------------------------
        save_persistent_state()












        st.markdown("---", unsafe_allow_html=True)

        col1, col2 = st.columns([1,1])
        with col2:
            st.markdown(f"""**Latest expiration:**  
        {(now + timedelta(days=st.session_state['exp_to'])).date()}""")

        with col1:
            st.markdown(f"""**Earliest expiration:**  
        {(now + timedelta(days=st.session_state['exp_from'])).date()}""")
            
            api, account, mode = connect_alpaca(api_key, api_secret)
            cash_value = float(account.cash) if account.cash is not None else 0.0
            st.markdown(f"**Cash: ${cash_value:,}**")













    # INDICATOR SELECT BOX








    # ---------------- CSS Styling ----------------
    st.markdown(f"""
    <style>
    /* Styled form container (dark, no gradient here) */
    .stForm {{
        background-color: #1C1C1C;
        border-radius: 15px;
        padding: 30px 25px;
        color: #c0c0c0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}

    /* Two-column flex layout with a vertical line in between */
    .main-columns {{
        display: flex;
        justify-content: space-between;
        flex-wrap: nowrap;
        position: relative;
    }}

    /* Inner container for each side */
    .column-wrapper {{
        flex: 1;
        padding: 0 30px;
        min-width: 350px;
    }}



    /* Bullish and Bearish column styling */
    .bullish-column, .bearish-column {{
        flex: 1;
    }}

    /* Header labels */
    .bullish-label {{
        font-weight: 900;
        font-size: 28px;
        margin-bottom: 30px;
        color: #62ad50;
        user-select: none;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.7);
    }}

    .bearish-label {{
        font-weight: 900;
        font-size: 28px;
        margin-bottom: 30px;
        color: #bc3f3f;
        user-select: none;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.7);
    }}

    /* Section headers */
    .section-header {{
        position: relative;
        font-weight: 700;
        font-size: 20px;
        margin-bottom: 24px;
        color: #888;
        padding-bottom: 6px;
        text-shadow: 0 0 3px rgba(0,0,0,0.6);
    }}

    .section-header::after {{
        content: "";
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;  /* Viewport width */

        height: 4px;
        background-color: #888;
        border-radius: 10px;
        opacity: 0.8;
    }}




    /* Checkbox label styling */
    .stCheckbox > label > div {{
        color: #c0c0c0;
        font-weight: 500;
        font-size: 14.5px;
        user-select: none;
        text-shadow: 0 0 2px rgba(0,0,0,0.5);
    }}

    /* Reduce checkbox spacing */
    .stCheckbox {{
        margin-bottom: 6px !important;
    }}

    </style>
    """, unsafe_allow_html=True)






    techniques = {
        "Moving Averages": [
            "EMA Bullish", "EMA Bearish", "TEMA Bullish", "TEMA Bearish", "Hull MA Bullish", "Hull MA Bearish"
        ],
        "Momentum Indicators": [
            "MACD Bullish", "MACD Bearish", "RSI Bullish", "RSI Bearish",
            "Stochastic Bullish", "Stochastic Bearish", "ROC Bullish", "ROC Bearish",
            "Williams %R Bullish", "Williams %R Bearish", "Z-Score Bullish", "Z-Score Bearish"
        ],
        "Volatility Indicators": [
            "ATR Bullish", "ATR Bearish", "Bollinger Bands Bullish", "Bollinger Bands Bearish",
            "Donchian Channels Bullish", "Donchian Channels Bearish", "Keltner Channels Bullish", "Keltner Channels Bearish",
            "Pivot Points Bullish", "Pivot Points Bearish", "Fibonacci Retracement Bullish", "Fibonacci Retracement Bearish"
        ],
        "Volume Indicators": [
            "OBV Bullish", "OBV Bearish", "CMF Bullish", "CMF Bearish", "Accumulation/Distribution Bullish", "Accumulation/Distribution Bearish",
            "High Volume Bullish", "High Volume Bearish", "Elder Force Index Bullish", "Elder Force Index Bearish"
        ],
        "Smart Money Concepts": [
            "BOS Bullish", "Liquidity Sweep Bullish", "Order Block Bullish", "FVG Bullish", "Discount Bullish",
            "BOS Bearish", "Liquidity Sweep Bearish", "Order Block Bearish", "FVG Bearish", "Discount Bearish"
        ]
    }

    def get_signals_by_type(side, category):
        confluences = techniques.get(category, [])
        return [c for c in confluences if side in c]

    bullish_volatility = get_signals_by_type("Bullish", "Volatility Indicators")
    bearish_volatility = get_signals_by_type("Bearish", "Volatility Indicators")
    bullish_momentum = get_signals_by_type("Bullish", "Momentum Indicators")
    bearish_momentum = get_signals_by_type("Bearish", "Momentum Indicators")
    bullish_volume = get_signals_by_type("Bullish", "Volume Indicators")
    bearish_volume = get_signals_by_type("Bearish", "Volume Indicators")
    bullish_smart = get_signals_by_type("Bullish", "Smart Money Concepts")
    bearish_smart = get_signals_by_type("Bearish", "Smart Money Concepts")
    bullish_ma = get_signals_by_type("Bullish", "Moving Averages")
    bearish_ma = get_signals_by_type("Bearish", "Moving Averages")

    # Helper function to collect selected indicators from checkboxes
    def collect_selected_indicators():
        selected = []

        def collect_selected(indicator_list, prefix):
            for conf in indicator_list:
                key = f"{prefix}_{conf.replace(' ', '_').lower()}"
                if st.session_state.get(key, False):
                    selected.append(conf)

        collect_selected(bullish_volatility, "bullish_volatility")
        collect_selected(bullish_momentum, "bullish_momentum")
        collect_selected(bullish_volume, "bullish_volume")
        collect_selected(bullish_smart, "bullish_smart")
        collect_selected(bullish_ma, "bullish_ma")

        collect_selected(bearish_volatility, "bearish_volatility")
        collect_selected(bearish_momentum, "bearish_momentum")
        collect_selected(bearish_volume, "bearish_volume")
        collect_selected(bearish_smart, "bearish_smart")
        collect_selected(bearish_ma, "bearish_ma")

        return selected

    # Set initial checkbox states based on saved selections for persistence
    saved = set(st.session_state.settings.get("selected_indicators", []))















    import streamlit as st
    import atexit

    # === LAYOUT HEADER LINE (CENTERED) ===
    col1, col2, col3 = st.columns([0.2, 1, 0.2])
    with col2:
        st.markdown("---")



    @st.cache_resource
    def get_alpaca_account():
        try:
            print("Connecting to Alpaca...")  # Check your terminal
            api, account, mode = connect_alpaca(api_key, api_secret)
            print(f"API: {api}, Account: {account}, Mode: {mode}")  # Debug print
            if account is None:
                print("ACCOUNT IS NONE!")
            else:
                print(f"Account cash: {account.cash}")
            return api, account, mode
        except Exception as e:
            print(f"Connection error: {e}")  # Terminal output
            return None, None, None


    # === GLOBAL CSS (ADD ONCE) ===
    st.markdown("""
    <style>

        /* Tighten top/bottom padding of main content area */
        header.stAppHeader {
            background-color: transparent;
        }

        section.stMain .block-container {
            padding-top: 0rem !important;
            padding-bottom: 0rem !important;
        }

        /* Remove / reduce vertical space between horizontal blocks (rows of columns) */
        div[data-testid="stHorizontalBlock"] {
            margin-top: 0rem !important;
            margin-bottom: 0rem !important;
            padding-top: 0rem !important;
            padding-bottom: 0rem !important;
            gap: 0.25rem !important;  /* adjust horizontal gap between columns if needed */
        }

        /* If you want even tighter stacking, you can try negative margins:
        div[data-testid="stHorizontalBlock"] {
            margin-top: -0.25rem !important;
            margin-bottom: -0.25rem !important;
        }
        */



        /* Disable clipping for tooltip container column */
        .tooltip-layer {
            position: relative !important;
            overflow: visible !important;
            z-index: 9999 !important;
            margin-top: 0rem !important;
            margin-bottom: 0rem !important;
        }

        /* Tooltip sits above all Streamlit elements */
        .custom-tooltip {
            position: relative;
            display: inline-block;
            cursor: help;
            z-index: 9999 !important;
            margin-top: 0rem !important;
            margin-bottom: 0rem !important;
        }

        .custom-tooltip .tooltiptext {
            visibility: hidden;
            width: 340px;
            background-color: #ffe899;
            color: #222;
            text-align: left;
            border-radius: 10px;
            border: 3px solid #444;
            padding: 12px;
            position: absolute;
            z-index: 100000 !important;   /* highest layer */
            bottom: 120%;
            left: 50%;
            transform: translateX(-50%);
            box-shadow: 0 4px 16px rgba(0,0,0,0.35);
            font-size: 0.95em;
            opacity: 0;
            transition: opacity 0.15s ease-in-out;
            pointer-events: none;
            overflow: visible !important;
            white-space: normal;
        }

        .custom-tooltip:hover .tooltiptext {
            visibility: visible;
            opacity: 1;
            pointer-events: all;
        }

        .custom-tooltip > span:first-child {
            font-size: 2em;
            color: #00bfae;
            transform: translate(17px, -25px);
            display: inline-block;
        }

    </style>
    """, unsafe_allow_html=True)

    # === THE FINAL NON-STACKING ROW ===
    col1, spacer1, col2, tooltip_col, col3 = st.columns([1, 0.08, 1, 0.08, 1])

    with col1:
        lines = [
            f"BUY when ≥ **{st.session_state.buy_min_indicators}** bullish indicators",
            f"SELL when ≥ **{st.session_state.sell_min_indicators}** bearish indicators",
        ]
        st.success("\n\n".join(lines))

    with col2:
        max_pos_pct = float(st.session_state.get('ETF_max_size', 0.0))
        min_pos_pct = float(st.session_state.get('ETF_min_size', 0.0))
        cash = float(account.cash)
        max_pos_dollar = max_pos_pct * cash / 100
        min_pos_dollar = min_pos_pct * cash / 100
        lines_pos = [
            f"Max Position Size: **{max_pos_pct:.2f}%** (~${max_pos_dollar:,.2f})",
            f"Min Position Size: **{min_pos_pct:.2f}%** (~${min_pos_dollar:,.2f})",
        ]
        st.success("\n\n".join(lines_pos))

    with col3:
        stop_loss_pct = float(st.session_state.get('ETF_stop_loss', 0.0))
        take_profit_pct = float(st.session_state.get('ETF_take_profit', 0.0))
        max_stop_loss_amt = stop_loss_pct * (max_pos_pct * cash / 100) / 100
        min_stop_loss_amt = stop_loss_pct * (min_pos_pct * cash / 100) / 100
        max_take_profit_amt = take_profit_pct * (max_pos_pct * cash / 100) / 100
        min_take_profit_amt = take_profit_pct * (min_pos_pct * cash / 100) / 100
        lines_sl_tp = [
            f"Stop Loss: **\${min_stop_loss_amt:.2f} – \${max_stop_loss_amt:.2f}**",
            f"Take Profit: **\${min_take_profit_amt:.2f} – \${max_take_profit_amt:.2f}**",
        ]
        st.success("\n\n".join(lines_sl_tp))

    with tooltip_col:
        st.markdown('<div class="tooltip-layer">', unsafe_allow_html=True)

        st.markdown("""
            <div class="custom-tooltip" style="text-align:center; margin-top: 8px;">
                <span>❗️</span>
                <span class="tooltiptext">
                    Stop Loss and Take Profit are only available when program is running and connected to the internet.<br>
                    Alpaca does not currently support fully-functional stop and stop-limit orders for options.
                </span>
            </div>
        """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # === SAVE SETTINGS ON EXIT ===
    atexit.register(lambda: save_settings(st.session_state.settings))























































with tabs[4]:
    st.markdown(f"<h2 style='color: {primary_color};'>Crypto</h2>", unsafe_allow_html=True)
    st.write("Not Available in Beta.")
    if st.session_state.active_tab == "Crypto":
        st.session_state.active_tab = "Crypto"







if "trading" not in st.session_state:
    st.session_state.trading = False
if "last_bias" not in st.session_state:
    st.session_state.last_bias = "bullish"  # default












from yahoo_earnings_calendar import YahooEarningsCalendar
import datetime

yec = YahooEarningsCalendar()

def has_upcoming_earnings(ticker, days_ahead):
    today = datetime.datetime.now()
    future_date = today + datetime.timedelta(days=days_ahead)
    earnings = yec.get_earnings_of(ticker)
    for event in earnings:
        earnings_date = event['startdatetime'] if 'startdatetime' in event else None
        if earnings_date:
            earnings_dt = datetime.datetime.strptime(earnings_date, '%Y-%m-%d %H:%M:%S')
            if today <= earnings_dt <= future_date:
                return True
    return False



def check_and_apply_stop_loss_and_take_profit(api, stop_loss_percent, take_profit_percent, output_log):
    positions = api.list_positions()
    for pos in positions:
        qty = int(pos.qty)
        avg_price = float(pos.avg_entry_price)
        current_price = float(getattr(pos, "current_price", getattr(pos, "market_price", 0)))

        if qty == 0 or avg_price == 0:
            continue

        invested_capital = avg_price * abs(qty)

        if qty > 0:
            unrealized_loss = (avg_price - current_price) * qty
            unrealized_gain = (current_price - avg_price) * qty
        else:
            unrealized_loss = (current_price - avg_price) * abs(qty)
            unrealized_gain = (avg_price - current_price) * abs(qty)

        loss_percent = (unrealized_loss / invested_capital) * 100
        gain_percent = (unrealized_gain / invested_capital) * 100

        # Check stop loss
        if loss_percent >= stop_loss_percent:
            side = "sell" if qty > 0 else "buy"
            qty_to_close = abs(qty)
            order_type = "stop loss"
        # Check take profit
        elif gain_percent >= take_profit_percent:
            side = "sell" if qty > 0 else "buy"
            qty_to_close = abs(qty)
            order_type = "take profit"
        else:
            continue  # no action

        try:
            api.submit_order(
                symbol=pos.symbol,
                qty=qty_to_close,
                side=side,
                type="market",
                time_in_force="day"
            )
            output_log.append(
                f"{order_type.capitalize()} triggered: Closed {qty_to_close} of {pos.symbol} at market price.\n"
            )
        except Exception as e:
            err_str = str(e).lower()
            if "no available bid" in err_str or "please reenter with a limit" in err_str:
                try:
                    quote_req = OptionLatestQuoteRequest(symbol_or_symbols=[pos.symbol])
                    quote = option_data_client.get_option_latest_quote(quote_req)
                    bid = None
                    if quote:
                        this_quote = quote.get(list(quote.keys())[0])
                        if isinstance(this_quote, dict):
                            bid = this_quote.get("bid_price")
                        else:
                            bid = getattr(this_quote, "bid_price", None)
                    if bid and bid > 0:
                        api.submit_order(
                            symbol=pos.symbol,
                            qty=qty_to_close,
                            side=side,
                            type="limit",
                            limit_price=bid,
                            time_in_force="day"
                        )
                        output_log.append(
                            f"{order_type.capitalize()} triggered: No market, so placed limit close at bid ${bid if bid is not None else 'None'} for {qty_to_close} of {pos.symbol}.\n"
                        )
                    else:
                        output_log.append(
                            f"Failed to close {pos.symbol}: no current bid available for limit order.\n"
                        )
                except Exception as ex2:
                    output_log.append(f"Failed limit close for {pos.symbol}: {ex2}\n")
            else:
                output_log.append(f"Failed to close position for {pos.symbol}: {e}\n")










import streamlit as st
import time
import re  # Ensure this is in your imports for scan_and_trade_etf_stocks
from datetime import datetime, timedelta
import pandas as pd  # Ensure for scan_and_trade_etf_stocks
import alpaca_trade_api as tradeapi  # Ensure for scan_and_trade_etf_stocks
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, OrderType, TimeInForce, ContractType, AssetStatus, ExerciseStyle
from alpaca.trading.requests import MarketOrderRequest, GetOptionContractsRequest
from alpaca.data.requests import OptionLatestQuoteRequest
from alpaca.data.historical.option import OptionHistoricalDataClient
from alpaca.data.timeframe import TimeFrame
from alpaca.data.historical.stock import StockHistoricalDataClient, StockBarsRequest

# Constants
import streamlit as st
import time

LOOPDELAY = st.session_state.get('loopbreakkey', 30)  # Default 30 seconds















def run_trading_loop(tickers, selected_indicators, category="ETFs", loop_delay=60):
    st.session_state.run_trading_loop = True
    output_container = st.empty()
    countdown_container = st.empty()
    
    # Initialize bias to Bullish or from session state
    if "bias_market" not in st.session_state:
        st.session_state.bias_market = "Bullish"
    
    while st.session_state.run_trading_loop:
        # Alternate bias every loop
        current_bias = st.session_state.bias_market
        st.session_state.bias_market = "Bearish" if current_bias == "Bullish" else "Bullish"
        
        # You may want to pass bias explicitly or rely on session state inside scan_and_trade_etf_stocks
        trade_log = scan_and_trade_etf_stocks(
            tickers=tickers,
            selected_indicators=selected_indicators
        )
        
        # Show logs
        # Append to main universal output log session variable
        if "two_tab_universal_output_log" not in st.session_state:
            st.session_state["two_tab_universal_output_log"] = ""
        st.session_state["two_tab_universal_output_log"] += trade_log + "\n"
        # Display the combined main output log
        output_container.text_area("Output Log", value=st.session_state["two_tab_universal_output_log"], height=400)

        countdown_container.write(f"Next scan in {loop_delay} seconds... (Current Market Bias: {current_bias})")
        
        # Countdown timer with UI update every second, checking for stop signal
        for remaining in range(loop_delay, 0, -1):
            if not st.session_state.run_trading_loop:
                break
            countdown_container.write(f"Next scan in {remaining} seconds... (Current Market Bias: {current_bias})")
            time.sleep(1)
        
    st.success("Trading loop stopped.")
















import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo




# --- Standard Library ---
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import time
import threading
import random
import re

# --- Third-Party Libraries ---
import pandas as pd
import numpy as np
import talib
import alpaca_trade_api as tradeapi
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent

# --- Alpaca Trading API ---
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import (
    AssetStatus,
    ExerciseStyle,
    OrderSide,
    OrderType,
    TimeInForce,
    ContractType,
)
from alpaca.trading.requests import (
    GetOptionContractsRequest,
    MarketOrderRequest,
)

# --- Alpaca Market Data: Historical & Live ---
from alpaca.data.timeframe import TimeFrame
from alpaca.data.historical.stock import (
    StockHistoricalDataClient,
    StockBarsRequest,
)
from alpaca.data.historical.option import OptionHistoricalDataClient
from alpaca.data.requests import OptionLatestQuoteRequest


# Trading-related (orders, contracts)
from alpaca.trading.requests import GetOptionContractsRequest, MarketOrderRequest

# Market data (quotes)
from alpaca.data.requests import OptionLatestQuoteRequest


import requests


# -----------------------------
# CODE FOR BUYING ASSETS
# -----------------------------


import pandas as pd
from datetime import datetime, timedelta
from datetime import datetime, timedelta
import streamlit as st

from alpaca.trading.client import TradingClient
from alpaca.data.historical.option import OptionHistoricalDataClient
from alpaca.trading.requests import MarketOrderRequest, GetOptionContractsRequest
from alpaca.trading.enums import OrderSide, OrderType, TimeInForce, AssetStatus, ContractType, ExerciseStyle
import pandas as pd
import re
import uuid


def scan_and_trade_etf_stocks(tickers, selected_indicators=None, trading_log_container=None):

    if selected_indicators is None:
        selected_indicators = []
    
    bullish_indicators = [ind for ind in selected_indicators if "Bullish" in ind]
    bearish_indicators = [ind for ind in selected_indicators if "Bearish" in ind]




    # Initialize log
    log = f"=== Trading Scan Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n"

    # Unique identifier for this run to avoid key collisions
    run_id = str(uuid.uuid4())[:8]

    # Initialize session state log if not present
    if 'two_tab_trading_log' not in st.session_state:
        st.session_state.two_tab_trading_log = ""
    
    # Update log
    st.session_state.two_tab_trading_log += log
    if trading_log_container:
        trading_log_container.text_area(
            "",
            st.session_state.get("two_tab_trading_log", ""),
            height=200,
            disabled=True,
            label_visibility="collapsed",
            placeholder="No trading activity to display.",
            key=f"trade_log_output_dynamic_{tickers[0] if tickers else 'scan'}_{run_id}"
        )


    # Initialize Alpaca API clients (fixed version)
    # Safely get keys (they should now exist in session_state after initial connection)
    api_key = st.session_state.get("api_key")
    api_secret = st.session_state.get("api_secret")
    mode = st.session_state.get("alpaca_mode", "paper")

    if not api_key or not api_secret:
        log = "API keys not available in session state. Cannot initialize trading clients or place options orders.\n\n"
        st.session_state.two_tab_trading_log += log
        if trading_log_container:
            trading_log_container.text_area(
                "",
                st.session_state.get("two_tab_trading_log", ""),
                height=200,
                disabled=True,
                label_visibility="collapsed",
                placeholder="No trading activity to display.",
                key=f"trade_log_output_dynamic_keys_missing_{run_id}"
            )
        return log

    # Use the old authenticated api object from session state (for equity/stock calls)
    api = st.session_state.api  # This is already connected and working

    # Create new SDK clients with guaranteed valid keys
    from alpaca.trading.client import TradingClient
    from alpaca.data.historical.option import OptionHistoricalDataClient

    try:
        trade_client = TradingClient(
            api_key,
            api_secret,
            paper=(mode == "paper")
        )
        option_data_client = OptionHistoricalDataClient(
            api_key,
            api_secret
        )
    except Exception as e:
        log = f"API client initialization failed (new SDK): {e}\n\n"
        st.session_state.two_tab_trading_log += log
        if trading_log_container:
            trading_log_container.text_area(
                "",
                st.session_state.get("two_tab_trading_log", ""),
                height=200,
                disabled=True,
                label_visibility="collapsed",
                placeholder="No trading activity to display.",
                key=f"trade_log_output_dynamic_init_fail_{run_id}"
            )
        return log

    # --- Check market status ---
    if not is_market_open():
        log = "\nMarket Closed: No Trading\n\n"
        st.session_state.two_tab_trading_log += log
        if trading_log_container:
            trading_log_container.text_area(
                "",
                st.session_state.get("two_tab_trading_log", ""),
                height=200,
                disabled=True,
                label_visibility="collapsed",
                placeholder="No trading activity to display.",
                key=f"trade_log_output_dynamic_market_closed_{run_id}"
            )
        return log

    # --- Stop loss logic ---
    # --- Stop loss logic ---
    # --- Stop loss logic (improved: fully isolated, never blocks trading) ---
    stop_loss_pct = st.session_state.settings.get("ETF_stop_loss", 5)
    stop_loss_log = "\n--- Stop-Loss/Take-Profit Check Started ---\n"

    # Safety: rebuild API if missing (already in your code)
    if api is None:
        try:
            import alpaca_trade_api as tradeapi
            api = tradeapi.REST(
                st.session_state.get("api_key"),
                st.session_state.get("api_secret"),
                base_url=st.session_state.get("alpaca_base_url", "https://paper-api.alpaca.markets")
            )

        except Exception as rebuild_error:
            stop_loss_log += f"Stop-loss aborted — failed to restore API client: {rebuild_error}\n"
            st.session_state.two_tab_trading_log += stop_loss_log
            if trading_log_container:
                trading_log_container.text_area(
                    "", st.session_state.get("two_tab_trading_log", ""), height=200, disabled=True,
                    label_visibility="collapsed", placeholder="No trading activity to display.",
                    key=f"trade_log_sl_restore_fail_{run_id}"
                )
            # Continue anyway — stop-loss failure shouldn't block new trades
        pass
            
    # Run stop-loss check if api exists (after possible restore)
    if api:
        try:
            positions = api.list_positions()
            sl_triggered_count = 0
            for pos in positions:
                try:
                    qty = int(pos.qty)
                    avg_price = float(pos.avg_entry_price)
                    current_price = float(getattr(pos, "current_price", getattr(pos, "market_price", 0)))
                    if qty == 0 or avg_price == 0 or current_price <= 0:
                        continue
                    # Calculate % loss (positive = loss)
                    if qty > 0:  # Long
                        loss_percent = (avg_price - current_price) / avg_price * 100
                    else:  # Short
                        loss_percent = (current_price - avg_price) / avg_price * 100
                    if loss_percent >= stop_loss_pct:
                        side = "sell" if qty > 0 else "buy"
                        qty_to_close = abs(qty)
                        try:
                            api.submit_order(
                                symbol=pos.symbol,
                                qty=qty_to_close,
                                side=side,
                                type="market",
                                time_in_force="day"
                            )
                            stop_loss_log += f"Stop-loss triggered: Closed {qty_to_close} {pos.symbol} at market (~${current_price:.2f})\n"
                            sl_triggered_count += 1
                        except Exception as e:
                            err_str = str(e).lower()
                            if "not eligible" in err_str or "uncovered" in err_str or "option" in err_str:
                                stop_loss_log += f"Cannot close {pos.symbol}: Account not approved for this option trade (likely naked/uncovered). Skipping.\n"
                            elif "no available bid" in err_str or "limit" in err_str:
                                try:
                                    quote_req = OptionLatestQuoteRequest(symbol_or_symbols=[pos.symbol])
                                    quote = option_data_client.get_option_latest_quote(quote_req)
                                    bid = None
                                    if quote:
                                        q = quote.get(list(quote.keys())[0])
                                        bid = q.bid_price if hasattr(q, 'bid_price') else (q.get('bid_price') if isinstance(q, dict) else None)
                                    if bid and bid > 0:
                                        api.submit_order(
                                            symbol=pos.symbol, qty=qty_to_close, side=side,
                                            type="limit", limit_price=bid, time_in_force="day"
                                        )
                                        stop_loss_log += f"Stop-loss: Market failed, placed limit order at bid ${bid:.2f} for {pos.symbol}\n"
                                    else:
                                        stop_loss_log += f"Stop-loss failed for {pos.symbol}: No bid liquidity for limit order.\n"
                                except Exception as ex2:
                                    stop_loss_log += f"Stop-loss limit fallback failed for {pos.symbol}: {ex2}\n"
                            else:
                                stop_loss_log += f"Failed to close {pos.symbol} on stop-loss: {e}\n"
                except Exception as per_pos_err:
                    stop_loss_log += f"Error processing position {getattr(pos, 'symbol', 'unknown')}: {per_pos_err}\n"
            stop_loss_log += f"--- Stop-Loss Check Completed: {sl_triggered_count} position(s) acted on ---\n"
        except Exception as critical_err:
            stop_loss_log += f"CRITICAL: Stop-loss check failed entirely: {critical_err}\n"
            stop_loss_log += "Continuing to new trade scanning anyway — risk management isolated.\n"

    # ALWAYS append stop-loss log and update UI (moved OUTSIDE if/else)
    st.session_state.two_tab_trading_log += stop_loss_log
    if trading_log_container:
        trading_log_container.text_area(
            "", st.session_state.get("two_tab_trading_log", ""), height=200, disabled=True,
            label_visibility="collapsed", placeholder="No trading activity to display.",
            key=f"trade_log_sl_complete_{run_id}"
        )


    # --- Minimum/Max position size ---
    # --- Minimum/Max position size ---
    min_size_val = float(st.session_state.settings.get("ETF_min_size", 1.0))  # Default to 1% if missing
    if min_size_val <= 0:
        log = "Warning: Invalid Min Position Size (<= 0). Using fallback value of 1%.\n\n"
        st.session_state.two_tab_trading_log += log
        if trading_log_container:
            trading_log_container.text_area(
                "", st.session_state.get("two_tab_trading_log", ""), height=200, disabled=True,
                label_visibility="collapsed", placeholder="No trading activity to display.",
                key=f"trade_log_output_dynamic_invalid_size_{run_id}"
            )
        min_size_val = 1.0  # Fallback to safe value
    # DO NOT return — continue trading

    # --- Indicator mapping and ticker processing ---


    def process_tickers(tickers, bullish_indicators, bearish_indicators, log, api, trade_client, option_data_client, trading_log_container):
        indicator_columns_map = {
            "EMA Bullish": "EMA_Bullish", "EMA Bearish": "EMA_Bearish",
            "TEMA Bullish": "TEMA_Bullish", "TEMA Bearish": "TEMA_Bearish",
            "Hull MA Bullish": "HMA_Bullish", "Hull MA Bearish": "HMA_Bearish",
            "SMA Bullish": "SMA_Bullish", "SMA Bearish": "SMA_Bearish",
            "MACD Bullish": "MACD_Bullish", "MACD Bearish": "MACD_Bearish",
            "RSI Bullish": "RSI_Bullish", "RSI Bearish": "RSI_Bearish",
            "Stochastic Bullish": "StochRSI_Bullish", "Stochastic Bearish": "StochRSI_Bearish",
            "ROC Bullish": "ROC_Bullish", "ROC Bearish": "ROC_Bearish",
            "Williams %R Bullish": "WilliamsR_Bullish", "Williams %R Bearish": "Williams_%R_Bearish",
            "Z-Score Bullish": "ZScore_Bullish", "Z-Score Bearish": "ZScore_Bearish",
            "ATR Bullish": "ATR_Bullish", "ATR Bearish": "ATR_Bearish",
            "Bollinger Bands Bullish": "BB_Bullish", "Bollinger Bands Bearish": "BB_Bearish",
            "Donchian Channels Bullish": "Donchian_Bullish", "Donchian Channels Bearish": "Donchian_Bearish",
            "Keltner Channels Bullish": "Keltner_Bullish", "Keltner Channels Bearish": "Keltner_Bearish",
            "Pivot Points Bullish": "Pivot_Bullish", "Pivot Points Bearish": "Pivot_Bearish",
            "Fibonacci Retracement Bullish": "Fibonacci_Bullish", "Fibonacci Retracement Bearish": "Fibonacci_Bearish",
            "OBV Bullish": "OBV_Bullish", "OBV Bearish": "OBV_Bearish",
            "CMF Bullish": "CMF_Bullish", "CMF Bearish": "CMF_Bearish",
            "Accumulation/Distribution Bullish": "AD_Bullish", "Accumulation/Distribution Bearish": "AD_Bearish",
            "High Volume Bullish": "HighVolume_Bullish", "High Volume Bearish": "HighVolume_Bearish",
            "Elder Force Index Bullish": "EFI_Bullish", "Elder Force Index Bearish": "EFI_Bearish",
            "BOS Bullish": "BOS_Bullish", "Liquidity Sweep Bullish": "Liquidity_Sweep_Bullish",
            "Order Block Bullish": "OrderBlock_Bullish", "FVG Bullish": "FVG_Bullish",
            "Discount Bullish": "Discount_Bullish", "BOS Bearish": "BOS_Bearish",
            "Liquidity Sweep Bearish": "Liquidity_Sweep_Bearish", "Order Block Bearish": "OrderBlock_Bearish",
            "FVG Bearish": "FVG_Bearish", "Discount Bearish": "Discount_Bearish",
        }

                # Fetch portfolio value once outside the loop
        ticker_log = ""  # Reset at start of processing

        # Fetch portfolio value once outside the loop
        try:
            if st.session_state.api:
                account = st.session_state.api.get_account()
            else:
                import alpaca_trade_api as tradeapi
                base_url = "https://paper-api.alpaca.markets" if mode == "paper" else "https://api.alpaca.markets"
                api_temp = tradeapi.REST(st.session_state.api_key, st.session_state.api_secret, base_url=base_url)
                account = api_temp.get_account()
            portfolio_value = float(account.portfolio_value)
            cash = float(account.cash)
            if portfolio_value <= 0:
                portfolio_value = float(account.equity or account.cash or 10000)
            max_invest_pct = st.session_state.get("max_portfolio_invested_pct", 100) / 100.0
            max_allowed_invested = portfolio_value * max_invest_pct
            current_invested = portfolio_value - cash
            remaining_global_allocation = max(0, max_allowed_invested - current_invested)
            ticker_log += f"Portfolio: ${portfolio_value:,.0f} | Cash: ${cash:,.0f} | Invested: {current_invested/portfolio_value*100:.1f}%\n"
            ticker_log += f"Max allowed invested: {max_invest_pct*100:.0f}% → Remaining allocation: ${remaining_global_allocation:,.0f}\n\n"
        except Exception as e:
            ticker_log += f"Failed to fetch portfolio value: {e}. Using fallback values.\n"


        for idx, symbol in enumerate(tickers):
            ticker_log = ""  # Added to reset per-ticker log
            try:
                # --- Fetch data ---
                df = fetch_data(symbol, datetime.now() - timedelta(days=130), datetime.now())
                if isinstance(df.index, pd.MultiIndex):
                    df.index = df.index.get_level_values(1)
                df.index = pd.to_datetime(df.index)
                if df.empty or len(df) < 50:
                    ticker_log += f"{symbol}\nInsufficient data (rows={len(df)}).\n\n"
                    continue

                price = float(df.iloc[-1]['close']) if 'close' in df.columns and not df.empty else 0.0
                if price <= 0:
                    ticker_log += f"{symbol}\nInvalid/missing price data.\n\n"
                    continue

                # --- Position info (per-symbol) ---
                try:
                    pos = api.get_position(symbol)
                    current_position_value = float(pos.market_value)
                except Exception:
                    current_position_value = 0.0

                min_size_pct = st.session_state.settings.get("ETF_min_size", 1)
                max_size_pct = st.session_state.settings.get("ETF_max_size", 5)
                max_position_value = portfolio_value * (max_size_pct / 100)

                # --- Calculate indicators ---
                df_bullish = calculate_selected_indicators_bullish(df.copy(), bullish_indicators, timeframe='1d')
                df_bearish = calculate_selected_indicators_bearish(df.copy(), bearish_indicators, timeframe='1d')

                # Count and list triggered indicators
                signal_hits = 0
                triggered_indicators = []
                for ind in bullish_indicators:
                    col_name = indicator_columns_map.get(ind)
                    if col_name and col_name in df_bullish.columns and bool(df_bullish.iloc[-1][col_name]):
                        signal_hits += 1
                        triggered_indicators.append(ind)
                for ind in bearish_indicators:
                    col_name = indicator_columns_map.get(ind)
                    if col_name and col_name in df_bearish.columns and bool(df_bearish.iloc[-1][col_name]):
                        signal_hits += 1
                        triggered_indicators.append(ind)

                # Check if there are enough signals to proceed
                buy_min_indicators = st.session_state.get("buy_min_indicators", 1)
                if signal_hits < buy_min_indicators:
                    ticker_log += f"{symbol}\n{signal_hits}/{len(bullish_indicators)} indicators triggered\n\n"
                    continue

                # Check if already at max allocation
                target_value = min(portfolio_value * (max_size_pct / 100), max_position_value)
                remaining_allocation = max(0, target_value - current_position_value)

                if remaining_allocation <= 0:
                    ticker_log += f"{symbol}\nAlready at or above max allocation (${current_position_value:.2f}/${max_position_value:.2f}), skipping.\n\n"
                    continue

                # --- Bearish Logic ---
                if st.session_state.get("bias_market") == "Bearish":
                    bear_signal_hits = 0
                    bear_triggered_indicators = []
                    for ind in bearish_indicators:
                        col_name = indicator_columns_map.get(ind)
                        if col_name and col_name in df_bearish.columns and bool(df_bearish.iloc[-1][col_name]):
                            bear_signal_hits += 1
                            bear_triggered_indicators.append(ind)

                    if bear_signal_hits < buy_min_indicators:
                        ticker_log += f"{symbol}\n{bear_signal_hits}/{len(bearish_indicators)} Bearish indicators\n\n"
                        continue

                    ticker_log += f"Detected {bear_signal_hits}/{len(bearish_indicators)} bearish indicators"
                    if bear_triggered_indicators:
                        ticker_log += f" ({', '.join(bear_triggered_indicators)})"
                    ticker_log += "\n"
                    ticker_log += "Bearish signals meet threshold, proceeding with trade evaluation.\n"

                    fraction = (bear_signal_hits - buy_min_indicators) / max(1, len(bearish_indicators) - buy_min_indicators)
                    fraction = max(0, min(1, fraction))
                    position_size_bear = min_size_pct + fraction * (max_size_pct - min_size_pct)
                    target_value_bear = min(portfolio_value * (position_size_bear / 100), max_position_value)
                    remaining_allocation_bear = max(0, target_value_bear - current_position_value)

                    if remaining_allocation_bear <= 0:
                        ticker_log += f"Already at or above bearish max allocation (${target_value_bear:.2f}), skipping trade.\n\n"
                        continue

                    if st.session_state.get("etf_options_mode", False):
                        try:
                            today = datetime.now().date()
                            exp_earliest = today + timedelta(days=st.session_state.get("exp_from", 7))
                            exp_latest = today + timedelta(days=st.session_state.get("exp_to", 14))

                            req = GetOptionContractsRequest(
                                underlying_symbols=[symbol],
                                status=AssetStatus.ACTIVE,
                                expiration_date_gte=exp_earliest,
                                expiration_date_lte=exp_latest,
                                type=ContractType.PUT,
                                style=ExerciseStyle.AMERICAN,
                                limit=100,
                            )
                            res = trade_client.get_option_contracts(req)
                            contracts = res.option_contracts
                            if not contracts:
                                ticker_log += f"{symbol}\nNo Put contracts found in expiration window ({exp_earliest} to {exp_latest}). Check if {symbol} has an active option chain or adjust expiration window.\n\n"
                                continue

                            raw_symbol = re.match(r"^[A-Za-z]+", symbol)
                            underlying_symbol = raw_symbol.group(0) if raw_symbol else symbol
                            try:
                                trade = api.get_latest_trade(underlying_symbol)
                                if trade is None:
                                    raise ValueError("No latest trade data returned")
                                underlying_price = float(trade.price)
                            except Exception as e:
                                ticker_log += f"Failed to fetch underlying price for {underlying_symbol}: {e}\n\n"
                                continue
                            if not contracts:
                                ticker_log += f"No Put contracts found for {symbol}.\n\n"
                                continue
                            best_put_contract = min(contracts, key=lambda c: abs(c.strike_price - underlying_price))

                            if not hasattr(best_put_contract, 'symbol') or not best_put_contract.symbol:
                                ticker_log += f"Invalid Put contract selected for {symbol}, skipping.\n\n"
                                continue

                            try:
                                quote_req = OptionLatestQuoteRequest(symbol_or_symbols=[best_put_contract.symbol])
                                option_quote = option_data_client.get_option_latest_quote(quote_req)
                                quote_data = option_quote.get(best_put_contract.symbol)
                                if not quote_data or quote_data.ask_price is None:
                                    ticker_log += (
                                        f"{symbol}\n"
                                        f"No valid quote or ask price for Put {best_put_contract.symbol}. "
                                        f"Possible low liquidity or inactive contract.\n\n"
                                    )
                                    continue

                                opt_price = float(quote_data.ask_price) if quote_data.ask_price and float(quote_data.ask_price) > 0 else None
                                if not opt_price:
                                    opt_price = float(quote_data.bid_price) if quote_data.bid_price and float(quote_data.bid_price) > 0 else None

                                if not opt_price or opt_price <= 0:
                                    ticker_log += (
                                        f"{symbol}\n"
                                        f"Unable to get valid price for Put {best_put_contract.symbol}. "
                                        f"Bid: {quote_data.bid_price if quote_data.bid_price is not None else 'None'}, "
                                        f"Ask: {quote_data.ask_price if quote_data.ask_price is not None else 'None'}. "
                                        f"Possible low liquidity or inactive contract.\n\n"
                                    )
                                    continue
                            except Exception as e:
                                ticker_log += (
                                    f"{symbol}\n"
                                    f"Error fetching option quote for Put {best_put_contract.symbol}: {e}. "
                                    f"Possible issue with API or market data access.\n\n"
                                )
                                continue

                            contracts_to_buy = int(remaining_allocation_bear // (opt_price * 100))

                            if contracts_to_buy <= 0 or (contracts_to_buy * opt_price * 100) < 100:
                                ticker_log += f"Bearish allocation too small for option trade (${contracts_to_buy * opt_price * 100:.2f}), skipping.\n\n"
                                continue

                            option_symbol = best_put_contract.symbol if hasattr(best_put_contract, 'symbol') else None
                            if not option_symbol:
                                ticker_log += f"Contract symbol missing for {symbol}, skipping option order\n\n"
                                continue

                            order = MarketOrderRequest(
                                symbol=option_symbol,
                                qty=contracts_to_buy,
                                side=OrderSide.BUY,
                                type=OrderType.MARKET,
                                time_in_force=TimeInForce.DAY,
                            )
                            trade_client.submit_order(order)

                            ticker_log += (
                                f"Placed bearish option order: {contracts_to_buy} Puts {best_put_contract.symbol}\n"
                                f"Price: ${opt_price:.2f}/contract\n"
                                f"Underlying price: ${underlying_price:.2f}\n"
                                f"Strike: ${best_put_contract.strike_price:.2f}\n"
                                f"Expiry: {best_put_contract.expiration_date}\n"
                                f"Total cost: ${(contracts_to_buy * opt_price * 100):.2f}\n\n"
                            )
                            continue

                        except Exception as e:
                            ticker_log += f"Bearish option order failed: {e}\n\n"
                            continue

                    else:
                        qty_shrt = int(remaining_allocation_bear // price)
                        if qty_shrt <= 0:
                            ticker_log += f"Bearish allocation too small for short shares (${remaining_allocation_bear:.2f}), skipping.\n\n"
                            continue

                        short_side = "sell"
                        try:
                            api.submit_order(
                                symbol=symbol,
                                qty=qty_shrt,
                                side=short_side,
                                type="market",
                                time_in_force="day"
                            )
                            ticker_log += (
                                f"Placed bearish short sell order: {qty_shrt} shares\n"
                                f"Price: ${price:.2f}/share\n"
                                f"Total value: ${(qty_shrt * price):.2f}\n\n"
                            )
                            continue

                        except Exception as e:
                            ticker_log += f"Bearish short order failed: {e}\n\n"
                            continue

                # --- Bullish/Neutral Logic ---
                if st.session_state.get("etf_options_mode", False):
                    try:
                        today = datetime.now().date()
                        exp_earliest = today + timedelta(days=st.session_state.get("exp_from", 7))
                        exp_latest = today + timedelta(days=st.session_state.get("exp_to", 14))

                        market_bias = st.session_state.get("bias_market", "Neutral")


                        def get_effective_bias():
                            actual_bias = st.session_state.get("bias_market", "Neutral")
                            if st.session_state['bias_only']:
                                if actual_bias == "Neutral":
                                    return None
                                return actual_bias
                            elif st.session_state['bullish_only']:
                                return "Bullish"
                            elif st.session_state['bearish_only']:
                                return "Bearish"
                            return actual_bias


                        effective_bias = get_effective_bias()
                        if effective_bias is None:
                            ticker_log += f"{symbol}\nNo trade due to neutral bias in Bias Only mode.\n\n"
                            continue


                        if effective_bias == "Bullish":
                            contract_type = ContractType.CALL
                            option_trade_side = OrderSide.BUY
                        elif effective_bias == "Bearish":
                            contract_type = ContractType.PUT
                            option_trade_side = OrderSide.BUY
                        elif effective_bias == "Neutral":
                            contract_type = ContractType.CALL if st.session_state.get("fallback_bias", True) else ContractType.PUT
                            option_trade_side = OrderSide.BUY
                        else:
                            ticker_log += f"{symbol}\nUnknown bias, skipping.\n\n"
                            continue

                        req = GetOptionContractsRequest(
                            underlying_symbols=[symbol],
                            status=AssetStatus.ACTIVE,
                            expiration_date_gte=exp_earliest,
                            expiration_date_lte=exp_latest,
                            type=contract_type,
                            style=ExerciseStyle.AMERICAN,
                            limit=100
                        )
                        res = trade_client.get_option_contracts(req)
                        contracts = res.option_contracts
                        if not contracts:
                            ticker_log += f"{symbol}\nNo option contracts found in expiration window ({exp_earliest} to {exp_latest}). Check if {symbol} has an active option chain or adjust expiration window.\n\n"
                            continue

                        raw_symbol = re.match(r"^[A-Za-z]+", symbol)
                        underlying_symbol = raw_symbol.group(0) if raw_symbol else symbol
                        # Fallback: Use latest close from historical df (already fetched for indicators)
                        if 'close' in df.columns and not df.empty:
                            underlying_price = float(df.iloc[-1]['close'])
                            ticker_log += f"{symbol}\nUsing historical close price for underlying ${underlying_price:.2f} (real-time fetch skipped due to data subscription).\n"
                        else:
                            ticker_log += f"{symbol}\nNo historical close price available. Skipping option trade.\n\n"
                            continue
                        if not contracts:
                            ticker_log += f"{symbol}\nNo option contracts found for {symbol}.\n\n"
                            continue
                        best_contract = sorted(
                            contracts,
                            key=lambda c: (c.expiration_date, abs(c.strike_price - underlying_price))
                        )[0]

                        if not hasattr(best_contract, 'symbol') or not best_contract.symbol:
                            ticker_log += f"{symbol}\nInvalid option contract selected, skipping.\n\n"
                            continue

                        try:
                            quote_req = OptionLatestQuoteRequest(symbol_or_symbols=[best_contract.symbol])
                            option_quote = option_data_client.get_option_latest_quote(quote_req)
                            quote_data = option_quote.get(best_contract.symbol)
                            if not quote_data or quote_data.ask_price is None:
                                ticker_log += (
                                    f"{symbol}\n"
                                    f"No valid quote or ask price for {best_contract.symbol}. "
                                    f"Possible low liquidity or inactive contract.\n\n"
                                )
                                continue

                            option_price = float(quote_data.ask_price) if quote_data.ask_price and float(quote_data.ask_price) > 0 else None
                            if not option_price:
                                option_price = float(quote_data.bid_price) if quote_data.bid_price and float(quote_data.bid_price) > 0 else None

                            if not option_price or option_price <= 0:
                                ticker_log += (
                                    f"{symbol}\n"
                                    f"Unable to get valid price for {best_contract.symbol}. "
                                    f"Bid: {quote_data.bid_price if quote_data.bid_price is not None else 'None'}, "
                                    f"Ask: {quote_data.ask_price if quote_data.ask_price is not None else 'None'}. "
                                    f"Possible low liquidity or inactive contract.\n\n"
                                )
                                continue
                        except Exception as e:
                            ticker_log += (
                                f"{symbol}\n"
                                f"Error fetching option quote for {best_contract.symbol}: {e}. "
                                f"Possible issue with API or market data access.\n\n"
                            )
                            continue

                        max_allocation = min(remaining_allocation, max_position_value - current_position_value)
                        contracts_to_buy = int(max_allocation // (option_price * 100))

                        if contracts_to_buy < 1 or contracts_to_buy * option_price * 100 < 100:
                            ticker_log += (
                                f"{symbol}\n"
                                f"Allocation too small for a meaningful position\n"
                                f"Max allocation: ${max_allocation:.2f}\n"
                                f"Contract cost: ${option_price*100:.2f}\n\n"
                            )
                            continue

                        ticker_log += (
                            f"{symbol}\n"
                            f"Placing option order: {contracts_to_buy} {contract_type.value} contracts\n"
                            f"Symbol: {best_contract.symbol}\n"
                            f"Price: ${option_price:.2f}/contract\n"
                            f"Underlying price: ${underlying_price:.2f}\n"
                            f"Strike: ${best_contract.strike_price:.2f}\n"
                            f"Expiry: {best_contract.expiration_date}\n"
                            f"Total cost: ${(contracts_to_buy * option_price * 100):.2f}\n"
                            f"Side: {option_trade_side.value}\n"
                        )

                        order = MarketOrderRequest(
                            symbol=best_contract.symbol,
                            qty=contracts_to_buy,
                            side=option_trade_side,
                            type=OrderType.MARKET,
                            time_in_force=TimeInForce.DAY
                        )
                        trade_client.submit_order(order)
                        ticker_log += f"✅ Placed order\n\n"
                        continue

                    except Exception as e:
                        ticker_log += f"{symbol}\nOption trading failed: {e}\n\n"
                        continue

                else:
                    qty_equity = int(remaining_allocation // price) if price > 0 else 0
                    if qty_equity < 1:
                        ticker_log += f"{symbol}\nNot enough allocation for a full share (${remaining_allocation:.2f}).\n\n"
                        continue

                    bias = st.session_state.get("bias_market", "Neutral")
                    if bias == "Neutral":
                        side = 'buy' if st.session_state.get("fallback_bias", True) else 'sell'
                    elif bias == "Bullish":
                        side = 'buy'
                    elif bias == "Bearish":
                        side = 'sell'
                    else:
                        ticker_log += f"{symbol}\nUnknown bias for equity order, skipping.\n\n"
                        continue

                    ticker_log += (
                        f"{symbol}\n"
                        f"Placing equity order: {qty_equity} shares\n"
                        f"Price: ${price:.2f}/share\n"
                        f"Total value: ${(qty_equity * price):.2f}\n"
                        f"Side: {side}\n"
                    )

                    api.submit_order(
                        symbol=symbol,
                        qty=qty_equity,
                        side=side,
                        type='market',
                        time_in_force='day'
                    )
                    ticker_log += f"✅ Placed order\n\n"
                    continue

            except Exception as e:
                ticker_log += f"{symbol}\nError processing: {e}\n\n"

            finally:
                if ticker_log:
                    st.session_state.two_tab_trading_log += ticker_log
                    if trading_log_container:
                        trading_log_container.text_area(
                            "",
                            st.session_state.get("two_tab_trading_log", ""),
                            height=200,
                            disabled=True,
                            label_visibility="collapsed",
                            placeholder="No trading activity to display.",
                            key=f"trade_log_output_dynamic_{symbol}_{run_id}_{idx}"
                        )

        return log



    # Execute ticker processing
    log = process_tickers(tickers, bullish_indicators, bearish_indicators, log, api, trade_client, option_data_client, trading_log_container)
    

    # Finalize log
    st.session_state.two_tab_trading_log += f"=== Trading Loop Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ==="

    if trading_log_container:
        trading_log_container.text_area(
            "",
            st.session_state.get("two_tab_trading_log", ""),
            height=200,
            disabled=True,
            label_visibility="collapsed",
            placeholder="No trading activity to display.",
            key=f"trade_log_output_dynamic_final_{run_id}"
        )

    try:
        with open("TRADE_LOG.txt", "a") as f:
            f.write(st.session_state.two_tab_trading_log[-500:])  # or full log if needed
    except Exception as file_error:
        print(f"Error writing to TRADE_LOG.txt: {file_error}")

    return None  # or just remove the return



def is_market_open():
    try:
        api, _, _ = connect_alpaca(
            st.session_state.api_key,
            st.session_state.api_secret
        )
        clock = api.get_clock()
        return {
            "is_open": clock.is_open,
            "next_open": clock.next_open,    # datetime object
            "next_close": clock.next_close,  # datetime object
            "timestamp": clock.timestamp     # current market time
        }
    except Exception as e:
        print(f"Error checking market clock: {e}")
        return {"is_open": False}























































































































































import streamlit as st

# Initialize session state
if "settings" not in st.session_state:
    st.session_state.settings = {
        "theme": "Light",
        "font_size": 14,
        "secondary_color": "#000000"
    }

# Initialize width_selection with query parameter or default
categories = ["Tight", "Moderate", "Wide"]
if "width_selection" not in st.session_state:
    val = st.query_params.get("width_selection", categories[0])  # Default to Tight
    st.session_state.width_selection = val if val in categories else categories[0]

# Constants
PRIMARY_COLOR = "#F5BF03"
LINE_COLOR = "#000000"
width_map = {
    "Tight": "700px",
    "Moderate": "1000px",
    "Wide": "1200px"
}

# Set page config (must be first Streamlit call)
st.set_page_config(layout="centered")

# Function to update query parameters
def update_query_params(value):
    if value in width_map:
        st.session_state.width_selection = value
        st.query_params["width_selection"] = value

# Settings Tab (assuming tabs is defined; using container as placeholder)
with tabs[-1]:  # Replace with tabs[-1] in your actual app
    # Set active tab
    st.session_state.active_tab = "Legal"

    # Margin for spacing
    st.markdown("""<div style="margin-top: 10px;"></div>""", unsafe_allow_html=True)

    # Title
    st.markdown(
        """
        <div style="display: flex; justify-content: center; width: 100%; margin-top: 10px; margin-bottom: -30px;">
            <h1 class="gold-title" style="font-size: 36px; text-align: center;">
                <span class="front" data-text="Legal">Legal</span>
                <span class="shadow">Legal</span>
            </h1>
        </div>
        """,
        unsafe_allow_html=True
    )




    col1, col2, col3 = st.columns([0.2, 1, 0.2])


    with col2:
        @st.dialog("Terms of Service", width="large")
        def terms_dialog():
            st.markdown("""
            ### Terms of Service
            Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor 
            incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis 
            nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
            """)
            if st.button("Close", key="terms_close"):
                st.rerun()


        @st.dialog("Privacy Policy", width="large")
        def privacy_dialog():
            st.markdown("""
            ### Privacy Policy
            Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore 
            eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt 
            in culpa qui officia deserunt mollit anim id est laborum.
            """)
            if st.button("Close", key="privacy_close"):
                st.rerun()


        @st.dialog("Cookie Policy", width="large")
        def cookie_dialog():
            st.markdown("""
            ### Cookie Policy
            We love to eat cookies
            """)
            if st.button("Close", key="cookie_close"):
                st.rerun()


        @st.dialog("Risk Disclosure Statement", width="large")
        def risk_dialog():
            st.markdown("""
            ### Risk Disclosure Statement
            Dummy Text.
            """)
            if st.button("Close", key="risk_close"):
                st.rerun()


        @st.dialog("Financial Adviser Disclaimer", width="large")
        def advice_dialog():
            st.markdown("""
            ### Financial Adviser Disclaimer
            Not Financial Advice.
            """)
            if st.button("Close", key="advice_close"):
                st.rerun()


        @st.dialog("End-User License Agreement", width="large")
        def eula_dialog():
            st.markdown("""
            ### End-User License Agreement
            Dummy Text
            """)
            if st.button("Close", key="eula_close"):
                st.rerun()


    

        import streamlit as st





        col1, col2, col3 = st.columns([0.1, 0.1, 0.1])
        with col2:
            st.markdown("---")

        st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)


        with st.form(key="dialogue_form"):
            # Row 1: Three columns
            col1_row1, col2_row1, col3_row1 = st.columns([1, 1, 1])
            with col1_row1:
                if st.form_submit_button("Terms of Service", use_container_width=True):
                    terms_dialog()
            with col2_row1:
                if st.form_submit_button("Privacy Policy", use_container_width=True):
                    privacy_dialog()
            with col3_row1:
                if st.form_submit_button("Cookie Policy", use_container_width=True):
                    cookie_dialog()
            
            st.markdown('<div style="height:15px;"></div>', unsafe_allow_html=True)
            
            # Row 2: Three columns
            col1_row2, col2_row2, col3_row2 = st.columns([1, 1, 1])
            with col1_row2:
                if st.form_submit_button("Risk Statement", use_container_width=True):
                    risk_dialog()
            with col2_row2:
                if st.form_submit_button("Adviser Disclaimer", use_container_width=True):
                    advice_dialog()
            with col3_row2:
                if st.form_submit_button("EULA", use_container_width=True):
                    eula_dialog()




    # Get the width *before* slider (will update on rerun)
    selected_width = width_map.get(st.session_state.width_selection, "1000px")

    # Inject CSS before columns
    st.markdown(
        f"""
        <style>
        /* Main container styling */


        /* Yellow gradient background box (bottom layer) */
        .yellow-bg-box {{
            position: absolute;
            top: 50%;
            left: 50%;
            width: 60%;
            height: 150px;
            background: linear-gradient(120deg, #3a3a3a 15%, #575757 50%, #7a7a7a 85%, #3a3a3a 100%);
            border: 6px solid rgb(26, 27, 28);
            border-radius: 20px;
            pointer-events: none;
            user-select: none;
            z-index: 1;
            transform: translate(-50%, 0%);
        }}

        /* Black background box (second layer) */
        .black-bg-box {{
            position: absolute;
            top: 50%;
            left: 50%;
            width: 56%;
            height: 100px;
            background-color: rgb(42, 42, 42);
            border: 4px solid rgb(26, 27, 28);
            border-radius: 20px;
            pointer-events: none;
            user-select: none;
            z-index: 2;
            transform: translate(-50%, 5%);
        }}


        


        /* Blue background box (top layer) */
        .second-bg-box {{
            position: absolute;
            top: 50%;
            left: 50%;
            width: 20%;
            height: 150px;

            border-radius: 20px;
            pointer-events: none;
            user-select: none;
            z-index: 4;
            transform: translate(-130%, -22%);
        }}



        /* Style for image inside blue box */
        .second-bg-box img {{
            width: 100%; /* Adjust to fit within box */
            max-height: 120px; /* Limit height to fit */
            object-fit: contain;
            margin-top: 6px; /* Added to move text up slightly */
            margin-bottom: 10px; /* Space between image and text */
        }}






        /* Ensure interactive UI elements are above background boxes */
        div[data-testid="stSlider"],
        div[data-testid="stColorPicker"] {{
            position: relative;
            z-index: 1000;
        }}

        /* Style color picker */
        div[data-testid="stColorPicker"] input[type="color"] {{
            width: 40px;
            height: 40px;
            border-radius: 6px;
            cursor: pointer;
        }}

        /* Ensure tooltips and popovers are on top */
        [data-testid="stTooltip"],
        [data-testid="stPopover"] {{
            z-index: 2000;
        }}

        /* Ensure column content is above background boxes */
        div[data-testid="column"] > div:nth-child(2) {{
            position: relative;
            z-index: 500;
        }}

        /* Ensure Chart Color label is at the forefront */
        .chart-color-label {{
            position: relative;
            z-index: 1000;
        }}

        .chart-color-container {{
            margin-top: 50px; /* Your adjusted value */
            z-index: 1000;
            display: flex;
            align-items: center;
            justify-content: center;
            width: fit-content;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )



    import base64
    img_base64 = base64.b64encode(open("logo.png", "rb").read()).decode()
    

    st.markdown('<div class="yellow-bg-box"></div>', unsafe_allow_html=True)
    st.markdown('<div class="black-bg-box"></div>', unsafe_allow_html=True)
    st.markdown('<div class="third-bg-box"></div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="second-bg-box" style="text-align: center;">
            <img src="data:image/png;base64,{img_base64}" />
            <h4 style="position: relative; top: -30px;">HalterAPI</h4>
        </div>
        """,
        unsafe_allow_html=True
    )







    # Layout columns
    col1, col12, col2, col23, col3 = st.columns([0.45, 0.05, 0.96, 0.05, 0.45])


    # ——————— PAGE WIDTH SLIDER — 3 OPTIONS, ACTUALLY WORKS ———————

    st.markdown("<div style='height:5px'></div>", unsafe_allow_html=True)

    with col2:
    


        
        chartcol1, chartcol2, chartcol3, chartcol4 = st.columns([5, 2, .2, 1])
        with chartcol2:
            st.markdown('<h3 class="chart-color-label" style="text-align: left; margin-top: -5px;">Chart Color</h3>', unsafe_allow_html=True)
        
        with chartcol4:


            chart_color = st.color_picker(
                label="Pick chart color",
                value=st.session_state.settings.get("secondary_color", "#00ff88"),
                key="chart_color",
                label_visibility="collapsed"
            )
            if chart_color != st.session_state.settings.get("secondary_color"):
                st.session_state.settings["secondary_color"] = chart_color
                save_settings(st.session_state.settings)
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)






st.markdown("<div style='height:50px'></div>", unsafe_allow_html=True)





















# Footer
st.markdown(
    """
    <hr style="border: 1px solid rgba(128, 128, 128, 0.3); margin-top: 0; margin-bottom: 5px;">
    <p style="font-size: 12px; color: rgba(128, 128, 128, 0.7); text-align: center; margin-top: 0;">
        Not financial advice. All risk is assumed by the user.
    </p>
    """,
    unsafe_allow_html=True
)

st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)











def render_custom_progress_bar(progress_pct, bar_color="#ffe899"):
    # Clamp 0-100
    progress_pct = min(max(progress_pct, 0), 100)
    bar_html = f"""
        <div style="width: 100%; height: 8px; background: #393939; border-radius: 4px; margin-top: 10px; margin-bottom: 0;">
          <div style="width: {progress_pct}%; height: 100%; background: {bar_color}; border-radius: 4px;"></div>
        </div>
    """
    st.markdown(bar_html, unsafe_allow_html=True)









with tabs[-2]:







    import streamlit as st
    import requests
    from bs4 import BeautifulSoup
    import re
    import json
    import os
    import time
    from datetime import datetime, timedelta
    import pandas as pd
    # Add any other imports you need for your Alpaca client, etc.





    # --- UTILS ---

    def render_custom_progress_bar(progress_pct, bar_color="#ffe899"):
        progress_pct = min(max(progress_pct, 0), 100)
        st.markdown(f'''
            <div style="width: 100%; height: 8px; background: #393939; border-radius: 4px; margin-top:10px; margin-bottom: 0;">
                <div style="width: {progress_pct}%; height: 100%; background: {bar_color}; border-radius: 4px;"></div>
            </div>
        ''', unsafe_allow_html=True)


    def get_stock_tickers_from_url(html_or_url, max_tickers=50):
        """Scrape stock tickers from HTML or URL."""
        if html_or_url.startswith("http"):
            try:
                r = requests.get(
                    html_or_url,
                    timeout=8,
                    headers={"User-Agent": "Mozilla/5.0 (compatible; ScraperApp/1.0)"}
                )
                r.raise_for_status()
                html = r.text
            except Exception:
                return []
        else:
            html = html_or_url

        soup = BeautifulSoup(html, "html.parser")
        tables = soup.find_all("table")

        ticker_regex = re.compile(r"^[A-Z]{1,5}(?:[\.-][A-Z0-9]{1,4})?(?:\.[A-Z]{1,4})?$")

        best_column = []
        for table in tables:
            rows = table.find_all("tr")
            if not rows:
                continue
            parsed_rows = []
            for row in rows:
                cells = row.find_all(["td", "th"])
                row_texts = []
                for cell in cells:
                    a = cell.find("a")
                    cell_text = a.text.strip() if a and a.text.strip() else cell.get_text(strip=True)
                    row_texts.append(cell_text)
                parsed_rows.append(row_texts)
            if not parsed_rows or len(parsed_rows[0]) < 1:
                continue
            maxlen = max(len(r) for r in parsed_rows)
            for r in parsed_rows:
                while len(r) < maxlen:
                    r.append('')
            columns = list(zip(*parsed_rows))
            for col in columns:
                matches = [cell for cell in col if ticker_regex.match(cell.upper())]
                if len(matches) > len(best_column):
                    best_column = matches

        if not best_column and soup:
            all_links = soup.find_all("a")
            link_texts = [a.get_text(strip=True) for a in all_links]
            link_matches = [t for t in link_texts if ticker_regex.match(t.upper())]
            if len(link_matches) > len(best_column):
                best_column = link_matches

        cleaned = []
        seen = set()
        for t in best_column:
            u = t.upper()
            if u not in seen and len(u) <= 14:
                seen.add(u)
                cleaned.append(u)
            if len(cleaned) >= max_tickers:
                break

        return cleaned


    def load_settings_from_file():
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f:
                    data = json.load(f)
                for key in data:
                    if key not in st.session_state:
                        st.session_state[key] = data[key]
            except Exception as e:
                st.error(f"Failed to load settings: {e}")


    def save_settings_to_file():
        to_save = {}
        keys_to_save = [
            "tab_list", "tab_select", "per_tab_data",
            "manual_tickers", "manual_disliked",
            "two_tab_selected_category",
            "manual_selected_category",
            
        ]
        for cat in ["Options", "ETFs", "Equity", "Crypto"]:
            keys_to_save.extend([
                f"two_tab_urls_input_{cat}",
                f"two_tab_disliked_url_{cat}",
                f"two_tab_max_tickers_{cat}",
                f"manual_tickers_{cat}",
            ])
        for key in keys_to_save:
            if key in st.session_state:
                to_save[key] = st.session_state[key]
        try:
            with open(SETTINGS_FILE, "w") as f:
                json.dump(to_save, f, indent=4)
        except Exception as e:
            st.error(f"Failed to save settings: {e}")


    import re
    import time
    import streamlit as st

    def parse_mixed_input(input_text):
        items = re.split(r'[\s,]+', input_text.strip())
        url_list = []
        manual_tickers = []
        ticker_pattern = re.compile(r'^[A-Z0-9\.\-]{1,14}$')  # Ticker format pattern (adjust if needed)

        for item in items:
            item = item.strip()
            if not item:
                continue
            if item.lower().startswith('http'):
                url_list.append(item)
            elif ticker_pattern.match(item.upper()):
                manual_tickers.append(item.upper())
            else:
                # Ignore or log unknown format entries
                pass
        return url_list, manual_tickers

    def run_scan(category, local_max_tickers, prog_bar_container=None, progress_start=0, total_progress=100):
        pdata = st.session_state.per_tab_data["Scraper"]
        cd = pdata["category_data"][category]
        cd["scraper_urls"] = st.session_state.get(f"two_tab_urls_input_{category}", "")
        cd["url_scraper_disliked"] = st.session_state.get(f"two_tab_disliked_url_{category}", "")
        cd["max_tickers"] = st.session_state.get(f"two_tab_max_tickers_{category}", 50)

        url_list, manual_tickers = parse_mixed_input(cd["scraper_urls"])
        disliked_set = {t.strip().upper() for t in cd["url_scraper_disliked"].split(",") if t.strip()}
        all_tickers = []
        log = f"=== Scanning {category} ===\n"

        num_urls = len(url_list)
        progress_pct = 0

        for i, url in enumerate(url_list):
            log += f"🌐 {url}\n"
            tickers = get_stock_tickers_from_url(url, local_max_tickers)
            if tickers:
                log += f"✔️ {len(tickers)} tickers found\n"
                all_tickers.extend(tickers)
            else:
                log += "❌ No tickers found or error\n"
            progress_pct = 100 * (i + 1) / max(num_urls, 1)

            if prog_bar_container:
                render_progress_bar(prog_bar_container, progress_start + progress_pct * total_progress / 100)

            time.sleep(0.2)

        if prog_bar_container:
            render_progress_bar(prog_bar_container, progress_start + total_progress)

        # Add manual tickers directly
        all_tickers.extend(manual_tickers)

        all_tickers_upper = [t.strip().upper() for t in all_tickers if t.strip()]
        total_retrieved = len(all_tickers_upper)

        seen = set()
        final_all_tickers = []
        for ticker in all_tickers_upper:
            if ticker not in seen:
                seen.add(ticker)
                final_all_tickers.append(ticker)
        duplicates_removed = total_retrieved - len(final_all_tickers)

        filtered_tickers = [t for t in final_all_tickers if t not in disliked_set]
        manually_removed = len(set(final_all_tickers) & disliked_set)

        cd["final_tickers"] = filtered_tickers


        log += (
            f"Total tickers retrieved: {total_retrieved}\n"
            + f"Duplicates removed: {duplicates_removed}\n"
            + f"Manually Removed: {manually_removed}\n"
            + f"Final tickers: {len(filtered_tickers)}\n\n"
        )

        return log, filtered_tickers


    def render_progress_bar(container, pct, color=PRIMARY_COLOR):
        pct = min(max(pct, 0), 100)
        bar_html = f"""
        <div style="width: 100%; height: 8px; background: #393939; border-radius: 4px; margin-top:10px; margin-bottom:0;">
            <div style="width: {pct}%; height: 100%; background: {color}; border-radius: 4px;"></div>
        </div>
        """
        container.markdown(bar_html, unsafe_allow_html=True)


    def render_progress_bar_container():
        if "prog_bar_container" not in st.session_state:
            st.session_state["prog_bar_container"] = st.empty()
        return st.session_state["prog_bar_container"]


    # --- INITIALIZE SESSION STATE ---
    core_tabs = ["Scraper"]

    if "tab_list" not in st.session_state:
        st.session_state.tab_list = core_tabs.copy()
    if "tab_select" not in st.session_state:
        st.session_state.tab_select = "Scraper"
    if "per_tab_data" not in st.session_state:
        st.session_state.per_tab_data = {}
    if "manual_tickers" not in st.session_state:
        st.session_state.manual_tickers = ""
    if "manual_disliked" not in st.session_state:
        st.session_state.manual_disliked = ""
    if "trade_running" not in st.session_state:
        st.session_state.trade_running = False
    if "trade_last_run" not in st.session_state:
        st.session_state.trade_last_run = None
    if "trade_log" not in st.session_state:
        st.session_state.trade_log = ""
    if "show_all_tickers" not in st.session_state:
        st.session_state.show_all_tickers = False

    load_settings_from_file()

    if "_force_select_tab" in st.session_state:
        forced_tab = st.session_state._force_select_tab
        del st.session_state._force_select_tab
        if forced_tab in st.session_state.tab_list:
            st.session_state.tab_select = forced_tab

    if st.session_state.tab_select not in st.session_state.tab_list:
        st.session_state.tab_select = st.session_state.tab_list[0]

    # --- MAIN TAB SELECTOR ---
    tab_list = st.session_state.tab_list

    st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)
    tabrow = st.columns([2, 0.1, 1])
    with tabrow[0]:
        st.markdown(
            '<h1 class="gold-title" style="font-size: 36px;">'
            '<span class="front" data-text="Data Center">Data Center</span>'
            '<span class="shadow">Data Center</span>'
            '</h1>',
            unsafe_allow_html=True
        )

    with tabrow[2]:

    
        selected_index = 0
        if st.session_state.tab_select in tab_list:
            selected_index = tab_list.index(st.session_state.tab_select)
        current_tab = st.selectbox(
            "",
            tab_list,
            index=selected_index,
            key="tab_selectbox",
            label_visibility="collapsed",
            placeholder="Type or select tab..."
        )
        if current_tab != st.session_state.tab_select:
            st.session_state.tab_select = current_tab
            st.rerun()

    for key in ["tab_add_notification", "tab_delete_confirm", "tab_deleted_notification", "tab_to_delete"]:
        if key not in st.session_state:
            st.session_state[key] = "" if key == "tab_to_delete" else False





    # --- SCRAPER TAB UI ---
    # Conditional initialization to avoid overwriting existing data
    if "Scraper" not in st.session_state.per_tab_data:
        st.session_state.per_tab_data["Scraper"] = {
            "final_tickers": [],
            "status_log": "",
            "scraper_urls": "",
            "url_scraper_disliked": "",
            "category_data": {
                "Options": {"scraper_urls": "", "url_scraper_disliked": "", "final_tickers": [], "max_tickers": 50},
                "ETFs": {"scraper_urls": "", "url_scraper_disliked": "", "final_tickers": [], "max_tickers": 50},
                "Equity": {"scraper_urls": "", "url_scraper_disliked": "", "final_tickers": [], "max_tickers": 50},
                "Crypto": {"scraper_urls": "", "url_scraper_disliked": "", "final_tickers": [], "max_tickers": 50}
            }
        }

    if "category_data" not in st.session_state.per_tab_data["Scraper"]:
        st.session_state.per_tab_data["Scraper"]["category_data"] = {
            "Options": {"scraper_urls": "", "url_scraper_disliked": "", "final_tickers": [], "max_tickers": 50},
            "ETFs": {"scraper_urls": "", "url_scraper_disliked": "", "final_tickers": [], "max_tickers": 50},
            "Equity": {"scraper_urls": "", "url_scraper_disliked": "", "final_tickers": [], "max_tickers": 50},
            "Crypto": {"scraper_urls": "", "url_scraper_disliked": "", "final_tickers": [], "max_tickers": 50}
        }

    # Safely add missing keys per category (no overwrite)
    for cat in ["Options", "ETFs", "Equity", "Crypto"]:
        cat_data = st.session_state.per_tab_data["Scraper"]["category_data"].setdefault(cat, {})
        cat_data.setdefault("scraper_urls", "")
        cat_data.setdefault("url_scraper_disliked", "")
        cat_data.setdefault("final_tickers", [])
        cat_data.setdefault("max_tickers", 50)

    if "show_all_tickers" not in st.session_state:
        st.session_state["show_all_tickers"] = False

    pdata = st.session_state.per_tab_data["Scraper"]
    categories = ["Options", "ETFs", "Equity", "Crypto"]
    selected_category = st.session_state["two_tab_selected_category"]

    left_col, spacer_col, right_col = st.columns([2, 0.1, 1])

    with left_col:
        word_col, dot_col = st.columns([3, 1])

        with word_col:
            st.markdown(
                '<p style="font-size:1.0rem; color:gray; margin-bottom:0;' \
                '">Some websites may not work if they require login or use JavaScript rendering.</p>',
                unsafe_allow_html=True,
            )

        with dot_col:
            PRIMARY_COLOR = "#F5BF03"
            UNSELECTED_COLOR = "grey"
            HOVER_COLOR = "#F5BF03"

            dots = ["•", "•", "•", "•"]
            tooltips = ["Options", "ETFs", "Equity", "Crypto"]
            categories = ["Options", "ETFs", "Equity", "Crypto"]

            # Initialize selected index
            if "dot" not in st.session_state:
                st.session_state.dot = int(st.query_params.get("dot", "0"))

            # Inject CSS for positioning and styling
            st.markdown(
                f"""
                <style>
                /* Make the parent columns bottom-aligned */
                [data-testid="column"] {{
                    display: flex !important;
                    flex-direction: column !important;
                    justify-content: flex-end !important;
                    align-items: flex-start !important;
                }}

                .dot-container {{
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    top: -18px;
                    gap: 0.09375rem;
                    margin: 0;
                    position: relative;
                    height: 0rem;
                }}

                .dot-wrapper {{
                    position: relative;
                    width: 2.5rem;
                    height: 3rem;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin: 0;
                }}

                .dot {{
                    font-size: 2.5rem;
                    color: {UNSELECTED_COLOR};
                    text-decoration: none;
                    transition: transform 0.2s ease, color 0.2s ease;
                    line-height: 1;
                    user-select: none;
                    transform-origin: center;
                    z-index: 10;
                    cursor: pointer;
                    pointer-events: none;
                }}

                div[data-testid="stButton"]:has(button[aria-label=""]):hover ~ .dot-container .dot {{
                    color: {HOVER_COLOR} !important;
                    transform: scale(1.2) !important;
                }}

                div[data-testid="stButton"]:has(button[aria-label=""]):hover ~ .dot-container .dot::after {{
                    content: attr(data-tooltip);
                    position: absolute;
                    bottom: 125%;
                    left: 50%;
                    transform: translateX(-50%);
                    background-color: #333;
                    color: #fff;
                    padding: 4px 8px;
                    border-radius: 4px;
                    white-space: nowrap;
                    font-size: 0.8rem;
                    pointer-events: none;
                    z-index: 15;
                }}

                div[data-testid="stButton"]:has(button[aria-label=""]):hover ~ .dot-container .dot::before {{
                    content: "";
                    position: absolute;
                    bottom: 115%;
                    left: 50%;
                    transform: translateX(-50%);
                    border-width: 5px;
                    border-style: solid;
                    border-color: #333 transparent transparent transparent;
                    pointer-events: none;
                    z-index: 15;
                }}

                .dot.selected {{
                    color: {PRIMARY_COLOR};
                    transform: scale(1.2);
                    font-weight: bold;
                    margin-top: -10px;
                }}

                div[data-testid="stButton"]:has(button[aria-label=""]) {{
                    position: absolute !important;
                    top: -18px;
                    left: 0 !important;
                    width: 2.5rem !important;
                    height: 3rem !important;
                    background: transparent !important;
                    border: none !important;
                    padding: 0 !important;
                    margin: 0 !important;
                    z-index: 5 !important;
                }}

                div[data-testid="stButton"]:has(button[aria-label=""]) button[aria-label=""] {{
                    position: absolute !important;
                    top: 0 !important;
                    left: 0 !important;
                    width: 100% !important;
                    height: 100% !important;
                    opacity: 0 !important;
                    background: transparent !important;
                    border: none !important;
                    box-shadow: none !important;
                    cursor: pointer !important;
                }}

                [data-testid="column"]:nth-child(2) {{
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                }}

                div[data-testid="column"] {{
                    margin: 0 !important;
                    padding: 0 !important;
                }}

                div[data-testid="stButton"] {{
                    margin: 0 !important;
                    padding: 0 !important;
                }}

                .stMarkdown {{
                    margin: 0 !important;
                    padding: 0 !important;
                }}

                .element-container {{
                    margin: 0 !important;
                    padding: 0 !important;
                }}
                </style>
                """,
                unsafe_allow_html=True,
            )

            # Render the UI for dots with invisible buttons
            cols = st.columns(len(dots))
            for i, (col, dot, tooltip) in enumerate(zip(cols, dots, tooltips)):
                is_selected = i == st.session_state.dot
                selected_class = "selected" if is_selected else ""

                with col:
                    if st.button("", key=f"dot_btn_{i}", use_container_width=True, help=tooltip):
                        if st.session_state.dot != i:
                            st.session_state.dot = i
                            st.query_params["dot"] = str(i)
                            st.rerun()

                    st.markdown(
                        f"""
                        <div class="dot-container">
                            <div class="dot-wrapper">
                                <span class="dot {selected_class}" data-tooltip="{tooltip}" id="dot_{i}">{dot}</span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            # Show selected form content
            selected_category = categories[st.session_state.dot]

        # Assuming per_tab_data and selected_category are already defined
        pdata = st.session_state.per_tab_data["Scraper"]
        cat_data = pdata["category_data"].setdefault(
            selected_category,
            {
                "scraper_urls": "",
                "url_scraper_disliked": "",
                "final_tickers": [],
                "max_tickers": 50,
            },
        )

        urls_key = f"two_tab_urls_input_{selected_category}"
        disliked_key = f"two_tab_disliked_url_{selected_category}"
        max_key = f"two_tab_max_tickers_{selected_category}"
        loop_break_key = f"two_tab_loop_break_{selected_category}"
        form_key = f"two_tab_scraper_form_{st.session_state.tab_select}_{selected_category}"

        import time
        from datetime import datetime, time as dtime

        # --- Initialize session state ---
        if "trade_running" not in st.session_state:
            st.session_state.trade_running = False
        if "trade_last_run" not in st.session_state:
            st.session_state.trade_last_run = 0
        if "two_tab_scanning_log" not in st.session_state:
            st.session_state.two_tab_scanning_log = ""
        if "two_tab_trading_log" not in st.session_state:
            st.session_state.two_tab_trading_log = ""
        if "trigger_trade" not in st.session_state:
            st.session_state.trigger_trade = False

        if f"two_tab_urls_input_{selected_category}" not in st.session_state:
            st.session_state[f"two_tab_urls_input_{selected_category}"] = cat_data.get("scraper_urls", "")
        if f"two_tab_max_tickers_{selected_category}" not in st.session_state:
            st.session_state[f"two_tab_max_tickers_{selected_category}"] = cat_data.get("max_tickers", 50)
        if f"two_tab_loop_break_{selected_category}" not in st.session_state:
            st.session_state[f"two_tab_loop_break_{selected_category}"] = 60
        if f"two_tab_disliked_url_{selected_category}" not in st.session_state:
            st.session_state[f"two_tab_disliked_url_{selected_category}"] = cat_data.get("url_scraper_disliked", "")

        if "trade_loop_count" not in st.session_state:
            st.session_state.trade_loop_count = 0
        if "trade_loop_date" not in st.session_state:
            st.session_state.trade_loop_date = datetime.now().date()



        # Add CSS to move the form up
        st.markdown("""
            <style>
            div[data-testid="stForm"] {
                margin-top: -20px;
            }
            </style>
        """, unsafe_allow_html=True)


        # --- Form for inputs and scan buttons ---
        
        with st.form(key=f"two_tab_scraper_form_{st.session_state.tab_select}_{selected_category}"):
            urls_input = st.text_area(
                "Paste each URL on a separate line:",
                height=120,
                key=f"two_tab_urls_input_{selected_category}",
                help="Enter URLs containing ticker lists (one per line), or enter tickers manually."
            )
            max_tickers = st.number_input(
                "Max total tickers (per URL):",
                min_value=1,
                max_value=200,
                step=50,
                key=f"two_tab_max_tickers_{selected_category}",
                help="Maximum number of tickers to extract from all URLs combined."
            )
            loop_break = st.number_input(
                "Time between loops (seconds):",
                min_value=10,
                max_value=3600,
                step=60,
                key=f"two_tab_loop_break_{selected_category}",
                help="Time delay in seconds between each trading loop."
            )
            disliked_url = st.text_input(
                "Remove tickers:",
                value=st.session_state.get(f"two_tab_disliked_url_{selected_category}", cat_data.get("url_scraper_disliked", "")),
                key=f"two_tab_disliked_url_{selected_category}",
                help="Enter tickers to exclude, separated by commas."
            )

            st.markdown("""
            <style>
            .stFormSubmitButton > button {
                margin-top: 10px;
            }
            </style>
            """, unsafe_allow_html=True)

            col1, gap1, col2 = st.columns([2, 0.1, 2])

            with col1:
                scan_btn = st.form_submit_button(f"Scan {selected_category}", use_container_width=True, type="tertiary")
            with col2:
                scan_all_btn = st.form_submit_button("Scan All", use_container_width=True, type="tertiary")

            prog_bar_container = render_progress_bar_container()
            prog_bar_container.empty()

            if scan_btn:
                st.session_state["show_all_tickers"] = False
                # Ensure cat_data is the correct dictionary
                cat_data = pdata["category_data"].setdefault(
                    selected_category,
                    {
                        "scraper_urls": "",
                        "url_scraper_disliked": "",
                        "final_tickers": [],
                        "max_tickers": 50,
                    }
                )
                cat_data["scraper_urls"] = urls_input
                cat_data["url_scraper_disliked"] = disliked_url
                cat_data["max_tickers"] = max_tickers

                st.session_state["two_tab_scanning_log"] = ""
                log, tickers = run_scan(selected_category, max_tickers, prog_bar_container)
                st.session_state["two_tab_scanning_log"] += log
                st.session_state["category_tickers"] = tickers
                # Update final_tickers in pdata
                cat_data["final_tickers"] = tickers

                prog_bar_container.empty()
                save_settings_to_file()

            if scan_all_btn:
                st.session_state["show_all_tickers"] = True
                st.session_state["two_tab_scanning_log"] = ""
                all_tickers = {}

                # Total number of categories for progress calculation
                total_categories = len(categories)
                progress_per_category = 100.0 / total_categories if total_categories > 0 else 100.0
                current_progress = 0.0

                for i, cat in enumerate(categories):
                    # Fetch or initialize category data
                    this_data = pdata["category_data"].setdefault(
                        cat,
                        {
                            "scraper_urls": "",
                            "url_scraper_disliked": "",
                            "final_tickers": [],
                            "max_tickers": 50,
                        },
                    )
                    # Pull current input values from session state
                    urls = st.session_state.get(f"two_tab_urls_input_{cat}", "")
                    disliked = st.session_state.get(f"two_tab_disliked_url_{cat}", "")
                    max_num = st.session_state.get(f"two_tab_max_tickers_{cat}", 50)

                    # Update the data dictionary for this category
                    this_data["scraper_urls"] = urls
                    this_data["url_scraper_disliked"] = disliked
                    this_data["max_tickers"] = max_num

                    # Run the scan for this category with progress
                    log, tickers = run_scan(cat, max_num, prog_bar_container, progress_start=current_progress, total_progress=progress_per_category)
                    st.session_state["two_tab_scanning_log"] += log
                    all_tickers[cat] = tickers
                    this_data["final_tickers"] = tickers

                    # Update progress
                    current_progress += progress_per_category
                    render_progress_bar(prog_bar_container, current_progress)

                # Ensure progress bar hits 100% and stays visible briefly
                render_progress_bar(prog_bar_container, 100.0)
                time.sleep(0.1)  # Brief delay (0.5 seconds) to show full bar
                prog_bar_container.empty()
                st.session_state["category_tickers"] = all_tickers
                save_settings_to_file()
                st.rerun()  # Force refresh to update UI





        # --- Timer and loop control ---

        with right_col:
            timer_col = st.empty()
            timer_col.info("&nbsp;")





            # Create two columns with equal width
            topleft_col, topright_col = st.columns([1, 0.83])

            # Left column: Start and Stop text and box

            with topleft_col:
                # Step 1: Create a persistent container for the labels (initialized once)
                if "label_container" not in st.session_state:
                    st.session_state.label_container = st.empty()

                # Step 2: Render the consolidated labels and HR in a single markdown block
                # Updated to move "Start" and "Stop" closer and shift blue box down
                st.session_state.label_container.markdown("""
                <style>
                /* Isolate labels from layout shifts and parent changes */
                .label-container {
                    position: relative !important;
                    width: 100% !important;
                    height: 100px !important; /* Fixed height to prevent column resizing */
                    contain: layout !important; /* Isolate from external layout changes */
                    z-index: 10000 !important;
                }
                
                /* Anti-flicker CSS for labels */
                .label-start, .label-stop {
                    position: absolute !important;
                    color: grey !important;
                    font-weight: bold !important;
                    font-size: 14px !important;
                    pointer-events: none !important;
                    transition: none !important; /* Prevent flicker */
                    will-change: transform !important;
                    transform: translateZ(0) !important;
                    line-height: 1 !important;
                    white-space: nowrap !important;
                    z-index: 10001 !important;
                }
                
                .label-start {
                    top: 0 !important;
                    left: 1.1rem !important;
                    margin-top: 1.3rem !important;
                }
                
                .label-stop {
                    top: 100% !important;
                    left: 1.1rem !important;
                    margin-top: 0.15rem !important; /* Reduced from 3.5rem to move Stop closer to Start */
                    transform: translateY(-100%) translateZ(0) !important;
                }
                
                /* Stable HR styling (blue box) */
                .stable-hr {
                    position: absolute !important;
                    top: 48.5% !important;
                    left: 0 !important;
                    width: 80% !important;
                    height: 100px !important;
                    background-color: #2b3e56!important;
                    border: none !important;
                    border-radius: 7px !important;
                    margin: 0 !important;
                    padding: 0 !important;
                    pointer-events: none !important;
                    user-select: none !important;
                    z-index: 9999 !important;
                    transition: none !important;
                    will-change: transform !important;
                    transform: translateY(-40%) !important; /* Adjusted from -50% to move blue box down */
                    /* TWEAK HERE: To move the blue box further down, increase the percentage (e.g., -35% or -30%).
                    To move it up, decrease it (e.g., -45% or -50%).
                    Example: transform: translateY(-35%) !important; */
                }
                
                /* Prevent column-level shifts during reruns */
                [data-testid="column"] {
                    transition: none !important;
                    contain: layout !important;
                }
                </style>
                
                <!-- Consolidated container for labels and HR -->
                <div class="label-container">
                    <span class="label-start">Start</span>
                    <span class="label-stop">Stop</span>
                    <hr class="stable-hr">
                </div>
                """, unsafe_allow_html=True)




            # Right column: Image placeholder text
            with topright_col:
                

                import streamlit as st
                import base64

                st.set_page_config(layout="wide")


                def get_base64_of_bin_file(bin_file):
                    with open(bin_file, "rb") as f:
                        data = f.read()
                    return base64.b64encode(data).decode()

                img_base64 = get_base64_of_bin_file("images/LOGO2.png")




                st.markdown(
                    f"""
                    <style>
                    .full-width-image img {{
                        margin-top: -27px;
                        padding: 0;
                        width: 100%;
                        display: block;
                    }}
                    </style>
                    <div class="full-width-image">
                        <img src="data:image/png;base64,{img_base64}" />
                    </div>
                    """,
                    unsafe_allow_html=True
                )




                # Display Name as Status

                st.markdown("<h4 style='text-align:center;margin-top: -16px;color:white;'>HalterAPI</h4>", unsafe_allow_html=True)








            # --- Scraped Tickers ---
            st.markdown("<div style='height: 29.5px;'></div>", unsafe_allow_html=True)
            st.markdown("#### Scraped Tickers")

            tickers_data = st.session_state.get("category_tickers", {})

            if st.session_state.get("show_all_tickers", False) and isinstance(tickers_data, dict):
                output_text = ""
                for cat in categories:
                    tickers = tickers_data.get(cat, [])
                    output_text += f"{cat}\n" + ("-" * 15) + "\n"
                    if tickers:
                        output_text += "\n".join(tickers) + "\n\n"
                    else:
                        output_text += "No tickers found.\n\n"
                st.text_area(
                    "",
                    output_text.strip(),
                    height=242,
                    disabled=True,
                    label_visibility="collapsed",
                    key=f"two_tab_scraped_tickers_combined_out",
                    placeholder="No tickers scraped yet."
                )
            else:
                tickers_to_display = tickers_data if isinstance(tickers_data, list) else []
                st.text_area(
                    "",
                    "\n".join(tickers_to_display),
                    height=242,
                    disabled=True,
                    label_visibility="collapsed",
                    placeholder=f"No tickers scraped yet for {selected_category}.",
                    key=f"two_tab_scraped_tickers_{selected_category}"
                )

            st.markdown(
                """
                <style>
                textarea {
                    border: 1.3px solid rgba(211, 211, 211, 0.3) !important;
                    border-radius: 10px !important;
                    padding: 8px !important;
                    box-sizing: border-box !important;
                    background-color: rgb(173, 216, 230, 0.05) !important;
                }
                </style>
                """,
                unsafe_allow_html=True
            )




            # -------------------------
            # Scanning Log
            # -------------------------

            st.markdown("<div style='height: 43px;'></div>", unsafe_allow_html=True)

      

            st.markdown("#### Scanning Log")
            st.text_area(
                "",
                st.session_state.get("two_tab_scanning_log", ""),
                height=152,
                disabled=True,
                label_visibility="collapsed",
                placeholder="No scanning activity to display."
            )









            import streamlit as st

            # =========================================================
            # 1. LAYOUT – Text | Spacer | Add Button | Delete Button
            # =========================================================
            col0, col_spacer, col_add, col_del = st.columns([5.8, 0.2, 1, 1])

            with col0:
                st.markdown(
                    '''
                    <div style="text-align: right; width: 100%;">
                    <span style="font-weight: bold; opacity: 0.8;" class="tab-controls-text">
                        Tab Controls&nbsp;&nbsp;&nbsp;|
                    </span>
                    ''',
                    unsafe_allow_html=True,
                )

            # ----- Add button -----
            with col_add:
                add_tab_btn = st.button("", key="add_tab_btn", use_container_width=True)
                st.markdown('<div class="emoji-overlay">✚</div>', unsafe_allow_html=True)

            # ----- Delete button -----
            with col_del:
                delete_tab_btn = st.button("", key="delete_tab_btn", use_container_width=True)
                st.markdown('<div class="emoji-overlay">🗑️</div>', unsafe_allow_html=True)

            # =========================================================
            # 2. CSS – proper overlay text (emoji floats OVER invisible button)
            # =========================================================
            st.markdown(
                """
                <style>

                /* Container for emoji overlay */
                .emoji-overlay {
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -56%);  /* optically centered */
                    font-size: 22px;
                    z-index: 20;        /* ABOVE the button */
                    pointer-events: none; /* allows clicks to pass through to button */
                }

                /* Ensure column has a relative container for absolute positioning */
                [data-testid="column"] {
                    position: relative;
                }

                /* Style the actual invisible buttons */
                .stButton > button {
                    background-color: #F5BF0300 !important; /* fully transparent */
                    border: 2px solid #0000 !important;     /* invisible border */
                    width: 36px !important;
                    height: 36px !important;
                    margin: 2px !important;
                    border-radius: 6px !important;
                    color: transparent !important;
                    padding: 0 !important;
                    position: relative;
                    z-index: 5; /* BELOW emoji */
                }

                /* hover still shows highlight */
                .stButton > button:hover {
                    background-color: #DAA52020 !important;
                    border-color: #fff !important;
                    border-width: 2px !important;
                }

                </style>
                """,
                unsafe_allow_html=True,
            )

            # =========================================================
            # 3. SESSION STATE (unchanged)
            # =========================================================
            if "confirm_delete" not in st.session_state:
                st.session_state.confirm_delete = False
            if "show_cannot_delete" not in st.session_state:
                st.session_state.show_cannot_delete = False
            if "add_new_tab" not in st.session_state:
                st.session_state.add_new_tab = False
            if "tab_list" not in st.session_state:
                st.session_state.tab_list = ["Scraper"]
            if "tab_select" not in st.session_state:
                st.session_state.tab_select = "Scraper"
            if "tab_add_notification" not in st.session_state:
                st.session_state.tab_add_notification = False
            if "active_dialog" not in st.session_state:
                st.session_state.active_dialog = None








                

            # Logic to determine which dialog (if any) to show
            if add_tab_btn and not (st.session_state.confirm_delete or st.session_state.show_cannot_delete):
                st.session_state.active_dialog = "add_new_tab"
            elif delete_tab_btn:
                if st.session_state.tab_select and st.session_state.tab_select in st.session_state.tab_list:
                    if len(st.session_state.tab_list) == 1:
                        st.session_state.active_dialog = "cannot_delete"
                    else:
                        st.session_state.active_dialog = "confirm_delete"
                else:
                    st.warning("No tab selected or tab does not exist.")

            # Dialog for single-tab case: "Cannot delete last tab."
            @st.dialog("Error")
            def cannot_delete_dialog():
                st.markdown(
                    """
                    <style>
                    div[data-testid="stDialog"] {
                        min-height: 200px !important;
                        border: 8px solid #ffe899 !important;
                        border-radius: 20px !important;
                        outline: none !important;
                        background-color: #2b3d56 !important;
                    }
                    div[data-testid="stDialog"] .stButton > button {
                        background-color: #F5BF03 !important;
                        border: 2px solid #000000 !important;
                        border-radius: 6px !important;
                        width: 100% !important;
                        height: 36px !important;
                        display: flex !important;
                        align-items: center !important;
                        justify-content: center !important;
                        cursor: pointer !important;
                        margin-top: 20px !important;
                    }
                    div[data-testid="stDialog"] .stButton > button:hover {
                        background-color: #2b3d56 !important;
                        border-color: #2b3d56 !important;
                    }
                    div[data-testid="stDialog"] p {
                        margin-bottom: 20px !important;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True
                )
                st.write("Cannot delete the last tab.")
                if st.button("Close", key="cannot_delete_close", use_container_width=True):
                    st.session_state.active_dialog = None
                    st.rerun()

            # Confirmation dialog for deleting tab
            @st.dialog("Confirm Delete Tab")
            def confirm_delete_dialog():
                st.markdown(
                    """
                    <style>
                    div[data-testid="stDialog"] {
                        min-height: 400px !important;
                        border: 8px solid #ffe899 !important;
                        border-radius: 20px !important;
                        outline: none !important;
                        background-color: #2b3d56 !important;
                    }
                    div[data-testid="stDialog"] .stButton > button {
                        background-color: #F5BF03 !important;
                        border: 2px solid #000000 !important;
                        border-radius: 6px !important;
                        width: 100% !important;
                        height: 36px !important;
                        display: flex !important;
                        align-items: center !important;
                        justify-content: center !important;
                        cursor: pointer !important;
                        margin-top: -10px !important;
                    }
                    div[data-testid="stDialog"] .stButton > button:hover {
                        background-color: #DAA520 !important;
                        border-color: #FFFFFF !important;
                    }
                    .yes-text-overlay {
                        position: absolute;
                        top: 0% !important;
                        left: 5% !important;
                        transform: translate(-50%, -30%) !important;
                        color: #ffe899 !important;
                        font-size: 16px !important;
                        font-weight: bold !important;
                        pointer-events: none !important;
                        z-index: 10001 !important;
                    }
                    div[data-testid="stDialog"] p {
                        margin-bottom: 30px !important;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True
                )
                st.write(f"Are you sure you want to delete the tab '{st.session_state.tab_select}'?")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(
                        """
                        <div style="position: relative;">
                            <span class="yes-text-overlay">Yes</span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    if st.button("Yes", key="confirm_delete_yes", use_container_width=True):
                        if st.session_state.tab_select in st.session_state.tab_list:
                            st.session_state.tab_list.remove(st.session_state.tab_select)
                            st.session_state.tab_select = st.session_state.tab_list[0] if st.session_state.tab_list else None
                        st.session_state.active_dialog = None
                        st.rerun()
                with col2:
                    if st.button("Cancel", key="confirm_delete_cancel", use_container_width=True):
                        st.session_state.active_dialog = None
                        st.rerun()

            # Dialog for adding a new tab
            @st.dialog("Add New Tab")
            def add_new_tab_dialog():
                st.markdown(
                    """
                    <style>
                    div[data-testid="stDialog"] h1 {
                        font-size: 30px !important;
                        font-weight: bold !important;
                        text-align: center !important;
                        color: #F5BF03 !important;
                        margin-bottom: 0px !important;
                    }
                    div[data-testid="stForm"][id*="add_tab_form"] button {
                        width: 100% !important;
                        background-color: #F5BF03 !important;
                        color: #000000 !important;
                        border-radius: 10px !important;
                        padding: 10px !important;
                        font-size: 16px !important;
                        font-weight: bold !important;
                        border: 2px solid #000000 !important;
                        transition: all 0.2s ease !important;
                    }
                    div[data-testid="stForm"][id*="add_tab_form"] button:hover {
                        background-color: #DAA520 !important;
                        color: #FFFFFF !important;
                        border-color: #FFFFFF !important;
                    }
                    div[data-testid="stForm"][id*="add_tab_form"] input {
                        border: 1.3px solid rgba(211, 211, 211, 0.3) !important;
                        border-radius: 10px !important;
                        padding: 8px !important;
                        background-color: rgba(173, 216, 230, 0.05) !important;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True
                )
                if st.button("Close", key="add_tab_close"):
                    st.session_state.active_dialog = None
                    st.session_state.tab_select = st.session_state.tab_list[0] if st.session_state.tab_list else "Scraper"
                    st.rerun()
                with st.form("add_tab_form", clear_on_submit=True):
                    new_tab_name = st.text_input("New tab name", max_chars=30)
                    submitted = st.form_submit_button("Add Tab")
                    if submitted:
                        new_tab_name = new_tab_name.strip()
                        if not new_tab_name:
                            st.warning("Tab name cannot be empty.")
                        elif new_tab_name in st.session_state.tab_list:
                            st.warning(f"Tab '{new_tab_name}' already exists.")
                        else:
                            st.session_state.tab_list.append(new_tab_name)
                            st.session_state.tab_select = new_tab_name
                            st.session_state.tab_add_notification = True
                            st.session_state.active_dialog = None
                            st.rerun()

            # Render the appropriate dialog based on active_dialog state
            if st.session_state.active_dialog == "cannot_delete":
                cannot_delete_dialog()
            elif st.session_state.active_dialog == "confirm_delete":
                confirm_delete_dialog()
            elif st.session_state.active_dialog == "add_new_tab":
                add_new_tab_dialog()







        with left_col:

            st.markdown("<div style='margin-top: 18px'></div>", unsafe_allow_html=True)

            trading_log_container = st.empty()  # For real-time Trading Log updates

            # --- Trading Log Display ---
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("#### Trading Log")
            trading_log_container = st.empty()
            trading_log_container.text_area(
                "",
                st.session_state.get("two_tab_trading_log", ""),
                height=200,
                disabled=True,
                label_visibility="collapsed",
                placeholder="No trading activity to display.",
                key=f"trade_log_output_{selected_category}"
            )














        with spacer_col:
            import streamlit as st
            import time
            from datetime import datetime
            import streamlit.components.v1 as components

            # -------------------------
            # Session state initialization
            # -------------------------
            if "trade_running" not in st.session_state:
                st.session_state.trade_running = False
            if "two_tab_trading_log" not in st.session_state:
                st.session_state.two_tab_trading_log = ""
            if "trade_last_run" not in st.session_state or st.session_state.trade_last_run is None:
                st.session_state.trade_last_run = 0
            if "trade_loop_count" not in st.session_state:
                st.session_state.trade_loop_count = 0
            if "trade_loop_date" not in st.session_state:
                st.session_state.trade_loop_date = datetime.now().date()

            # Initialize tab_list and tab_select if not already present
            if "tab_list" not in st.session_state:
                st.session_state.tab_list = []
            if "tab_select" not in st.session_state:
                st.session_state.tab_select = None

            # -------------------------
            # Global styles for centering, button overrides, dots, and labels
            # -------------------------
            st.markdown("""
            <style>
            .button-container {
                display: flex;
                flex-direction: column; /* Stack buttons vertically */
                justify-content: center;
                align-items: center;
                gap: 0rem; /* Reduced gap between buttons */
                margin-top: 2.4rem; /* Reduced margin to move buttons upward */
                width: 100%; /* Ensure container takes full width */
                max-width: 600px; /* Limit width for consistency */
                margin-left: auto;
                margin-right: auto;
            }

            /* Make both buttons relatively positioned for their dots and labels */
            div.stButton > button#custom_start_btn,
            div.stButton > button#custom_stop_btn {
                all: unset !important;
                cursor: pointer !important;
                border-radius: 9999px !important;
                font-size: 50px !important;
                font-weight: 900 !important;
                padding: 1rem 4rem !important;
                min-width: 280px !important;
                text-align: center !important;
                display: inline-flex !important;
                justify-content: center !important;
                align-items: center !important;
                transition: all 0.25s ease-in-out !important;
                color: #222 !important;
                background: transparent !important;
                position: relative !important; /* Allows dots and labels to position relative to buttons */
                z-index: 1 !important;
            }

            /* Hover interaction for buttons */
            div.stButton > button#custom_start_btn:hover,
            div.stButton > button#custom_stop_btn:hover {
                transform: scale(0.95) !important;
                color: #F5BF03 !important;
            }

            /* Visual pulse animation when active */
            @keyframes pulse {
                0% { transform: scale(1); opacity: 1; }
                50% { transform: scale(1.05); opacity: 0.9; }
                100% { transform: scale(1); opacity: 1; }
            }

            div.stButton > button#custom_start_btn.active {
                color: #F5BF03 !important; /* Yellow when trading loop is running */
                animation: pulse 1.5s infinite ease-in-out;
            }

            div.stButton > button#custom_stop_btn.active {
                color: #AA2828 !important;
            }

            /* Center and responsive */
            @media (max-width: 768px) {
                div.stButton > button#custom_start_btn,
                div.stButton > button#custom_stop_btn {
                    font-size: 36px !important;
                    padding: 0.8rem 2rem !important;
                    min-width: 200px !important;
                }
                .button-container {
                    gap: 1.5rem; /* Reduce gap on mobile */
                    max-width: 100%; /* Full width on mobile */
                }
            }

            /* Isolated dot styling and positioning (over Start button) */
            .isolated-yellow-dot-start,
            .isolated-yellow-dot-stop {
                position: absolute !important;
                top: 50% !important;
                left: 0% !important;
                transform: translate(5px, -50%) !important; /* Align left with 10px offset */
                width: 20px;
                height: 20px;
                background-color: grey; /* Default color */
                border-radius: 50%; /* Makes it a circle */
                display: inline-block;
                cursor: default; /* No pointer cursor since it's unclickable */
                pointer-events: none; /* Makes it unclickable and non-interfering */
                z-index: 10000 !important; /* Above buttons */
            }

            /* Overlay yellow dot, invisible by default, perfectly matching grey dot */
            .yellow-status-dot-start,
            .yellow-status-dot-stop {
                position: absolute !important;
                top: 50% !important;
                left: 0% !important;
                transform: translate(5px, -110%) !important;
                width: 20px;
                height: 20px;
                border-radius: 50%;
                z-index: 10001 !important;  /* Above the grey dot */
                background-color: #F5BF03 !important;
                opacity: 0;
                pointer-events: none !important;
                transition: opacity 0.5s;
            }
            .yellow-status-dot-start.visible {
                opacity: 1;
            }
            .yellow-status-dot-stop.visible {
                opacity: 1;
            }

            /* Label styling for Start and Stop */
            .label-start,
            .label-stop {
                position: absolute !important;
                top: calc(50% - 10.5px) !important; /* Move up 5px from center */
                left: 35px !important; /* Dot right edge (20px + 10px offset) + 5px gap */
                transform: translateY(-50%) !important; /* Vertical centering of text */
                font-size: 14px !important; /* Small size */
                color: grey !important; /* Grey color */
                font-weight: bold !important;
                pointer-events: none !important; /* Unclickable */
                z-index: 10000 !important; /* Above buttons */
            }

            /* Nuclear reset for Delete Tab button only */
            #delete-tab-container .stButton > button {
                all: unset !important;  /* wipe out ALL inherited CSS */
                display: block !important;
                visibility: visible !important;
                opacity: 1 !important;
                /* Force positioning */
                position: relative !important;
                z-index: 9999 !important;
                /* Make it obvious */
                background-color: #F5BF03 !important;
                color: #000000 !important;
                border: 3px solid #000000 !important;
                border-radius: 10px !important;
                padding: 12px !important;
                font-size: 18px !important;
                font-weight: bold !important;
                width: 100% !important;
                text-align: center !important;
                cursor: pointer !important;
            }
            #delete-tab-container .stButton > button:hover {
                background-color: #DAA520 !important;
                color: #FFFFFF !important;
                border-color: #FFFFFF !important;
            }
            textarea {
                border: 1.3px solid rgba(211, 211, 211, 0.3) !important;
                border-radius: 10px !important;
                padding: 8px !important;
                box-sizing: border-box !important;
                background-color: rgb(173, 216, 230, 0.05) !important;
            }
            </style>
            """, unsafe_allow_html=True)

            # -------------------------
            # Layout for buttons (stacked vertically: Start above, Stop below)
            # -------------------------
            st.markdown('<div class="button-container">', unsafe_allow_html=True)

            # Start button (top) with its dots and label
            st.markdown('<div style="position: relative;">', unsafe_allow_html=True)  # Container for Start button, dots, and label
            start_clicked = st.button("Start", key="ui_start_button")
            st.markdown("""
            <script>
            const btns = document.querySelectorAll('div.stButton > button');
            if (btns.length) { btns[btns.length - 1].id = 'custom_start_btn'; }
            </script>
            """, unsafe_allow_html=True)
            st.markdown('<div class="isolated-yellow-dot-start"></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="yellow-status-dot-start{" visible" if st.session_state.trade_running else ""}"></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # Stop button (bottom) with its dots and label
            st.markdown('<div style="position: relative;">', unsafe_allow_html=True)  # Container for Stop button, dots, and label
            stop_clicked = st.button("Stop", key="ui_stop_button")
            st.markdown("""
            <script>
            const btns = document.querySelectorAll('div.stButton > button');
            if (btns.length) { btns[btns.length - 1].id = 'custom_stop_btn'; }
            </script>
            """, unsafe_allow_html=True)
            st.markdown('<div class="isolated-yellow-dot-stop"></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="yellow-status-dot-stop{" visible" if not st.session_state.trade_running else ""}"></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

            # -------------------------
            # Core control logic
            # -------------------------
            if start_clicked:
                st.session_state.trade_running = True
                st.session_state.trade_last_run = 0
                st.session_state.trade_loop_count = 0
                st.session_state.trade_loop_date = datetime.now().date()
                st.session_state.two_tab_trading_log = (
                    f"=== Trading Loop Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n\n"
                )
                # Option 2: Unicode non-breaking space after emoji to force spacing
                st.toast("🚀\u200B \u200B \u200B Trading loop started!") # Toast notification
                st.rerun()

            if stop_clicked:
                st.session_state.trade_running = False
                st.session_state.two_tab_trading_log += (
                    f"=== Trading Stopped: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ==="
                )
                st.toast("Trading loop stopped.")
                st.rerun()

            # -------------------------
            # Trading Loop with LOOPDELAY
            # -------------------------
            if st.session_state.trade_running:
                now = time.time()
                last_run = st.session_state.trade_last_run or 0
                loop_delay = st.session_state.get(f"two_tab_loop_break_{selected_category}", 60)

                next_trade_timestamp = last_run + loop_delay
                next_trade_time_str = datetime.fromtimestamp(next_trade_timestamp).strftime('%Y-%m-%d %H:%M:%S')

                # Check if it's time to trade
                if now >= next_trade_timestamp:
                    # Time for trading!
                    st.session_state.trade_last_run = now  # Update last_run before executing trades

                    # Handle daily reset
                    today = datetime.now().date()
                    if st.session_state.trade_loop_date != today:
                        st.session_state.trade_loop_date = today
                        st.session_state.trade_loop_count = 0
                        st.session_state.two_tab_trading_log += f"Daily reset: New day started ({today}). Loop count reset to 0.\n\n"

                    # Log loop header and bias
                    st.session_state.trade_loop_count += 1
                    loop_num = st.session_state.trade_loop_count
                    # Set bias: Bullish for Loop 1, then alternate
                    if st.session_state.trade_loop_count == 1:
                        st.session_state.bias_market = "Bullish"
                    else:
                        st.session_state.bias_market = "Bearish" if st.session_state.bias_market == "Bullish" else "Bullish"
                    loop_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    bias = st.session_state.bias_market
                    st.session_state.two_tab_trading_log += f"=== Loop {loop_num}: {loop_time} ===\n"
                    st.session_state.two_tab_trading_log += f"Loop delay: {loop_delay} seconds\n"
                    st.session_state.two_tab_trading_log += f"Bias: {bias}\n"

                    selected_indicators = st.session_state.get('selected_indicators', [])
                    tickers_to_trade = pdata.get("category_data", {}).get(selected_category, {}).get("final_tickers", [])

                    if not selected_indicators:
                        msg = "No indicators selected. Please select at least one indicator. Skipping trade."
                        st.session_state.two_tab_trading_log += msg + "\n\n"
                        timer_col.warning(msg)
                    elif not tickers_to_trade:
                        msg = f"No tickers available for trading in {selected_category}."
                        st.session_state.two_tab_trading_log += msg + "\n\n"
                        timer_col.warning(msg)
                        st.session_state.trade_running = False
                    else:
                        # Log selected indicators with Bullish/Bearish breakdown
                        selected = st.session_state.selected_indicators or []

                        bullish_count = len([ind for ind in selected if "Bullish" in ind])
                        bearish_count = len([ind for ind in selected if "Bearish" in ind])
                        total_count = len(selected)

                        st.session_state.two_tab_trading_log += (
                            f"Selected Indicators: Total: {total_count} | Bullish: {bullish_count} | Bearish: {bearish_count}\n"
                        )

                        # Log number of tickers being traded
                        st.session_state.two_tab_trading_log += f"Tickers to trade: {len(tickers_to_trade)}\n"




                        try:
                            market_status = is_market_open()
                            import pytz
                            if not market_status["is_open"]:
                                
                                timer_col.warning("Market Closed")
                                st.session_state.trade_running = False
                            else:
                                msg = "Executing trades..."
                                st.session_state.two_tab_trading_log += msg + "\n"
                                timer_col.info(msg)

                                # Call scan_and_trade_etf_stocks
                                trade_log = scan_and_trade_etf_stocks(
                                    tickers=tickers_to_trade,
                                    selected_indicators=selected_indicators,
                                    trading_log_container=trading_log_container
                                )
                                st.session_state.two_tab_trading_log += trade_log
                                timer_col.success(f"Loop {loop_num} complete.")
                        except Exception as e:
                            pass

                    # Update the trading log display
                    st.rerun()

                    # Update last_run for the next loop
                    st.session_state.trade_last_run = time.time()
                    # Wait for the next trade time
                    now = time.time()
                    next_trade_timestamp = st.session_state.trade_last_run + loop_delay
                    time_remaining = next_trade_timestamp - now
                    timer_col.info(f"Next trade at {datetime.fromtimestamp(next_trade_timestamp).strftime('%Y-%m-%d %H:%M:%S')}")
                    if time_remaining > 0:
                        while time_remaining > 0 and st.session_state.trade_running:
                            time.sleep(min(time_remaining, 1))  # Check every second
                            now = time.time()
                            time_remaining = next_trade_timestamp - now
                    if st.session_state.trade_running:
                        st.rerun()
                else:
                    # Display the next trade time and wait
                    timer_col.info(f"Next trade at {next_trade_time_str}")
                    time_remaining = next_trade_timestamp - now
                    if time_remaining > 0:
                        while time_remaining > 0 and st.session_state.trade_running:
                            time.sleep(min(time_remaining, 1))  # Check every second
                            now = time.time()
                            time_remaining = next_trade_timestamp - now
                    if st.session_state.trade_running:
                        st.rerun()
            else:

    
                market_status = is_market_open()
                if not market_status.get("is_open", False):
                    try:
                        next_open_local = market_status["next_open"].astimezone(pytz.timezone("US/Eastern"))
                        next_open_str = next_open_local.strftime('%Y-%m-%d %H:%M:%S %Z')
                        timer_col.info(f"Market Closed — Next open: {next_open_str}")
                    except:
                        timer_col.info("Market Closed")
                else:
                    timer_col.info("Trading loop is stopped")

            # -------------------------
            # JavaScript: ID persistence, state indication, and dot color control
            # -------------------------
            running = st.session_state.trade_running
            components.html(f"""
            <script>
            const runState = {str(running).lower()};
            function setIDsAndDotState() {{
                // Assign button IDs
                const btns = document.querySelectorAll('div.stButton > button');
                btns.forEach(b => {{
                    if (b.innerText.trim() === "Start") b.id = 'custom_start_btn';
                    if (b.innerText.trim() === "Stop") b.id = 'custom_stop_btn';
                }});
                const startEl = document.getElementById('custom_start_btn');
                const stopEl = document.getElementById('custom_stop_btn');
                if (startEl && runState) startEl.classList.add('active');
                if (stopEl && !runState) stopEl.classList.add('active');
                // Dots handled by overlay logic, no JS toggle required
            }}

            // Ensure IDs and dot state are applied during reruns
            setTimeout(setIDsAndDotState, 50);
            setTimeout(setIDsAndDotState, 300);
            setTimeout(setIDsAndDotState, 1000);
            </script>
            """, height=0)

        with right_col:


            # -------------------------
            # JavaScript: ID persistence, state indication, and dot color control
            # -------------------------
            running = st.session_state.trade_running
            components.html(f"""
            <script>
            const runState = {str(running).lower()};
            function setIDsAndDotState() {{
                // Assign button IDs
                const btns = document.querySelectorAll('div.stButton > button');
                btns.forEach(b => {{
                    if (b.innerText.trim() === "Start") b.id = 'custom_start_btn';
                    if (b.innerText.trim() === "Stop") b.id = 'custom_stop_btn';
                }});
                const startEl = document.getElementById('custom_start_btn');
                const stopEl = document.getElementById('custom_stop_btn');
                if (startEl && runState) startEl.classList.add('active');
                if (stopEl && !runState) stopEl.classList.add('active');

                // Control Start dot color based on runState
                const startDot = document.querySelector('.isolated-yellow-dot-start');
                if (startDot) {{
                    if (runState) {{
                        startDot.classList.add('active');
                    }} else {{
                        startDot.classList.remove('active');
                    }}
                }}
            }}

            // Ensure IDs and dot state are applied during reruns
            setTimeout(setIDsAndDotState, 50);
            setTimeout(setIDsAndDotState, 300);
            setTimeout(setIDsAndDotState, 1000);
            </script>
            """, height=0)

            import streamlit as st









