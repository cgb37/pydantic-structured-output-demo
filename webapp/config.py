"""Configuration module for the Quart application."""
import os
from typing import Type


class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = False
    TESTING = False
    
    # Database configuration (for future use)
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    # AI/LLM configuration
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    LLM_MODEL = os.environ.get('LLM_MODEL', 'gpt-3.5-turbo')
    
    # Application settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file upload


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    
    # Development-specific settings
    CORS_ENABLED = True
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    
    # Production-specific settings
    CORS_ENABLED = False
    LOG_LEVEL = 'INFO'
    
    # Use environment variable for secret key in production
    SECRET_KEY = os.environ.get('SECRET_KEY') or None
    
    def __init__(self):
        if not self.SECRET_KEY:
            raise ValueError("SECRET_KEY environment variable must be set in production")


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    
    # Testing-specific settings
    WTF_CSRF_ENABLED = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config() -> Type[Config]:
    """Get configuration based on environment."""
    env = os.environ.get('QUART_ENV', 'default')
    return config.get(env, config['default'])
