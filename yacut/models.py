"""Модели приложения YaCut."""

import random
import re
import string
from datetime import datetime

from . import db
from .constants import (
    FORBIDDEN_SHORT_IDS,
    ORIGINAL_MAX_LENGTH,
    SHORT_AUTO_LENGTH,
    SHORT_MAX_LENGTH,
    VALID_SHORT_REGEX,
)


class ShortLinkCreationError(Exception):
    """Исключение при ошибке создания короткой ссылки."""
    pass


class URLMap(db.Model):
    """Модель для хранения соответствия короткой и оригинальной ссылок."""

    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(
        db.String(ORIGINAL_MAX_LENGTH), nullable=False
    )
    short = db.Column(
        db.String(SHORT_MAX_LENGTH), unique=True, nullable=False
    )
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Сериализация модели в словарь."""
        return {
            'url': self.original,
            'short_link': self.short
        }

    @staticmethod
    def get_by_short(short_id):
        """Получить объект по короткому идентификатору или None."""
        return URLMap.query.filter_by(short=short_id).first()

    @staticmethod
    def create(original, custom_id=None):
        """Создать короткую ссылку (микро-ORM).

        Проверяет custom_id, генерирует short, сохраняет в БД.
        При проблемах бросает ShortLinkCreationError.
        """
        if custom_id:
            custom_id = custom_id.strip()
            if not re.match(VALID_SHORT_REGEX, custom_id):
                raise ShortLinkCreationError(
                    'Указано недопустимое имя для короткой ссылки'
                )
            if len(custom_id) > SHORT_MAX_LENGTH or len(custom_id) < 1:
                raise ShortLinkCreationError(
                    'Указано недопустимое имя для короткой ссылки'
                )
            if custom_id in FORBIDDEN_SHORT_IDS:
                raise ShortLinkCreationError(
                    'Предложенный вариант короткой ссылки уже существует.'
                )
            if URLMap.query.filter_by(short=custom_id).first():
                raise ShortLinkCreationError(
                    'Предложенный вариант короткой ссылки уже существует.'
                )
            short = custom_id
        else:
            short = URLMap._generate_short_id()

        url_map = URLMap(original=original, short=short)  # type: ignore
        db.session.add(url_map)
        db.session.commit()
        return url_map

    @staticmethod
    def _generate_short_id():
        """Сгенерировать уникальный короткий идентификатор."""
        chars = string.ascii_letters + string.digits
        while True:
            short_id = ''.join(
                random.choices(chars, k=SHORT_AUTO_LENGTH)
            )
            if short_id not in FORBIDDEN_SHORT_IDS:
                if not URLMap.query.filter_by(short=short_id).first():
                    return short_id
