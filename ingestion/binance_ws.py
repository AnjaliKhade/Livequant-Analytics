import asyncio
import json
import websockets
from datetime import datetime


async def stream_trades(symbol: str, tick_buffer: list):
    """
    Connects to Binance Futures WebSocket and streams trade ticks.
    """

    url = f"wss://fstream.binance.com/ws/{symbol}@trade"
    print(f"Connecting to {url}")

    async with websockets.connect(url) as ws:
        async for message in ws:
            data = json.loads(message)

            tick = {
                "timestamp": datetime.utcfromtimestamp(data["T"] / 1000),
                "symbol": data["s"],
                "price": float(data["p"]),
                "qty": float(data["q"]),
            }

            tick_buffer.append(tick)


            if len(tick_buffer) % 10 == 0:
                print(tick)

                


if __name__ == "__main__":
    ticks = []
    asyncio.run(stream_trades("btcusdt", ticks))
