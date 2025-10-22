"""
Configuration settings for BinkRead application.
"""

import os
from typing import Dict, Any


class Config:
    """Base configuration class."""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # File upload settings
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'pdf'}
    
    # AI Model settings
    MODEL_NAME = 'facebook/bart-large-cnn'
    CHUNK_SIZE = 4000
    MAX_TOKENS = 1024
    SUMMARY_MAX_LENGTH = 300
    SUMMARY_MIN_LENGTH = 100
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    @staticmethod
    def get_model_config() -> Dict[str, Any]:
        """Get model configuration."""
        return {
            'model_name': Config.MODEL_NAME,
            'chunk_size': Config.CHUNK_SIZE,
            'max_tokens': Config.MAX_TOKENS,
            'summary_max_length': Config.SUMMARY_MAX_LENGTH,
            'summary_min_length': Config.SUMMARY_MIN_LENGTH
        }


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    LOG_LEVEL = 'WARNING'
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable must be set in production")


# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

