"""Конфигурация приложения YaCut."""

import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Класс конфигурации Flask-приложения."""

    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key-for-tests')
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URI', 'sqlite:///db.sqlite3'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DISK_TOKEN = os.getenv('DISK_TOKEN', '')
