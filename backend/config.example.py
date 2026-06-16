# Flask Configuration
FLASK_ENV = 'development'
DEBUG = True
TESTING = False

# Database Configuration
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://user:password@localhost:3306/prediction_db'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# API Keys
API_KEY_SPORTS = 'your_sports_api_key'
API_KEY_CRYPTO = 'your_crypto_api_key'
API_KEY_WEATHER = 'your_weather_api_key'

# Redis Configuration
REDIS_URL = 'redis://localhost:6379/0'

# Celery Configuration
CELERY_BROKER_URL = 'redis://localhost:6379/1'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'

# Logging
LOG_LEVEL = 'INFO'
LOG_FILE = 'logs/app.log'

# Server Configuration
HOST = '0.0.0.0'
PORT = 5000
SECRET_KEY = 'your-secret-key-here-change-in-production'

# CORS Configuration
CORS_ORIGINS = ['http://localhost:3000', 'http://localhost:5000']

# Cache Configuration
CACHE_TYPE = 'redis'
CACHE_REDIS_URL = 'redis://localhost:6379/0'
CACHE_DEFAULT_TIMEOUT = 300

# Data Configuration
DATA_DIR = './data'
CACHE_DIR = './data/cache'
HISTORY_DIR = './data/history'