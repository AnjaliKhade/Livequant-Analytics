import pandas as pd


def ticks_to_dataframe(ticks: list) -> pd.DataFrame:
    """
    Convert list of tick dictionaries to pandas DataFrame.
    """

    if not ticks:
        return pd.DataFrame()

    df = pd.DataFrame(ticks)
    df = df.set_index("timestamp")
    df = df.sort_index()

    return df
