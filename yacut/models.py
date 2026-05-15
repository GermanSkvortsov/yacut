"""Модели приложения YaCut."""

from datetime import datetime

from . import db


class URLMap(db.Model):
    """Модель для хранения соответствия короткой и оригинальной ссылок."""

    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(500), nullable=False)
    short = db.Column(db.String(16), unique=True, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Сериализация модели в словарь."""
        return {
            'url': self.original,
            'short_link': self.short
        }
