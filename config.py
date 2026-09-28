import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Application configuration parameters."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'customer-feedback-dashboard-secret-key-bca-2026')
    DATABASE_PATH = os.path.join(BASE_DIR, 'database', 'feedback.db')
    ITEMS_PER_PAGE = 10
    DEBUG = True
