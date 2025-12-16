import pandas as pd
from datetime import datetime
from typing import Callable, Dict, List


class Alert:
    """Alert definition"""
    
    def __init__(self, name: str, condition: Callable, message: str):
        self.name = name
        self.condition = condition  # Function that returns True when alert triggers
        self.message = message
        self.triggered_at = None
        self.active = True
        
    def check(self, data: pd.DataFrame) -> bool:
        """Check if alert condition is met"""
        if not self.active or data.empty:
            return False
            
        try:
            if self.condition(data):
                self.triggered_at = datetime.now()
                return True
        except Exception as e:
            print(f"Alert {self.name} error: {e}")
            
        return False


class AlertEngine:
    """Manages and evaluates alerts"""
    
    def __init__(self):
        self.alerts: Dict[str, Alert] = {}
        self.triggered_alerts: List[Dict] = []
        
    def add_alert(self, name: str, condition: Callable, message: str):
        """Add a new alert"""
        self.alerts[name] = Alert(name, condition, message)
        
    def remove_alert(self, name: str):
        """Remove an alert"""
        if name in self.alerts:
            del self.alerts[name]
            
    def check_alerts(self, data: pd.DataFrame):
        """Check all alerts against current data"""
        for alert in self.alerts.values():
            if alert.check(data):
                self.triggered_alerts.append({
                    'name': alert.name,
                    'message': alert.message,
                    'timestamp': alert.triggered_at
                })
                alert.active = False  # One-time trigger
                
    def get_triggered_alerts(self, limit=10):
        """Get recent triggered alerts"""
        return self.triggered_alerts[-limit:]
    
    def clear_alerts(self):
        """Clear triggered alerts history"""
        self.triggered_alerts = []
        
    def reset_alert(self, name: str):
        """Reactivate an alert"""
        if name in self.alerts:
            self.alerts[name].active = True
            self.alerts[name].triggered_at = None


# Predefined alert conditions
def zscore_above(threshold: float):
    """Alert when z-score exceeds threshold"""
    def condition(data: pd.DataFrame) -> bool:
        if 'zscore' not in data.columns or data['zscore'].empty:
            return False
        return data['zscore'].iloc[-1] > threshold
    return condition


def zscore_below(threshold: float):
    """Alert when z-score below threshold"""
    def condition(data: pd.DataFrame) -> bool:
        if 'zscore' not in data.columns or data['zscore'].empty:
            return False
        return data['zscore'].iloc[-1] < threshold
    return condition


def price_above(threshold: float):
    """Alert when price exceeds threshold"""
    def condition(data: pd.DataFrame) -> bool:
        if 'price' not in data.columns or data['price'].empty:
            return False
        return data['price'].iloc[-1] > threshold
    return condition


def price_below(threshold: float):
    """Alert when price below threshold"""
    def condition(data: pd.DataFrame) -> bool:
        if 'price' not in data.columns or data['price'].empty:
            return False
        return data['price'].iloc[-1] < threshold
    return condition


def volume_spike(multiplier: float = 2.0):
    """Alert when volume spikes above rolling average"""
    def condition(data: pd.DataFrame) -> bool:
        if 'volume' not in data.columns or len(data) < 10:
            return False
        avg_volume = data['volume'].iloc[-10:-1].mean()
        current_volume = data['volume'].iloc[-1]
        return current_volume > avg_volume * multiplier
    return condition
