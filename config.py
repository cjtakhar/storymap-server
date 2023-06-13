import os
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy

class Config:
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CORS_ORIGINS = ['http://localhost:3000', 'https://cjtakhar.github.io']

load_dotenv()

# You can create an instance of the SQLAlchemy class for working with your database
db = SQLAlchemy()
