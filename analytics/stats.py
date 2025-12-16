import pandas as pd
import numpy as np
from statsmodels.regression.linear_model import OLS
from statsmodels.tools import add_constant

def compute_spread(price1, price2):
    """Compute spread between two price series"""
    return price1 - price2

def compute_zscore(series):
    """Compute rolling z-score"""
    return (series - series.mean()) / series.std()

def rolling_corr(series1, series2, window=10):
    """Compute rolling correlation"""
    return series1.rolling(window).corr(series2)

def hedge_ratio(price_y, price_x):
    """OLS hedge ratio"""
    x = add_constant(price_x)
    model = OLS(price_y, x).fit()
    return model.params[1]
