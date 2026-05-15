"""Вспомогательные утилиты приложения YaCut."""

import random
import re
import string

from .models import URLMap


def get_unique_short_id(length=6):
    """Генерирует уникальный короткий идентификатор заданной длины."""
    chars = string.ascii_letters + string.digits
    while True:
        short_id = ''.join(random.choice(chars) for _ in range(length))
        if not URLMap.query.filter_by(short=short_id).first():
            return short_id


def validate_short_id(short_id):
    """Проверяет, что short_id содержит только латиницу и цифры."""
    return bool(re.match(r'^[a-zA-Z0-9]+$', short_id))
