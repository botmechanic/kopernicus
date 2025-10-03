from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Trade(Base):
    __tablename__ = 'trades'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    symbol = Column(String, nullable=False)
    side = Column(String, nullable=False)  # BUY/SELL
    position_side = Column(String, nullable=False)  # LONG/SHORT
    order_type = Column(String, default="MARKET")
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    notional = Column(Float, nullable=False)  # qty * price
    order_id = Column(String, unique=True)
    realized_pnl = Column(Float, default=0.0)
    commission = Column(Float, default=0.0)
    status = Column(String, default="FILLED")
    
    def __repr__(self):
        return f"<Trade {self.symbol} {self.side} {self.quantity} @ {self.price}>"

class Position(Base):
    __tablename__ = 'positions'
    
    id = Column(Integer, primary_key=True)
    opened_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)
    symbol = Column(String, nullable=False)
    position_side = Column(String, nullable=False)
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=True)
    quantity = Column(Float, nullable=False)
    leverage = Column(Integer, nullable=False)
    notional = Column(Float, nullable=False)
    hold_time_minutes = Column(Integer, default=0)
    realized_pnl = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<Position {self.symbol} {self.position_side} {self.quantity}>"

class DailyStats(Base):
    __tablename__ = 'daily_stats'
    
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.utcnow)
    total_volume = Column(Float, default=0.0)
    num_trades = Column(Integer, default=0)
    realized_pnl = Column(Float, default=0.0)
    fees_paid = Column(Float, default=0.0)
    rh_points_estimated = Column(Float, default=0.0)

