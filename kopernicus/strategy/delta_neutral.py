from loguru import logger
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import time
import random

from kopernicus.config.settings import settings
from kopernicus.exchange.aster_client import AsterExchangeClient
from kopernicus.strategy.risk_manager import RiskManager
from kopernicus.database.db import get_db
from kopernicus.database.models import Trade, Position

class DeltaNeutralStrategy:
    """
    Hold-and-Rotate Strategy for Aster Genesis Stage 3
    
    Strategy:
    1. Open equal long + short positions (delta-neutral)
    2. Hold for 90+ minutes (10x holding time multiplier)
    3. Close and reopen with slight variations to generate volume
    4. Target: $15K daily volume, $200K weekly holding time equivalent
    """
    
    def __init__(self):
        self.client = AsterExchangeClient()
        self.risk_manager = RiskManager()
        self.symbol = settings.trading_pairs[0]  # Start with BTCUSDT
        
        # Initialize leverage
        self.client.set_leverage(self.symbol, settings.leverage)
        
        # Strategy state
        self.active_positions: Dict[str, Dict] = {}  # position_side -> position data
        self.last_rotation_time: Optional[datetime] = None
    
    def run_cycle(self):
        """
        Main strategy loop - call this periodically (e.g., every 10 minutes)
        """
        logger.info("=" * 50)
        logger.info("Running strategy cycle...")
        
        try:
            # Step 1: Check current positions
            positions = self.client.get_position_risk(symbol=self.symbol)
            self._update_active_positions(positions)
            
            # Step 2: Risk check - close if needed
            self._check_and_close_risky_positions(positions)
            
            # Step 3: Decide action based on state
            if self._should_open_new_positions():
                self._open_delta_neutral_pair()
            elif self._should_rotate_positions():
                self._rotate_positions()
            else:
                logger.info("Holding current positions...")
                self._log_position_status()
            
            # Step 4: Log stats
            self._log_daily_stats()
            
        except Exception as e:
            logger.error(f"Strategy cycle error: {e}")
            raise
    
    def _should_open_new_positions(self) -> bool:
        """Check if we should open new delta-neutral positions"""
        # No active positions
        if not self.active_positions or all(
            not pos.get('is_active', False) for pos in self.active_positions.values()
        ):
            return True
        
        return False
    
    def _should_rotate_positions(self) -> bool:
        """Check if it's time to rotate (close and reopen) positions"""
        if not self.active_positions:
            return False
        
        # Check if we've held for minimum time
        for position_side, pos_data in self.active_positions.items():
            if not pos_data.get('is_active'):
                continue
            
            opened_at = pos_data.get('opened_at')
            if not opened_at:
                continue
            
            hold_time = datetime.utcnow() - opened_at
            if hold_time.total_seconds() / 60 < settings.position_hold_time_min:
                logger.info(f"Position {position_side} held for {hold_time.total_seconds()/60:.1f} min, need {settings.position_hold_time_min} min")
                return False
        
        # All positions have been held long enough
        logger.info("All positions held for minimum time - ready to rotate")
        return True
    
    def _open_delta_neutral_pair(self):
        """Open equal long and short positions"""
        logger.info("Opening new delta-neutral position pair...")
        
        # Get current price
        price = self.client.get_mark_price(self.symbol)
        
        # Calculate position size
        quantity = self.risk_manager.calculate_position_size(price)
        
        # Add slight randomization (±5%) to avoid wash trading detection
        quantity = quantity * random.uniform(0.95, 1.05)
        quantity = round(quantity, 3)
        
        try:
            # Open LONG position
            long_order = self.client.place_market_order(
                symbol=self.symbol,
                side="BUY",
                quantity=quantity,
                position_side="LONG"
            )
            
            # Small delay to appear natural
            time.sleep(random.uniform(2, 5))
            
            # Open SHORT position
            short_order = self.client.place_market_order(
                symbol=self.symbol,
                side="SELL",
                quantity=quantity,
                position_side="SHORT"
            )
            
            # Record in database
            opened_at = datetime.utcnow()
            with get_db() as db:
                for order, pos_side in [(long_order, "LONG"), (short_order, "SHORT")]:
                    trade = Trade(
                        symbol=self.symbol,
                        side=order['side'],
                        position_side=pos_side,
                        quantity=float(order['executedQty']),
                        price=float(order['avgPrice']),
                        notional=float(order['executedQty']) * float(order['avgPrice']),
                        order_id=str(order['orderId']),
                        commission=float(order.get('commission', 0))
                    )
                    db.add(trade)
                    
                    position = Position(
                        symbol=self.symbol,
                        position_side=pos_side,
                        entry_price=float(order['avgPrice']),
                        quantity=float(order['executedQty']),
                        leverage=settings.leverage,
                        notional=float(order['executedQty']) * float(order['avgPrice']),
                        is_active=True
                    )
                    db.add(position)
            
            # Update state
            self.active_positions = {
                "LONG": {"opened_at": opened_at, "is_active": True, "entry_price": float(long_order['avgPrice'])},
                "SHORT": {"opened_at": opened_at, "is_active": True, "entry_price": float(short_order['avgPrice'])}
            }
            
            logger.success(f"✅ Delta-neutral pair opened: {quantity} BTC @ ${price}")
            
        except Exception as e:
            logger.error(f"Failed to open positions: {e}")
            raise
    
    def _rotate_positions(self):
        """Close current positions and open new ones"""
        logger.info("Rotating positions...")
        
        try:
            # Close existing positions
            for position_side in ["LONG", "SHORT"]:
                close_result = self.client.close_position(self.symbol, position_side)
                if close_result:
                    logger.info(f"Closed {position_side} position")
                    
                    # Record in database
                    with get_db() as db:
                        position = db.query(Position).filter(
                            Position.symbol == self.symbol,
                            Position.position_side == position_side,
                            Position.is_active == True
                        ).first()
                        
                        if position:
                            position.is_active = False
                            position.closed_at = datetime.utcnow()
                            position.exit_price = float(close_result.get('avgPrice', 0))
                            position.hold_time_minutes = int(
                                (position.closed_at - position.opened_at).total_seconds() / 60
                            )
                            position.realized_pnl = float(close_result.get('realizedPnl', 0))
            
            # Small delay
            time.sleep(random.uniform(5, 10))
            
            # Open new positions
            self.active_positions = {}
            self._open_delta_neutral_pair()
            
        except Exception as e:
            logger.error(f"Rotation failed: {e}")
            raise
    
    def _check_and_close_risky_positions(self, positions: List[Dict]):
        """Close positions that exceed risk limits"""
        for pos in positions:
            if float(pos['positionAmt']) == 0:
                continue
            
            if self.risk_manager.should_close_position(pos):
                logger.warning(f"Closing risky position: {pos['positionSide']}")
                self.client.close_position(self.symbol, pos['positionSide'])
                
                if pos['positionSide'] in self.active_positions:
                    self.active_positions[pos['positionSide']]['is_active'] = False
    
    def _update_active_positions(self, positions: List[Dict]):
        """Update internal state from exchange positions"""
        for pos in positions:
            if float(pos['positionAmt']) == 0:
                if pos['positionSide'] in self.active_positions:
                    self.active_positions[pos['positionSide']]['is_active'] = False
    
    def _log_position_status(self):
        """Log current position status"""
        for pos_side, data in self.active_positions.items():
            if data.get('is_active'):
                opened_at = data.get('opened_at')
                if opened_at:
                    hold_time = (datetime.utcnow() - opened_at).total_seconds() / 60
                    logger.info(f"Position {pos_side}: held for {hold_time:.1f} minutes")
    
    def _log_daily_stats(self):
        """Log daily trading statistics"""
        with get_db() as db:
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            
            trades_today = db.query(Trade).filter(Trade.timestamp >= today_start).all()
            
            total_volume = sum(t.notional for t in trades_today)
            total_pnl = sum(t.realized_pnl for t in trades_today)
            total_fees = sum(t.commission for t in trades_today)
            
            logger.info(f"📊 Today's Stats: Volume=${total_volume:.2f} | PnL=${total_pnl:.2f} | Fees=${total_fees:.2f}")

