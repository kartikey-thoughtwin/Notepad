import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@localhost:5432/NotepadDB'
    CKEDITOR_PKG_TYPE = 'full-all'
    JWT_SECRET_KEY = 'thisissecretkey'
    JWT_ACCESS_COOKIE_PATH = '/'
    JWT_REFRESH_COOKIE_PATH = '/'
    JWT_COOKIE_SECURE = True
    # JWT_COOKIE_SAMESITE = 'None'