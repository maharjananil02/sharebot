"""Configuration management for the trading bot"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration"""
    NEPSE_USERNAME = os.getenv("NEPSE_USERNAME", "")
    NEPSE_PASSWORD = os.getenv("NEPSE_PASSWORD", "")
    NEPSE_LOGIN_URL = os.getenv("NEPSE_LOGIN_URL", "https://tms17.nepsetms.com.np/login")
    
    # Browser settings
    HEADLESS_MODE = os.getenv("HEADLESS_MODE", "False").lower() == "true"
    IMPLICIT_WAIT = int(os.getenv("IMPLICIT_WAIT", "10"))
    
    # Trading settings
    TRADING_ENABLED = os.getenv("TRADING_ENABLED", "False").lower() == "true"
    DEMO_MODE = os.getenv("DEMO_MODE", "True").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    DEMO_MODE = True
    TRADING_ENABLED = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

def get_config():
    """Get configuration based on environment"""
    env = os.getenv("ENV", "development").lower()
    if env == "production":
        return ProductionConfig()
    return DevelopmentConfig()
