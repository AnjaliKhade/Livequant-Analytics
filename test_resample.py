from ingestion.binance_ws import stream_trades
from storage.store import ticks_to_dataframe
from analytics.resample import resample_ticks
import asyncio
import time

ticks = []

async def collect():
    task = asyncio.create_task(stream_trades("btcusdt", ticks))
    await asyncio.sleep(10)
    task.cancel()

asyncio.run(collect())

df = ticks_to_dataframe(ticks)
print("Raw ticks:")
print(df.head())

bars = resample_ticks(df, "1m")
print("\nResampled 1m bars:")
print(bars.tail())
