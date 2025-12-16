import pandas as pd
import duckdb
import os


class TickStore:
    """
    DuckDB-based storage for tick data with efficient querying.
    """
    
    def __init__(self, db_path="data/ticks.db"):
        """Initialize DuckDB connection"""
        # Create directory if needed
        db_dir = os.path.dirname(db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        
        # Use shared connection to avoid locking issues
        self.db_path = db_path
        self.conn = duckdb.connect(db_path, read_only=False)
        self._create_tables()
        
    def _create_tables(self):
        """Create tick data table"""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS ticks (
                timestamp TIMESTAMP,
                symbol VARCHAR,
                price DOUBLE,
                qty DOUBLE
            )
        """)
        
    def insert_ticks(self, ticks: list):
        """Insert list of tick dictionaries"""
        if not ticks:
            return
            
        df = pd.DataFrame(ticks)
        self.conn.execute("INSERT INTO ticks SELECT * FROM df")
        
    def get_ticks(self, symbol=None, start_time=None, end_time=None):
        """Query ticks with optional filters"""
        query = "SELECT * FROM ticks WHERE 1=1"
        
        if symbol:
            query += f" AND symbol = '{symbol}'"
        if start_time:
            query += f" AND timestamp >= '{start_time}'"
        if end_time:
            query += f" AND timestamp <= '{end_time}'"
            
        query += " ORDER BY timestamp"
        
        return self.conn.execute(query).df()
    
    def get_latest_ticks(self, symbol, limit=1000):
        """Get most recent ticks for a symbol"""
        query = f"""
            SELECT * FROM ticks 
            WHERE symbol = '{symbol}'
            ORDER BY timestamp DESC 
            LIMIT {limit}
        """
        df = self.conn.execute(query).df()
        return df.sort_values('timestamp')
    
    def clear_old_data(self, days=1):
        """Delete data older than N days"""
        self.conn.execute(f"""
            DELETE FROM ticks 
            WHERE timestamp < NOW() - INTERVAL '{days} days'
        """)
        
    def get_symbols(self):
        """Get list of all symbols in database"""
        result = self.conn.execute("SELECT DISTINCT symbol FROM ticks").fetchall()
        return [row[0] for row in result]


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
