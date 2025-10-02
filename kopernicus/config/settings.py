from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    # Aster API
    aster_api_key: str
    aster_api_secret: str
    aster_base_url: str = "https://fapi.asterdex.com"
    aster_ws_url: str = "wss://fstream.asterdex.com"
    
    # Wallet
    wallet_address: str
    # private_key: str  # Add later for Web3 integration
    
    # Trading
    referral_code: str = "KoPPFo"
    capital_usdt: float = 1000.0
    leverage: int = 15
    position_hold_time_min: int = 90  # minutes
    daily_volume_target: float = 15000.0
    max_position_size_pct: float = 1.5
    trading_pairs: List[str] = ["BTCUSDT"]
    
    # Risk Management
    max_drawdown_pct: float = 5.0
    max_pnl_drift_pct: float = 0.8
    stop_loss_pct: float = 1.0
    funding_rate_threshold: float = 0.05
    
    # Database
    db_path: str = "kopernicus.db"
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()

