from loguru import logger
from kopernicus.config.settings import settings
from typing import Dict, Any

class RiskManager:
    """Manages position sizing and risk controls"""
    
    def __init__(self):
        self.capital = settings.capital_usdt
        self.max_position_size_pct = settings.max_position_size_pct
        self.leverage = settings.leverage
        self.stop_loss_pct = settings.stop_loss_pct
    
    def calculate_position_size(self, price: float) -> float:
        """
        Calculate position size in base currency (e.g., BTC)
        
        Formula: 
        Position Size = (Capital * Max% * Leverage) / Price
        """
        max_notional = self.capital * (self.max_position_size_pct / 100) * self.leverage
        quantity = max_notional / price
        
        # Round to reasonable precision (0.001 for BTC)
        quantity = round(quantity, 3)
        
        logger.debug(f"Position size: {quantity} @ ${price} = ${quantity * price} notional")
        return quantity
    
    def should_close_position(self, position: Dict[str, Any]) -> bool:
        """Check if position should be closed due to risk limits"""
        unrealized_pnl = float(position.get('unRealizedProfit', 0))
        entry_price = float(position.get('entryPrice', 0))
        
        if entry_price == 0:
            return False
        
        pnl_pct = (unrealized_pnl / (entry_price * float(position['positionAmt']))) * 100
        
        # Stop-loss trigger
        if abs(pnl_pct) > self.stop_loss_pct:
            logger.warning(f"Stop-loss triggered: PnL {pnl_pct:.2f}% exceeds {self.stop_loss_pct}%")
            return True
        
        # Drift check (delta neutrality broken)
        if abs(pnl_pct) > settings.max_pnl_drift_pct:
            logger.warning(f"Position drift: {pnl_pct:.2f}% exceeds {settings.max_pnl_drift_pct}%")
            return True
        
        return False
    
    def get_current_exposure(self, positions: list) -> float:
        """Calculate total notional exposure across all positions"""
        total = sum(
            abs(float(pos['positionAmt'])) * float(pos['entryPrice'])
            for pos in positions
            if float(pos['positionAmt']) != 0
        )
        return total
    
    def can_open_new_position(self, price: float, positions: list) -> bool:
        """Check if we can open a new position without exceeding limits"""
        current_exposure = self.get_current_exposure(positions)
        new_notional = self.calculate_position_size(price) * price
        
        max_total_exposure = self.capital * self.leverage * 0.5  # 50% of max leverage
        
        if (current_exposure + new_notional) > max_total_exposure:
            logger.warning(f"Cannot open position: would exceed max exposure")
            return False
        
        return True

