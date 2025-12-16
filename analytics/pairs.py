import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import adfuller
from statsmodels.regression.linear_model import OLS
from statsmodels.tools import add_constant


class PairsTradingAnalytics:
    """
    Analytics for pairs trading and statistical arbitrage.
    """
    
    def __init__(self, price_y: pd.Series, price_x: pd.Series):
        """
        Initialize with two price series.
        
        Args:
            price_y: Dependent variable (e.g., ETH)
            price_x: Independent variable (e.g., BTC)
        """
        self.price_y = price_y
        self.price_x = price_x
        self.hedge_ratio = None
        self.spread = None
        self.zscore = None
        
    def compute_hedge_ratio(self):
        """Compute OLS hedge ratio"""
        x = add_constant(self.price_x)
        model = OLS(self.price_y, x).fit()
        self.hedge_ratio = model.params[1]
        return self.hedge_ratio
    
    def compute_spread(self):
        """Compute spread using hedge ratio"""
        if self.hedge_ratio is None:
            self.compute_hedge_ratio()
        self.spread = self.price_y - self.hedge_ratio * self.price_x
        return self.spread
    
    def compute_zscore(self, window=20):
        """Compute rolling z-score of spread"""
        if self.spread is None:
            self.compute_spread()
            
        mean = self.spread.rolling(window=window).mean()
        std = self.spread.rolling(window=window).std()
        self.zscore = (self.spread - mean) / std
        return self.zscore
    
    def adf_test(self, spread=None):
        """
        Augmented Dickey-Fuller test for stationarity.
        
        Returns:
            dict with test statistic, p-value, and interpretation
        """
        if spread is None:
            if self.spread is None:
                self.compute_spread()
            spread = self.spread
            
        # Remove NaN values
        spread_clean = spread.dropna()
        
        if len(spread_clean) < 10:
            return {
                'test_statistic': None,
                'p_value': None,
                'is_stationary': False,
                'message': 'Insufficient data for ADF test'
            }
        
        result = adfuller(spread_clean, maxlag=1)
        
        return {
            'test_statistic': result[0],
            'p_value': result[1],
            'critical_values': result[4],
            'is_stationary': result[1] < 0.05,  # 5% significance level
            'message': 'Stationary' if result[1] < 0.05 else 'Non-stationary'
        }
    
    def rolling_correlation(self, window=20):
        """Compute rolling correlation between two series"""
        return self.price_y.rolling(window).corr(self.price_x)
    
    def compute_all(self, window=20):
        """
        Compute all analytics and return as DataFrame.
        
        Returns:
            DataFrame with spread, z-score, correlation
        """
        self.compute_hedge_ratio()
        self.compute_spread()
        zscore = self.compute_zscore(window)
        correlation = self.rolling_correlation(window)
        
        df = pd.DataFrame({
            'price_y': self.price_y,
            'price_x': self.price_x,
            'spread': self.spread,
            'zscore': zscore,
            'correlation': correlation
        })
        
        return df


def generate_trading_signals(zscore: pd.Series, entry_threshold=2.0, exit_threshold=0.5):
    """
    Generate simple mean-reversion trading signals.
    
    Args:
        zscore: Z-score series
        entry_threshold: Enter position when |zscore| > this
        exit_threshold: Exit position when |zscore| < this
        
    Returns:
        DataFrame with signals (-1: short, 0: neutral, 1: long)
    """
    signals = pd.Series(0, index=zscore.index)
    position = 0
    
    for i in range(len(zscore)):
        z = zscore.iloc[i]
        
        # Entry logic
        if position == 0:
            if z > entry_threshold:
                position = -1  # Short (mean reversion)
            elif z < -entry_threshold:
                position = 1   # Long
                
        # Exit logic
        elif position != 0:
            if abs(z) < exit_threshold:
                position = 0
                
        signals.iloc[i] = position
    
    return signals
