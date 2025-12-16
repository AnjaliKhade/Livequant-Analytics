import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from datetime import datetime, timedelta

from ingestion.binance_ws import BinanceWebSocket
from storage.store import TickStore, ticks_to_dataframe
from analytics.resample import resample_ticks
from analytics.stats import (
    compute_zscore, adf_test, compute_summary_stats,
    rolling_corr, compute_volatility, compute_returns
)
from analytics.pairs import PairsTradingAnalytics, generate_trading_signals
from alerts.alert_engine import (
    AlertEngine, zscore_above, zscore_below, 
    price_above, price_below, volume_spike
)

# Page configuration
st.set_page_config(
    page_title="Quant Trading Analytics Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "ws_clients" not in st.session_state:
    st.session_state.ws_clients = {}

# Initialize database connection only once to avoid locking
if "db" not in st.session_state:
    try:
        st.session_state.db = TickStore()
    except Exception as e:
        st.error(f"Database initialization failed: {e}")
        st.stop()

if "alert_engine" not in st.session_state:
    st.session_state.alert_engine = AlertEngine()
if "last_update" not in st.session_state:
    st.session_state.last_update = datetime.now()

# Title
st.title("📊 Live Quant Analytics Dashboard")
st.markdown("Real-time market analytics for statistical arbitrage and pairs trading")

# Sidebar Controls
st.sidebar.header("⚙️ Configuration")

# Symbol Selection
st.sidebar.subheader("Data Source")
mode = st.sidebar.radio("Mode", ["Live Stream", "Upload OHLC"])

if mode == "Live Stream":
    symbols_input = st.sidebar.text_input(
        "Symbols (comma-separated)", 
        value="btcusdt,ethusdt"
    )
    symbols = [s.strip().lower() for s in symbols_input.split(",")]
    
    # Start WebSocket streams
    for symbol in symbols:
        if symbol not in st.session_state.ws_clients:
            ws = BinanceWebSocket()
            ws.start(symbol)
            st.session_state.ws_clients[symbol] = ws
            st.sidebar.success(f"Started {symbol} stream")
            
else:
    uploaded_file = st.sidebar.file_uploader(
        "Upload OHLC CSV",
        type=['csv'],
        help="CSV with columns: timestamp, symbol, open, high, low, close, volume"
    )
    
    if uploaded_file:
        df_upload = pd.read_csv(uploaded_file)
        df_upload['timestamp'] = pd.to_datetime(df_upload['timestamp'])
        
        # Convert OHLC to tick-like format (using close price)
        ticks_from_upload = []
        for _, row in df_upload.iterrows():
            ticks_from_upload.append({
                'timestamp': row['timestamp'],
                'symbol': row.get('symbol', 'UPLOADED'),
                'price': row['close'],
                'qty': row.get('volume', 0)
            })
        
        st.session_state.db.insert_ticks(ticks_from_upload)
        st.sidebar.success(f"Uploaded {len(ticks_from_upload)} records")
        symbols = df_upload['symbol'].unique().tolist() if 'symbol' in df_upload.columns else ['UPLOADED']

# Analytics Controls
st.sidebar.subheader("Analytics Parameters")
timeframe = st.sidebar.selectbox(
    "Resample Timeframe",
    ["1s", "1m", "5m"],
    index=1
)

rolling_window = st.sidebar.slider(
    "Rolling Window",
    min_value=5,
    max_value=100,
    value=20,
    step=5
)

# Pairs Trading
st.sidebar.subheader("Pairs Trading")
enable_pairs = st.sidebar.checkbox("Enable Pairs Analysis")

if enable_pairs and len(symbols) >= 2:
    symbol_y = st.sidebar.selectbox("Symbol Y (dependent)", symbols, index=1 if len(symbols) > 1 else 0)
    symbol_x = st.sidebar.selectbox("Symbol X (independent)", symbols, index=0)
else:
    symbol_y = symbol_x = symbols[0] if symbols else None

# Alert Configuration
st.sidebar.subheader("🔔 Alerts")
alert_type = st.sidebar.selectbox(
    "Alert Type",
    ["None", "Z-Score Above", "Z-Score Below", "Price Above", "Price Below", "Volume Spike"]
)

if alert_type != "None":
    if "Z-Score" in alert_type:
        alert_threshold = st.sidebar.number_input("Z-Score Threshold", value=2.0, step=0.1)
    elif "Price" in alert_type:
        alert_threshold = st.sidebar.number_input("Price Threshold", value=50000.0, step=100.0)
    
    if st.sidebar.button("Add Alert"):
        alert_name = f"{alert_type}_{datetime.now().strftime('%H%M%S')}"
        
        if alert_type == "Z-Score Above":
            st.session_state.alert_engine.add_alert(
                alert_name,
                zscore_above(alert_threshold),
                f"Z-Score exceeded {alert_threshold}"
            )
        elif alert_type == "Z-Score Below":
            st.session_state.alert_engine.add_alert(
                alert_name,
                zscore_below(-alert_threshold),
                f"Z-Score below {-alert_threshold}"
            )
        elif alert_type == "Price Above":
            st.session_state.alert_engine.add_alert(
                alert_name,
                price_above(alert_threshold),
                f"Price exceeded {alert_threshold}"
            )
        elif alert_type == "Price Below":
            st.session_state.alert_engine.add_alert(
                alert_name,
                price_below(alert_threshold),
                f"Price below {alert_threshold}"
            )
        elif alert_type == "Volume Spike":
            st.session_state.alert_engine.add_alert(
                alert_name,
                volume_spike(2.0),
                "Volume spike detected"
            )
        
        st.sidebar.success(f"Alert added: {alert_name}")

# Auto-refresh
refresh_rate = st.sidebar.slider("Refresh Rate (seconds)", 1, 10, 2)

# Main Dashboard
tab1, tab2, tab3, tab4 = st.tabs(["📈 Charts", "📊 Analytics", "🔔 Alerts", "💾 Data Export"])

with tab1:
    st.header("Real-Time Charts")
    
    # Collect latest data
    if mode == "Live Stream":
        for symbol, ws_client in st.session_state.ws_clients.items():
            new_ticks = ws_client.get_ticks()
            if new_ticks:
                # Only insert new ticks since last update
                last_count = len(new_ticks) - 100  # Get last 100
                if last_count > 0:
                    st.session_state.db.insert_ticks(new_ticks[last_count:])
    
    # Display charts for each symbol
    for symbol in symbols[:2]:  # Limit to 2 symbols for layout
        st.subheader(f"{symbol.upper()}")
        
        # Get data from database
        df = st.session_state.db.get_latest_ticks(symbol.upper() if mode == "Live Stream" else symbol, limit=5000)
        
        if df.empty:
            st.warning(f"No data available for {symbol}. Waiting for stream...")
            continue
        
        # Set timestamp as index
        df = df.set_index('timestamp')
        
        # Resample
        try:
            resampled = resample_ticks(df, timeframe)
            
            if resampled.empty:
                st.warning(f"No resampled data for {symbol}")
                continue
            
            # Compute analytics
            resampled['zscore'] = compute_zscore(resampled['price'], window=rolling_window)
            resampled['returns'] = compute_returns(resampled['price'])
            resampled['volatility'] = compute_volatility(resampled['returns'], window=rolling_window)
            
            # Check alerts
            st.session_state.alert_engine.check_alerts(resampled)
            
            # Create subplots
            fig = make_subplots(
                rows=3, cols=1,
                subplot_titles=(f'{symbol.upper()} Price', 'Z-Score', 'Volume'),
                vertical_spacing=0.1,
                row_heights=[0.5, 0.25, 0.25]
            )
            
            # Price chart
            fig.add_trace(
                go.Scatter(
                    x=resampled.index,
                    y=resampled['price'],
                    mode='lines',
                    name='Price',
                    line=dict(color='#00ff00', width=2)
                ),
                row=1, col=1
            )
            
            # Z-Score
            fig.add_trace(
                go.Scatter(
                    x=resampled.index,
                    y=resampled['zscore'],
                    mode='lines',
                    name='Z-Score',
                    line=dict(color='#ff9900', width=2)
                ),
                row=2, col=1
            )
            
            # Add threshold lines
            fig.add_hline(y=2, line_dash="dash", line_color="red", row=2, col=1)
            fig.add_hline(y=-2, line_dash="dash", line_color="red", row=2, col=1)
            fig.add_hline(y=0, line_dash="dot", line_color="gray", row=2, col=1)
            
            # Volume
            fig.add_trace(
                go.Bar(
                    x=resampled.index,
                    y=resampled['volume'],
                    name='Volume',
                    marker_color='#3399ff'
                ),
                row=3, col=1
            )
            
            fig.update_layout(
                height=800,
                showlegend=True,
                hovermode='x unified',
                template='plotly_dark'
            )
            
            fig.update_xaxes(title_text="Time", row=3, col=1)
            fig.update_yaxes(title_text="Price", row=1, col=1)
            fig.update_yaxes(title_text="Z-Score", row=2, col=1)
            fig.update_yaxes(title_text="Volume", row=3, col=1)
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error processing {symbol}: {e}")

with tab2:
    st.header("Statistical Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Summary Statistics")
        
        for symbol in symbols[:2]:
            df = st.session_state.db.get_latest_ticks(symbol.upper() if mode == "Live Stream" else symbol, limit=5000)
            
            if not df.empty:
                df = df.set_index('timestamp')
                resampled = resample_ticks(df, timeframe)
                
                if not resampled.empty:
                    stats = compute_summary_stats(resampled['price'])
                    
                    st.markdown(f"**{symbol.upper()}**")
                    stats_df = pd.DataFrame([stats]).T
                    stats_df.columns = ['Value']
                    st.dataframe(stats_df, use_container_width=True)
    
    with col2:
        st.subheader("ADF Stationarity Test")
        
        for symbol in symbols[:2]:
            df = st.session_state.db.get_latest_ticks(symbol.upper() if mode == "Live Stream" else symbol, limit=5000)
            
            if not df.empty:
                df = df.set_index('timestamp')
                resampled = resample_ticks(df, timeframe)
                
                if not resampled.empty and len(resampled) > 10:
                    adf_result = adf_test(resampled['price'])
                    
                    st.markdown(f"**{symbol.upper()}**")
                    st.metric("Test Statistic", f"{adf_result['statistic']:.4f}" if adf_result['statistic'] else "N/A")
                    st.metric("P-Value", f"{adf_result['pvalue']:.4f}" if adf_result['pvalue'] else "N/A")
                    st.metric(
                        "Result", 
                        "✅ Stationary" if adf_result['is_stationary'] else "❌ Non-stationary",
                        delta=None
                    )
    
    # Pairs Trading Analytics
    if enable_pairs and len(symbols) >= 2:
        st.subheader("Pairs Trading Analysis")
        
        df_y = st.session_state.db.get_latest_ticks(symbol_y.upper() if mode == "Live Stream" else symbol_y, limit=5000)
        df_x = st.session_state.db.get_latest_ticks(symbol_x.upper() if mode == "Live Stream" else symbol_x, limit=5000)
        
        if not df_y.empty and not df_x.empty:
            df_y = df_y.set_index('timestamp')
            df_x = df_x.set_index('timestamp')
            
            res_y = resample_ticks(df_y, timeframe)
            res_x = resample_ticks(df_x, timeframe)
            
            # Align timestamps
            combined = pd.merge(
                res_y[['price']], res_x[['price']], 
                left_index=True, right_index=True, 
                suffixes=('_y', '_x')
            )
            
            if len(combined) > 20:
                pairs = PairsTradingAnalytics(combined['price_y'], combined['price_x'])
                results = pairs.compute_all(window=rolling_window)
                
                # Spread and Z-Score Chart
                fig = make_subplots(
                    rows=2, cols=1,
                    subplot_titles=('Spread', 'Z-Score'),
                    vertical_spacing=0.15
                )
                
                fig.add_trace(
                    go.Scatter(x=results.index, y=results['spread'], mode='lines', name='Spread'),
                    row=1, col=1
                )
                
                fig.add_trace(
                    go.Scatter(x=results.index, y=results['zscore'], mode='lines', name='Z-Score'),
                    row=2, col=1
                )
                
                fig.add_hline(y=2, line_dash="dash", line_color="red", row=2, col=1)
                fig.add_hline(y=-2, line_dash="dash", line_color="red", row=2, col=1)
                
                fig.update_layout(height=600, template='plotly_dark')
                st.plotly_chart(fig, use_container_width=True)
                
                # Display metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Hedge Ratio", f"{pairs.hedge_ratio:.4f}")
                
                with col2:
                    adf = pairs.adf_test()
                    st.metric("ADF P-Value", f"{adf['p_value']:.4f}" if adf['p_value'] else "N/A")
                
                with col3:
                    corr = results['correlation'].iloc[-1]
                    st.metric("Current Correlation", f"{corr:.4f}" if not pd.isna(corr) else "N/A")

with tab3:
    st.header("Alert Monitor")
    
    triggered = st.session_state.alert_engine.get_triggered_alerts(limit=20)
    
    if triggered:
        alert_df = pd.DataFrame(triggered)
        st.dataframe(alert_df, use_container_width=True)
    else:
        st.info("No alerts triggered yet")
    
    if st.button("Clear Alert History"):
        st.session_state.alert_engine.clear_alerts()
        st.success("Alerts cleared")

with tab4:
    st.header("Data Export")
    
    export_symbol = st.selectbox("Select Symbol for Export", symbols)
    export_format = st.radio("Format", ["CSV", "Parquet"])
    
    if st.button("Download Data"):
        df_export = st.session_state.db.get_latest_ticks(
            export_symbol.upper() if mode == "Live Stream" else export_symbol,
            limit=10000
        )
        
        if not df_export.empty:
            if export_format == "CSV":
                csv = df_export.to_csv(index=False)
                st.download_button(
                    "Download CSV",
                    csv,
                    file_name=f"{export_symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                parquet = df_export.to_parquet(index=False)
                st.download_button(
                    "Download Parquet",
                    parquet,
                    file_name=f"{export_symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.parquet",
                    mime="application/octet-stream"
                )
        else:
            st.warning("No data to export")

# Footer with status
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Active Streams", len(st.session_state.ws_clients))

with col2:
    total_ticks = sum(len(ws.get_ticks()) for ws in st.session_state.ws_clients.values())
    st.metric("Total Ticks Collected", total_ticks)

with col3:
    st.metric("Last Update", datetime.now().strftime("%H:%M:%S"))

# Auto-refresh
time.sleep(refresh_rate)
st.rerun()
