import os

class Config:
    UPLOAD_FOLDER = 'app/static'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    # Add other configuration variables as needed
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/mentalhealth_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False