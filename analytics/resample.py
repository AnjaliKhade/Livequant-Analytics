import pandas as pd


def resample_ticks(df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
    """
    Resample tick data into time bars.

    timeframe: '1s', '1min', '5min'
    """

    if df.empty:
        return df

    rule_map = {
        "1s": "1S",
        "1m": "1min",
        "5m": "5min",
    }

    rule = rule_map.get(timeframe)
    if rule is None:
        raise ValueError("Invalid timeframe")

    resampled = df.resample(rule).agg(
        price=("price", "last"),
        volume=("qty", "sum"),
    )

    return resampled.dropna()
