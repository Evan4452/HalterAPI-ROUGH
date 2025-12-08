import streamlit as st

# --- Set up theme in session state (default: Dark) ---
if "theme" not in st.session_state:
    st.session_state.theme = "Dark"

# --- Theme values (red theme) ---
theme = st.session_state.theme
primary_red = "#FF4B4B"
button_bg = primary_red if theme == "Dark" else "#fff0f0"
button_text = "#fff" if theme == "Dark" else primary_red
background_color = "#1e1e1e" if theme == "Dark" else "#ffffff"
text_color = "#ffffff" if theme == "Dark" else "#000000"
opposite_theme = "Light" if theme == "Dark" else "Dark"
button_label = f"{opposite_theme} Mode"

# --- Custom CSS for Button, Layout, and Sidebar ---
st.markdown(f"""
<style>
/* --- Theme Toggle Button --- */
div[data-testid="stButton"] > button {{
    background-color: {button_bg};
    color: {button_text};
    border: 1.5px solid {primary_red};
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 0.95rem;
    cursor: pointer;
    transition: 0.3s;
    margin-top: 1rem;
}}
div[data-testid="stButton"] > button:hover {{
    filter: brightness(1.1);
    border: 1.5px solid #b22222;
}}

/* --- Enlarge gear tab --- */
div[data-testid="stTabs"] div[role="tab"]:last-child span {{
    font-size: 1.3rem !important;
    display: flex;
    align-items: center;
    justify-content: center;
}}

/* --- Slide-out Sidebar --- */
#custom-left-sidebar {{
    position: fixed;
    top: 0;
    left: -320px;
    width: 300px;
    height: 100vh;
    background: {background_color};
    color: {text_color};
    box-shadow: 2px 0 12px rgba(0,0,0,0.15);
    z-index: 9999;
    transition: left 0.5s cubic-bezier(.5,1,.89,1);
    padding: 2rem 1.5rem 1.5rem 1.5rem;
    overflow-y: auto;
    border-right: 8px solid {primary_red};
}}
#custom-left-sidebar:hover,
#left-hover-zone:hover + #custom-left-sidebar {{
    left: 0;
}}
#left-hover-zone {{
    position: fixed;
    top: 0;
    left: 0;
    width: 24px;
    height: 100vh;
    z-index: 9998;
    background: transparent;
}}
#custom-left-sidebar h3 {{
    margin-top: 0;
    color: {primary_red};
}}
#custom-left-sidebar::-webkit-scrollbar {{
    width: 6px;
    background: transparent;
}}
#custom-left-sidebar::-webkit-scrollbar-thumb {{
    background: {primary_red};
    border-radius: 3px;
}}
</style>

<!-- Hover zone and sidebar HTML -->
<div id="left-hover-zone"></div>
<div id="custom-left-sidebar">
    <h3>Data Panel</h3>
    <p>This is your custom sidebar!<br>
    You can put any data, charts, or controls here.<br>
    <b>Hover your mouse on the left edge</b> to open.</p>
    <hr>
    <ul>
        <li>Live price: <b>$123.45</b></li>
        <li>Status: <span style="color:limegreen">Active</span></li>
        <li>More info...</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# --- Layout: Tabs ---
tabs = st.tabs(["Overview", "Options", "ETFs", "Shares", "Crypto", "⚙️"])

# CSS to make only the selected tab's label red (no background, no underline)
st.markdown(f"""
<style>
div[data-testid="stTabs"] div[role="tab"][aria-selected="true"] span {{
    color: {primary_red} !important;
    font-weight: bold;
}}
div[data-testid="stTabs"] div[role="tab"][aria-selected="true"] {{
    background: transparent !important;
    border-bottom: none !important;
}}
</style>
""", unsafe_allow_html=True)

# --- CSS Theme Styling ---
st.markdown(f"""
<style>
body {{
    background-color: {background_color};
    color: {text_color};
}}

div[data-testid="stAppViewContainer"] {{
    background-color: {background_color};
    color: {text_color};
}}

/* Custom tab colors - all active tabs are RED */
div[data-testid="stTabs"] div[role="tab"][aria-selected="true"] {{
    background-color: {primary_red} !important;
    color: {primary_red} !important;
    border-bottom: 3px solid {primary_red} !important;
}}

/* Settings tab is darker */
div[data-testid="stTabs"] div[role="tab"]:last-child[aria-selected="true"] {{
    background-color: #222 !important;
    color: {primary_red} !important;
    border-bottom: 3px solid #222 !important;
}}

/* General text color override */
html, body, [class*="st-"] {{
    color: {text_color} !important;
}}

/* Remove focus border */
div[data-testid="stTabs"] div[role="tab"]:focus {{
    box-shadow: none !important;
}}
</style>
""", unsafe_allow_html=True)

# --- Tab content ---
with tabs[0]:
    st.header("Overview")
    st.write("Welcome to HalterAPI.")

with tabs[1]:
    st.header("Options")
    st.write("Option trades for stocks.")

with tabs[2]:
    st.header("ETFs")
    st.write("Option trades for ETFs.")

with tabs[3]:
    st.header("Shares")
    st.write("Not available in beta.")

with tabs[4]:
    st.header("Crypto")
    st.write("Not available in beta.")

with tabs[5]:
    st.header("Settings")
    if st.button(button_label, key="theme-btn"):
        st.session_state.theme = opposite_theme
        st.rerun()
