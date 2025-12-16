import streamlit as st
import pandas as pd
import asyncio
from ingestion.binance_ws import stream_trades
from analytics.resample import resample_ticks
from analytics.stats import compute_zscore
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Quant Dashboard", layout="wide")
st.title("Live Quant Analytics Dashboard")

# Sidebar controls
symbol = st.sidebar.text_input("Symbol", value="btcusdt")
timeframe = st.sidebar.selectbox("Resample timeframe", ["1s", "1m", "5m"])
rolling_window = st.sidebar.slider("Rolling window", min_value=2, max_value=50, value=10)

# Placeholder for charts
price_chart = st.empty()
zscore_chart = st.empty()

# Auto-refresh every 2 seconds
st_autorefresh(interval=2000, key="datarefresh")

# Initialize ticks list in session_state
if "ticks" not in st.session_state:
    st.session_state.ticks = []

# Background function to collect data
async def collect_ticks():
    await stream_trades(symbol, st.session_state.ticks)

# Start WebSocket only once
if "ws_started" not in st.session_state:
    st.session_state.ws_started = True
    asyncio.run(collect_ticks())

# If we have ticks, process and plot
if st.session_state.ticks:
    df = pd.DataFrame(st.session_state.ticks)
    df.set_index("timestamp", inplace=True)

    # Resample
    resampled = resample_ticks(df, timeframe)

    # Compute rolling z-score
    resampled["zscore"] = compute_zscore(resampled["price"].rolling(rolling_window).mean())

    # Plot charts
    price_chart.line_chart(resampled["price"])
    zscore_chart.line_chart(resampled["zscore"])
