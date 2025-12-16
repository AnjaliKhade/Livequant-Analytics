import pandas as pd
import numpy as np
from statsmodels.regression.linear_model import OLS
from statsmodels.tools import add_constant
from statsmodels.tsa.stattools import adfuller
from scipy import stats as scipy_stats


def compute_spread(price1, price2, hedge_ratio=None):
    """
    Compute spread between two price series.
    
    Args:
        price1: First price series
        price2: Second price series
        hedge_ratio: Optional hedge ratio (if None, use 1:1)
    """
    if hedge_ratio is None:
        return price1 - price2
    return price1 - hedge_ratio * price2


def compute_zscore(series, window=None):
    """
    Compute z-score (rolling or full series).
    
    Args:
        series: Price or spread series
        window: Rolling window size (None for full series)
    """
    if series is None or len(series) == 0:
        return pd.Series()
    
    if window:
        mean = series.rolling(window=window).mean()
        std = series.rolling(window=window).std()
    else:
        mean = series.mean()
        std = series.std()
    
    return (series - mean) / std


def rolling_corr(series1, series2, window=10):
    """Compute rolling correlation"""
    return series1.rolling(window).corr(series2)


def hedge_ratio(price_y, price_x):
    """
    Compute OLS hedge ratio.
    
    Args:
        price_y: Dependent variable
        price_x: Independent variable
        
    Returns:
        Hedge ratio (beta)
    """
    # Remove NaN values
    mask = ~(price_y.isna() | price_x.isna())
    y = price_y[mask]
    x = price_x[mask]
    
    if len(x) < 2:
        return 1.0
    
    x_with_const = add_constant(x)
    model = OLS(y, x_with_const).fit()
    return model.params[1]


def adf_test(series, maxlag=1):
    """
    Augmented Dickey-Fuller test for stationarity.
    
    Returns:
        Dictionary with test results
    """
    series_clean = series.dropna()
    
    if len(series_clean) < 10:
        return {
            'statistic': None,
            'pvalue': None,
            'critical_values': {},
            'is_stationary': False
        }
    
    result = adfuller(series_clean, maxlag=maxlag)
    
    return {
        'statistic': result[0],
        'pvalue': result[1],
        'critical_values': result[4],
        'is_stationary': result[1] < 0.05
    }


def compute_returns(prices):
    """Compute log returns"""
    return np.log(prices / prices.shift(1))


def compute_volatility(returns, window=20):
    """Compute rolling volatility (annualized)"""
    return returns.rolling(window).std() * np.sqrt(252)


def sharpe_ratio(returns, risk_free_rate=0.0):
    """
    Compute Sharpe ratio.
    
    Args:
        returns: Return series
        risk_free_rate: Annual risk-free rate
    """
    excess_returns = returns - risk_free_rate / 252
    return np.sqrt(252) * excess_returns.mean() / returns.std()


def max_drawdown(prices):
    """
    Compute maximum drawdown.
    
    Returns:
        Maximum drawdown as percentage
    """
    cumulative = (1 + prices.pct_change()).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    return drawdown.min()


def compute_summary_stats(series):
    """
    Compute comprehensive summary statistics.
    
    Returns:
        Dictionary with statistics
    """
    return {
        'count': len(series),
        'mean': series.mean(),
        'std': series.std(),
        'min': series.min(),
        'max': series.max(),
        'median': series.median(),
        'skew': scipy_stats.skew(series.dropna()),
        'kurtosis': scipy_stats.kurtosis(series.dropna())
    }

