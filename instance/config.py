import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@localhost:5432/NotepadDB'
    CKEDITOR_PKG_TYPE = 'full-all'
    JWT_SECRET_KEY = 'thisissecretkey'
    JWT_ACCESS_COOKIE_PATH = '/'
    JWT_REFRESH_COOKIE_PATH = '/token/refresh'
    JWT_COOKIE_SECURE = True
    JWT_TOKEN_LOCATION = ['cookies']
    JWT_COOKIE_CSRF_PROTECT = False
    JWT_ACCESS_TOKEN_EXPIRES = 5 * 60  # 5 minutes
    JWT_REFRESH_TOKEN_EXPIRES = 7 * 24 * 60 * 60  # 7 days 