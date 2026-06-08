import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'aapni-secret-key-123'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://user:pass@host/db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
