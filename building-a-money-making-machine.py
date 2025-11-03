# money_machine.py
# Ek hi file mein pura Money-Making Stock Analyzer!
# uv + streamlit + yfinance + plotly = ₹₹₹

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import hashlib

# -----------------------------
# Page Config & Style
# -----------------------------
st.set_page_config(
    page_title="Money Machine Pro",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for pro look
st.markdown("""
<style>
    .main {background-color: #0e1117;}
    .stApp {background: linear-gradient(to bottom, #1a1a2e, #16213e);}
    h1, h2, h3 {color: #00ff88 !important;}
    .stTextInput > div > div > input {background-color: #16213e; color: #00ff88;}
    .stButton>button {background-color: #00ff88; color: black; font-weight: bold;}
    .premium-box {border: 2px solid #00ff88; padding: 15px; border-radius: 15px; background: #16213e;}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Fake Auth (Session State)
# -----------------------------
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'premium' not in st.session_state:
    st.session_state.premium = False

def fake_login(username, password):
    return hashlib.md5(password.encode()).hexdigest() == "5f4dcc3b5aa765d61d8327deb882cf99"  # "password"

# -----------------------------
# Login Screen
# -----------------------------
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align:center;'>💰 Money Machine Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#aaa;'>Login to unlock your wealth engine</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("Username", value="admin")
            password = st.text_input("Password", type="password", value="password")
            login_btn = st.form_submit_button("Login 🚀")
            
            if login_btn:
                if fake_login(username, password):
                    st.session_state.logged_in = True
                    st.session_state.premium = True if username == "pro" else False
                    st.success("Logged in! Welcome to the Money Machine!")
                    st.rerun()
                else:
                    st.error("Wrong credentials! Try: admin / password | pro / password")
    st.stop()

# -----------------------------
# Premium Check
# -----------------------------
def check_premium():
    if not st.session_state.premium:
        st.markdown("""
        <div class="premium-box">
            <h3>🔒 Premium Feature Locked</h3>
            <p>Upgrade to <b>Pro</b> to unlock:</p>
            <ul>
                <li>AI Price Predictions (LSTM)</li>
                <li>Risk Score & Volatility Alerts</li>
                <li>Export to PDF/CSV</li>
                <li>Unlimited Stocks</li>
            </ul>
            <p><b>Username: pro | Password: password</b> → Instant Pro Access!</p>
        </div>
        """, unsafe_allow_html=True)
        return False
    return True

# -----------------------------
# Main App
# -----------------------------
st.markdown("<h1 style='text-align:center;'>💸 Stock Portfolio Analyzer</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#aaa;'>Enter stocks. Get returns. Make money. Repeat.</p>", unsafe_allow_html=True)

# Sidebar Inputs
with st.sidebar:
    st.header("📈 Portfolio Input")
    stock_input = st.text_area(
        "Stock Symbols (one per line)",
        value="AAPL\nGOOGL\nMSFT\nTSLA",
        height=150,
        help="Example: AAPL, NVDA, AMZN"
    )
    col_start, col_end = st.columns(2)
    with col_start:
        start_date = st.date_input("Start", datetime.now() - timedelta(days=365))
    with col_end:
        end_date = st.date_input("End", datetime.now())
    
    analyze_btn = st.button("Analyze Portfolio 🚀", use_container_width=True)

# -----------------------------
# Analysis Logic
# -----------------------------
if analyze_btn:
    symbols = [s.strip().upper() for s in stock_input.split('\n') if s.strip()]
    
    if not symbols:
        st.error("Please enter at least one stock!")
    else:
        with st.spinner(f"Fetching data for {len(symbols)} stocks..."):
            try:
                data = yf.download(symbols, start=start_date, end=end_date, progress=False)['Adj Close']
                data = data.dropna(axis=1, how='all')  # Clean
            except:
                st.error("Failed to fetch data. Check symbols or internet.")
                st.stop()

        if data.empty or data.shape[1] == 0:
            st.error("No data found. Try valid symbols like AAPL, GOOGL.")
        else:
            # Returns Calculation
            returns = ((data.iloc[-1] / data.iloc[0]) - 1) * 100
            returns_df = pd.DataFrame({
                'Stock': data.columns,
                'Return (%)': returns.round(2),
                'Final Price': data.iloc[-1].round(2),
                'Start Price': data.iloc[0].round(2)
            }).sort_values('Return (%)', ascending=False)

            # Display Results
            col1, col2 = st.columns([2, 1])
            with col1:
                st.subheader("📊 Portfolio Performance")
                st.dataframe(returns_df, use_container_width=True, hide_index=True)

            with col2:
                st.subheader("📈 Summary")
                total_return = returns_df['Return (%)'].mean()
                winners = len(returns_df[returns_df['Return (%)'] > 0])
                st.metric("Avg Return", f"{total_return:.2f}%")
                st.metric("Winning Stocks", f"{winners}/{len(symbols)}")

            # Price Chart
            st.subheader("📉 Price Trends")
            fig = px.line(
                data.reset_index().melt(id_vars='Date', var_name='Stock', value_name='Price'),
                x='Date', y='Price', color='Stock',
                title="Stock Price Evolution",
                markers=True
            )
            fig.update_layout(height=500, template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)

            # Premium Features
            if check_premium():
                st.success("Premium Unlocked: AI Predictions Coming Soon!")
                # Future: Add LSTM model here
            else:
                st.info("Login as **pro / password** to unlock AI predictions!")

            # Export Button (Premium Only)
            if check_premium():
                csv = returns_df.to_csv(index=False)
                st.download_button(
                    "📥 Download Report (CSV)",
                    csv,
                    "portfolio_report.csv",
                    "text/csv"
                )

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.markdown("""
<div style='text-align:center; color:#666;'>
    <p>Built with <b>uv</b> + <b>Streamlit</b> | 30+ Years of Python Magic ✨</p>
    <p>Deploy on <a href='https://share.streamlit.io' target='_blank'>Streamlit Cloud</a> • Monetize with Stripe</p>
</div>
""", unsafe_allow_html=True)

# Logout
if st.sidebar.button("Logout"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()