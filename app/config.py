"""
Configuration settings for QI-Guard Stellar MVP using Pydantic Settings.
"""

from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "QI-Guard for Stellar"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/v1"
    
    # Security
    SECRET_KEY: str = "qi-guard-super-secret-development-key-change-in-production-2026"
    
    # Database & Cache
    DATABASE_URL: str = "sqlite+aiosqlite:///./qiguard.db"  # Default SQLite for dev, overridden by Postgres
    REDIS_URL: Optional[str] = "redis://localhost:6379/0"
    
    # Stellar & Soroban RPC Nodes
    STELLAR_HORIZON_URL: str = "https://horizon-testnet.stellar.org"
    SOROBAN_RPC_URL: str = "https://soroban-testnet.stellar.org"
    
    # Access Tier Limits (Analyses per month)
    LIMIT_DEVELOPER_CONTRACTS: int = 50
    LIMIT_DEVELOPER_ADDRESSES: int = 100
    LIMIT_BUILDER_CONTRACTS: int = 500
    LIMIT_BUILDER_ADDRESSES: int = 2000
    LIMIT_PROTOCOL_CONTRACTS: int = -1  # Unlimited
    LIMIT_PROTOCOL_ADDRESSES: int = 20000

    # Stripe & Billing
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    STRIPE_PRICE_ID_BUILDER: str = "price_builder_monthly"
    STRIPE_PRICE_ID_PROTOCOL: str = "price_protocol_monthly"
    DASHBOARD_URL: str = "http://localhost:3000"

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
