# Quant Trading Analytics Dashboard

A comprehensive real-time quantitative trading analytics platform built for statistical arbitrage, pairs trading, and market microstructure analysis. This application ingests live tick data from Binance, processes it through a robust analytics pipeline, and presents actionable insights through an interactive dashboard.

## 🎯 Project Overview

This application was developed as a quantitative developer evaluation project, demonstrating end-to-end capabilities in:
- Real-time data ingestion and processing
- Statistical analysis and quantitative finance
- Interactive visualization and UI/UX design
- Modular architecture and software engineering

**Target Use Cases:**
- Statistical arbitrage research
- Pairs trading strategy development
- Market microstructure analysis
- Risk-premia analytics
- Real-time monitoring and alerting

---

## ✨ Features

### 📊 Core Functionality

**Real-Time Data Ingestion**
- WebSocket streaming from Binance Futures
- Thread-safe background data collection
- Support for multiple symbols simultaneously
- Persistent storage using DuckDB

**Data Processing**
- Configurable resampling (1s, 1m, 5m timeframes)
- OHLC aggregation from tick data
- Rolling window analytics
- Upload custom OHLC CSV data

**Quantitative Analytics**
- **Pairs Trading**: OLS hedge ratio, spread calculation, z-score analysis
- **Statistical Tests**: Augmented Dickey-Fuller (ADF) test for stationarity
- **Risk Metrics**: Volatility, returns, correlation analysis
- **Summary Statistics**: Mean, std dev, skewness, kurtosis
- **Trading Signals**: Mean-reversion signal generation

**Interactive Visualization**
- Multi-panel Plotly charts with zoom/pan/hover
- Price charts with volume overlays
- Z-score plots with entry/exit thresholds
- Spread and correlation heatmaps
- Real-time updates with configurable refresh rates

**Alert System**
- Custom alert conditions (z-score, price, volume)
- Real-time monitoring and notifications
- Alert history tracking
- Multiple alert types supported

**Data Export**
- Download processed data (CSV, Parquet)
- Export analytics results
- Historical data retrieval

---

## 🏗️ Architecture

### System Design

```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit Frontend                       │
│  (Interactive Dashboard, Charts, Controls, Alerts)          │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────────┐
│                   Application Layer                          │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │  Analytics  │  │ Alert Engine │  │  Data Export    │   │
│  │   Engine    │  │              │  │                 │   │
│  └─────────────┘  └──────────────┘  └─────────────────┘   │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────────┐
│                   Storage Layer (DuckDB)                     │
│  - Persistent tick storage                                   │
│  - Efficient querying and filtering                         │
│  - Historical data management                               │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────────┐
│              Data Ingestion Layer                            │
│  ┌────────────────────────────────────────────────────┐    │
│  │  BinanceWebSocket (Thread-based async handler)     │    │
│  │  - Multi-symbol support                            │    │
│  │  - Thread-safe tick buffer                         │    │
│  │  - Auto-reconnect logic                            │    │
│  └────────────────────────────────────────────────────┘    │
└──────────────────────┬──────────────────────────────────────┘
                       │
                  Binance API
           (wss://fstream.binance.com)
```

### Module Structure

```
Quant_app/
├── app.py                    # Main Streamlit dashboard
├── requirements.txt          # Python dependencies
├── README.md                 # This file
│
├── ingestion/
│   └── binance_ws.py        # WebSocket client (threaded)
│
├── storage/
│   └── store.py             # DuckDB storage layer
│
├── analytics/
│   ├── resample.py          # Time-based resampling
│   ├── stats.py             # Statistical functions
│   └── pairs.py             # Pairs trading analytics
│
└── alerts/
    └── alert_engine.py      # Alert management system
```

### Design Principles

1. **Loose Coupling**: Each module has clear interfaces and minimal dependencies
2. **Extensibility**: Easy to add new data sources, analytics, or visualizations
3. **Scalability**: Thread-based WebSocket handling allows multi-symbol scaling
4. **Maintainability**: Clean code structure with comprehensive documentation
5. **Performance**: DuckDB for fast querying, efficient resampling algorithms

---

## 🚀 Installation & Setup

### Prerequisites

- Python 3.8+
- pip package manager
- Internet connection (for live data streaming)

### Quick Start

```bash
# 1. Clone the repository
git clone <repository-url>
cd Quant_app

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
streamlit run app.py
```

The dashboard will open automatically in your browser at `http://localhost:8501`.

### Dependencies

```
streamlit              # Web framework
streamlit-autorefresh  # Auto-refresh functionality
pandas                 # Data manipulation
numpy                  # Numerical computing
plotly                 # Interactive charts
websockets             # WebSocket client
statsmodels            # Statistical analysis
duckdb                 # Embedded database
scikit-learn           # Machine learning utilities
scipy                  # Scientific computing
```

---

## 📖 User Guide

### Getting Started

1. **Select Data Source**
   - Choose "Live Stream" for real-time Binance data
   - Or "Upload OHLC" to analyze your own CSV data

2. **Configure Symbols**
   - Enter symbols (e.g., `btcusdt,ethusdt`)
   - Streams start automatically

3. **Set Analytics Parameters**
   - Resample timeframe: 1s, 1m, or 5m
   - Rolling window: 5-100 periods
   - Enable pairs trading for spread analysis

4. **Monitor Charts**
   - Real-time price, z-score, and volume
   - Interactive zoom/pan/hover

5. **Configure Alerts**
   - Set z-score thresholds
   - Price breakout alerts
   - Volume spike detection

6. **Export Data**
   - Download as CSV or Parquet
   - Export resampled or raw data

### Using Uploaded Data

CSV format:
```csv
timestamp,symbol,open,high,low,close,volume
2024-12-16 10:00:00,BTC,50000,51000,49500,50500,1000
2024-12-16 10:01:00,BTC,50500,50800,50200,50600,800
```

### Pairs Trading Workflow

1. Enable "Pairs Trading" in sidebar
2. Select Symbol Y (dependent) and Symbol X (independent)
3. View spread, z-score, and correlation
4. Check ADF test for stationarity
5. Use z-score for entry/exit signals (|z| > 2 = entry, |z| < 0.5 = exit)

---

## 🧮 Analytics Methodology

### Resampling
- Tick data aggregated into OHLC bars
- Last price for close, sum for volume
- Time-based indexing with configurable intervals

### Z-Score Calculation
```
z = (x - μ) / σ
```
Where μ and σ are computed over rolling window

### Hedge Ratio (OLS)
```
Y = α + β*X + ε
```
Hedge ratio β estimated via ordinary least squares

### Spread
```
Spread = Price_Y - β * Price_X
```

### ADF Test
- Null hypothesis: Series has unit root (non-stationary)
- Reject if p-value < 0.05
- Critical for pairs trading validation

### Statistical Summary
- Mean, standard deviation, min/max
- Skewness (distribution asymmetry)
- Kurtosis (tail heaviness)

---

## 🔧 Advanced Configuration

### Custom Timeframes

Edit `analytics/resample.py`:
```python
rule_map = {
    "1s": "1S",
    "1m": "1min",
    "5m": "5min",
    "15m": "15min",  # Add custom timeframe
}
```

### Custom Alerts

Create custom alert conditions in `alerts/alert_engine.py`:
```python
def custom_condition(threshold):
    def condition(data: pd.DataFrame) -> bool:
        # Your logic here
        return data['metric'].iloc[-1] > threshold
    return condition
```

### Database Location

Change DuckDB path in `app.py`:
```python
st.session_state.db = TickStore(db_path="custom/path/ticks.db")
```

---

## 🎨 Architecture Decisions

### Why DuckDB?
- **Embedded**: No separate server required
- **Fast**: Columnar storage optimized for analytics
- **SQL**: Familiar query interface
- **Portability**: Single file database

### Why Threading for WebSocket?
- **Streamlit Compatibility**: Avoids asyncio event loop conflicts
- **Simplicity**: Easier to manage than multiprocessing
- **Performance**: Sufficient for tick data rates

### Why Streamlit?
- **Rapid Development**: Fast prototyping
- **Interactive**: Built-in widgets and charts
- **Python-Native**: Seamless integration with analytics code

### Trade-offs
- **Scalability**: Thread-based approach limits to ~10 symbols
- **Latency**: ~500ms refresh rate (not sub-millisecond HFT)
- **Storage**: DuckDB limited to single machine (not distributed)

**Future Improvements:**
- Redis for ultra-low latency
- Microservices architecture for scaling
- WebSocket → Kafka for production-grade ingestion

---

## 🧪 Testing

Run the test script:
```bash
python test_resample.py
```

This verifies:
- WebSocket connectivity
- Tick collection
- Resampling logic

---

## 📊 Sample Use Cases

### 1. BTC/ETH Pairs Trading
```
1. Set symbols: btcusdt,ethusdt
2. Enable pairs trading
3. Symbol Y: ethusdt, Symbol X: btcusdt
4. Monitor z-score > 2 for mean reversion entries
```

### 2. Price Breakout Alert
```
1. Set alert type: "Price Above"
2. Threshold: 51000
3. Monitor alert tab for triggers
```

### 3. Volatility Analysis
```
1. Set 1m timeframe
2. View Analytics tab
3. Check volatility metrics and returns
```

---

## 🤖 AI Usage Transparency

This project utilized GitHub Copilot and ChatGPT for:

**Code Generation (40%)**
- Boilerplate WebSocket client
- Plotly chart templates
- Alert engine structure

**Debugging (20%)**
- Streamlit + asyncio compatibility issues
- DuckDB query optimization
- Pandas resampling edge cases

**Documentation (30%)**
- README structure and formatting
- Docstring improvements
- Architecture diagram suggestions

**Research (10%)**
- ADF test implementation details
- Pairs trading best practices
- DuckDB syntax lookups

**Key Prompts Used:**
- "Create thread-safe WebSocket client for Binance that works with Streamlit"
- "Implement pairs trading analytics with OLS hedge ratio and ADF test"
- "Design alert system with custom condition functions"
- "Generate comprehensive README for quant trading dashboard"

All AI-generated code was reviewed, tested, and modified to ensure correctness and alignment with project requirements.

---

## 🚧 Known Limitations

1. **Data Retention**: No automatic cleanup (manual via DuckDB)
2. **Error Handling**: Limited WebSocket reconnection logic
3. **Scalability**: Single-machine, limited to ~10 concurrent symbols
4. **Latency**: Not suitable for ultra-low latency HFT
5. **Backtesting**: No historical simulation framework included

---

## 🔮 Future Enhancements

- [ ] Kalman Filter for dynamic hedge estimation
- [ ] Robust regression (Huber, Theil-Sen)
- [ ] Simple backtesting engine
- [ ] Cross-correlation heatmaps
- [ ] Liquidity filters (bid-ask spread analysis)
- [ ] Multi-timeframe analysis
- [ ] Machine learning signal generation
- [ ] REST API for programmatic access
- [ ] Docker containerization

---

## 📄 License

This project is for educational and evaluation purposes.

---

## 👤 Author

**Assignment Submission**
- Developed as part of Quant Developer Evaluation
- Demonstrates end-to-end quant analytics capabilities
- Focus: Clean architecture, statistical rigor, user experience

---

## 📞 Support

For issues or questions:
1. Check this README
2. Review code comments and docstrings
3. Test with sample data upload first
4. Verify internet connection for live streams

---

**Happy Trading! 📈**
