"""
Utility functions for Micro-Cap AI Agent 2.5
Common helper functions used across modules
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json

def format_currency(value: float, decimals: int = 2) -> str:
    """Format value as currency"""
    if value >= 1_000_000_000:
        return f"${value/1_000_000_000:.2f}B"
    elif value >= 1_000_000:
        return f"${value/1_000_000:.2f}M"
    elif value >= 1_000:
        return f"${value/1_000:.2f}K"
    else:
        return f"${value:.{decimals}f}"

def format_percent(value: float, decimals: int = 1) -> str:
    """Format value as percentage"""
    return f"{value*100:.{decimals}f}%"

def format_number(value: float, decimals: int = 0) -> str:
    """Format number with thousands separator"""
    if decimals == 0:
        return f"{value:,.0f}"
    else:
        return f"{value:,.{decimals}f}"

def is_market_hours(check_time: Optional[datetime] = None) -> bool:
    """Check if current time is during market hours (EST)"""
    if check_time is None:
        check_time = datetime.now()
    
    # Simple check (would need timezone handling in production)
    hour = check_time.hour
    minute = check_time.minute
    weekday = check_time.weekday()
    
    # Monday-Friday
    if weekday >= 5:
        return False
    
    # 9:30 AM - 4:00 PM EST
    if hour < 9 or hour >= 16:
        return False
    if hour == 9 and minute < 30:
        return False
    
    return True

def is_premarket_hours(check_time: Optional[datetime] = None) -> bool:
    """Check if current time is during premarket hours"""
    if check_time is None:
        check_time = datetime.now()
    
    hour = check_time.hour
    minute = check_time.minute
    weekday = check_time.weekday()
    
    # Monday-Friday
    if weekday >= 5:
        return False
    
    # 4:00 AM - 9:30 AM EST
    if hour < 4 or hour >= 9:
        return False
    if hour == 9 and minute >= 30:
        return False
    
    return True

def calculate_returns(prices: List[float]) -> List[float]:
    """Calculate returns from price series"""
    if len(prices) < 2:
        return []
    
    returns = []
    for i in range(1, len(prices)):
        if prices[i-1] != 0:
            ret = (prices[i] - prices[i-1]) / prices[i-1]
            returns.append(ret)
        else:
            returns.append(0.0)
    
    return returns

def calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.02) -> float:
    """Calculate Sharpe ratio"""
    if not returns or len(returns) < 2:
        return 0.0
    
    returns_array = np.array(returns)
    excess_returns = returns_array - (risk_free_rate / 252)  # Daily risk-free rate
    
    if np.std(excess_returns) == 0:
        return 0.0
    
    sharpe = np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)
    return sharpe

def calculate_max_drawdown(prices: List[float]) -> float:
    """Calculate maximum drawdown"""
    if len(prices) < 2:
        return 0.0
    
    prices_array = np.array(prices)
    cumulative_max = np.maximum.accumulate(prices_array)
    drawdowns = (prices_array - cumulative_max) / cumulative_max
    
    return abs(np.min(drawdowns))

def normalize_symbol(symbol: str) -> str:
    """Normalize stock symbol (uppercase, trim)"""
    if not symbol:
        return ""
    return symbol.strip().upper()

def validate_symbol(symbol: str) -> bool:
    """Validate stock symbol format"""
    if not symbol or len(symbol) > 5:
        return False
    
    # Check if alphanumeric
    if not symbol.isalpha():
        return False
    
    return True

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safe division with default value"""
    if denominator == 0:
        return default
    return numerator / denominator

def calculate_position_value(shares: int, price: float) -> float:
    """Calculate position value"""
    return shares * price

def calculate_profit_loss(entry_price: float, exit_price: float, shares: int) -> float:
    """Calculate profit/loss"""
    return (exit_price - entry_price) * shares

def calculate_profit_loss_percent(entry_price: float, exit_price: float) -> float:
    """Calculate profit/loss percentage"""
    if entry_price == 0:
        return 0.0
    return (exit_price - entry_price) / entry_price

def load_json_safe(filepath: str, default: Any = None) -> Any:
    """Safely load JSON file"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception:
        return default if default is not None else {}

def save_json_safe(filepath: str, data: Any) -> bool:
    """Safely save JSON file"""
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving JSON to {filepath}: {e}")
        return False

def merge_dicts(*dicts: Dict) -> Dict:
    """Merge multiple dictionaries"""
    result = {}
    for d in dicts:
        if d:
            result.update(d)
    return result

def get_date_range(days: int = 30) -> tuple:
    """Get date range for historical data"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    return start_date, end_date

def format_timestamp(dt: Optional[datetime] = None, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime as string"""
    if dt is None:
        dt = datetime.now()
    return dt.strftime(format_str)

def parse_timestamp(timestamp_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
    """Parse timestamp string"""
    try:
        return datetime.strptime(timestamp_str, format_str)
    except Exception:
        return None

def clamp(value: float, min_value: float, max_value: float) -> float:
    """Clamp value between min and max"""
    return max(min_value, min(max_value, value))

def moving_average(data: List[float], window: int) -> List[float]:
    """Calculate simple moving average"""
    if len(data) < window:
        return []
    
    result = []
    for i in range(window - 1, len(data)):
        avg = sum(data[i-window+1:i+1]) / window
        result.append(avg)
    
    return result

def exponential_moving_average(data: List[float], window: int) -> List[float]:
    """Calculate exponential moving average"""
    if len(data) < window:
        return []
    
    alpha = 2 / (window + 1)
    ema = [sum(data[:window]) / window]  # Start with SMA
    
    for price in data[window:]:
        ema.append(alpha * price + (1 - alpha) * ema[-1])
    
    return ema

def volatility(returns: List[float], annualize: bool = True) -> float:
    """Calculate volatility"""
    if len(returns) < 2:
        return 0.0
    
    vol = np.std(returns)
    
    if annualize:
        vol *= np.sqrt(252)  # Annualize assuming 252 trading days
    
    return vol

def correlation(series1: List[float], series2: List[float]) -> float:
    """Calculate correlation between two series"""
    if len(series1) != len(series2) or len(series1) < 2:
        return 0.0
    
    return np.corrcoef(series1, series2)[0, 1]

def percentile(data: List[float], percent: float) -> float:
    """Calculate percentile of data"""
    if not data:
        return 0.0
    return np.percentile(data, percent)

def z_score(value: float, mean: float, std: float) -> float:
    """Calculate z-score"""
    if std == 0:
        return 0.0
    return (value - mean) / std

def rank_items(items: List[Dict], key: str, reverse: bool = True) -> List[Dict]:
    """Rank items by a key"""
    return sorted(items, key=lambda x: x.get(key, 0), reverse=reverse)

def filter_items(items: List[Dict], filters: Dict) -> List[Dict]:
    """Filter items based on criteria"""
    filtered = items
    
    for key, condition in filters.items():
        if callable(condition):
            filtered = [item for item in filtered if condition(item.get(key))]
        else:
            filtered = [item for item in filtered if item.get(key) == condition]
    
    return filtered

def group_by(items: List[Dict], key: str) -> Dict[Any, List[Dict]]:
    """Group items by a key"""
    groups = {}
    for item in items:
        group_key = item.get(key, 'unknown')
        if group_key not in groups:
            groups[group_key] = []
        groups[group_key].append(item)
    return groups

def safe_get(dictionary: Dict, *keys, default=None):
    """Safely get nested dictionary value"""
    result = dictionary
    for key in keys:
        if isinstance(result, dict) and key in result:
            result = result[key]
        else:
            return default
    return result

def print_table(data: List[Dict], headers: List[str], max_width: int = 80):
    """Print data as formatted table"""
    if not data:
        print("No data to display")
        return
    
    # Calculate column widths
    col_widths = {h: len(h) for h in headers}
    for row in data:
        for header in headers:
            value = str(row.get(header, ''))
            col_widths[header] = max(col_widths[header], len(value))
    
    # Print header
    header_line = " | ".join(h.ljust(col_widths[h]) for h in headers)
    print(header_line)
    print("-" * len(header_line))
    
    # Print rows
    for row in data:
        row_line = " | ".join(str(row.get(h, '')).ljust(col_widths[h]) for h in headers)
        print(row_line)

# Example usage
if __name__ == "__main__":
    # Test utilities
    print(format_currency(1_234_567))
    print(format_percent(0.1234))
    print(format_number(1234567.89, 2))
    
    prices = [100, 105, 103, 108, 110]
    returns = calculate_returns(prices)
    print(f"Returns: {returns}")
    print(f"Max Drawdown: {calculate_max_drawdown(prices):.2%}")
