import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@localhost:5432/NotepadDB'
    CKEDITOR_PKG_TYPE = 'full-all'