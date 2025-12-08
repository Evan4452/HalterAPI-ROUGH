import streamlit as st

st.set_page_config(page_title="HalterAI", layout="wide")

# --- Custom CSS styling ---
st.markdown("""
<style>
/* Custom tab styling when selected (active) */
div[data-testid="stTabs"] div[role="tab"]:nth-child(1)[aria-selected="true"] {
    background-color: #FFD700 !important;  /* Overview - Yellow */
    color: black !important;
}

div[data-testid="stTabs"] div[role="tab"]:nth-child(2)[aria-selected="true"],
div[data-testid="stTabs"] div[role="tab"]:nth-child(3)[aria-selected="true"] {
    background-color: #FFA500 !important;  /* Stocks/ETFs Options - Orange */
    color: white !important;
}

div[data-testid="stTabs"] div[role="tab"]:nth-child(4)[aria-selected="true"],
div[data-testid="stTabs"] div[role="tab"]:nth-child(5)[aria-selected="true"] {
    background-color: #F5F5DC !important;  /* Stocks/Crypto - Beige */
    color: black !important;
}

/* Optional: remove red highlight on hover/focus */
div[data-testid="stTabs"] div[role="tab"]:focus {
    box-shadow: none !important;
}
</style>
""", unsafe_allow_html=True)

# --- Define the 5 tabs ---
tabs = st.tabs([
    "Overview",
    "Options",
    "ETFs",
    "Shares",
    "Crypto"
])

# --- Tab content placeholders ---
with tabs[0]:
    st.header("📊 Overview")
    st.write("Welcome to HalterAI.")

with tabs[1]:
    st.header("📈 Stocks (Options)")
    st.write("Option trades for stocks.")

with tabs[2]:
    st.header("📊 ETFs (Options)")
    st.write("Option trades for ETFs.")

with tabs[3]:
    st.header("📈 Stocks (Equity)")
    st.write("Buy/sell actual stocks.")

with tabs[4]:
    st.header("💰 Crypto")
    st.write("Trade crypto pairs.")
