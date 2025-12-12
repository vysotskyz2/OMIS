import os
from datetime import timedelta

# Flask Configuration
DEBUG = True
TESTING = False

# Database
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///adaptive_ui.db')
DATABASE_PATH = 'adaptive_ui.db'

# Session Configuration
PERMANENT_SESSION_LIFETIME = timedelta(days=7)
SESSION_COOKIE_SECURE = False  
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# Security
SECRET_KEY = os.getenv('SECRET_KEY', 'secret')

# ML Model Configuration
ML_MODEL_ACCURACY_TARGET = 0.85
ML_MODEL_PATH = 'models/ml_model.pkl'

# Feature Flags
ENABLE_ML_PREDICTIONS = True
ENABLE_A_B_TESTING = True
ENABLE_ANALYTICS = True

# API Configuration
API_PREFIX = '/api'
API_VERSION = '1.0'

# Logging
LOG_LEVEL = 'INFO'
LOG_FILE = 'logs/app.log'

# Server
HOST = '0.0.0.0'
PORT = 5000

print("[CONFIG] Settings loaded")
