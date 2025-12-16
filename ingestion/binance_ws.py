import asyncio
import json
import websockets
from datetime import datetime
import threading


class BinanceWebSocket:
    """
    Thread-safe Binance WebSocket client that runs in background.
    """
    
    def __init__(self):
        self.ticks = []
        self.running = False
        self.thread = None
        self.loop = None
        
    def start(self, symbol: str):
        """Start WebSocket in background thread"""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run, args=(symbol,), daemon=True)
        self.thread.start()
        
    def _run(self, symbol: str):
        """Run async event loop in thread"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._stream_trades(symbol))
        
    async def _stream_trades(self, symbol: str):
        """Connect to Binance WebSocket and stream trades"""
        url = f"wss://fstream.binance.com/ws/{symbol}@trade"
        print(f"Connecting to {url}")
        
        try:
            async with websockets.connect(url) as ws:
                async for message in ws:
                    if not self.running:
                        break
                        
                    data = json.loads(message)
                    tick = {
                        "timestamp": datetime.utcfromtimestamp(data["T"] / 1000),
                        "symbol": data["s"],
                        "price": float(data["p"]),
                        "qty": float(data["q"]),
                    }
                    self.ticks.append(tick)
                    
                    if len(self.ticks) % 100 == 0:
                        print(f"Collected {len(self.ticks)} ticks")
        except Exception as e:
            print(f"WebSocket error: {e}")
            
    def get_ticks(self):
        """Get all collected ticks"""
        return self.ticks.copy()
    
    def stop(self):
        """Stop WebSocket"""
        self.running = False


async def stream_trades(symbol: str, tick_buffer: list):
    """
    Legacy function for backward compatibility.
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
