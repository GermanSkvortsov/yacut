"""Модели приложения YaCut."""

import random
import string
from datetime import datetime, timezone

from flask import url_for

from . import db
from .constants import (
    FORBIDDEN_SHORT_IDS,
    ORIGINAL_MAX_LENGTH,
    SHORT_AUTO_LENGTH,
    SHORT_MAX_LENGTH,
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
    timestamp = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self, fields=None, external=False):
        """Сериализация модели в словарь.

        Параметр fields позволяет выбрать нужные поля (например, {'url'}).
        Если fields не указан — возвращаются все поля.
        Параметр external управляет генерацией абсолютного URL для short_link.
        """
        result = {
            'url': self.original,
            'short_link': url_for(
                'redirect_to_url',
                short_id=self.short,
                _external=external,
            ),
        }
        if fields is not None:
            return {
                key: value
                for key, value in result.items()
                if key in fields
            }
        return result

    @staticmethod
    def get_by_short(short_id):
        """Получить объект по короткому идентификатору или None."""
        return URLMap.query.filter_by(short=short_id).first()

    @staticmethod
    def is_short_taken(short_id):
        """Проверить, занят ли короткий идентификатор."""
        return (
            short_id in FORBIDDEN_SHORT_IDS
            or URLMap.get_by_short(short_id) is not None
        )

    @staticmethod
    def create(original, custom_id=None):
        """Создать короткую ссылку (микро-ORM).

        При проблемах с занятостью custom_id бросает ShortLinkCreationError.
        """
        if custom_id:
            custom_id = custom_id.strip()
            if URLMap.is_short_taken(custom_id):
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
            if not URLMap.is_short_taken(short_id):
                return short_id
