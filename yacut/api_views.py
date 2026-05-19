"""API-вьюхи сервиса YaCut."""

import re
from http import HTTPStatus

from flask import jsonify, request, url_for

from . import app
from .constants import (
    ORIGINAL_MAX_LENGTH,
    SHORT_MAX_LENGTH,
    SHORT_MIN_LENGTH,
    VALID_SHORT_REGEX,
)
from .error_handlers import InvalidAPIUsage
from .models import ShortLinkCreationError, URLMap


@app.route('/api/id/', methods=['POST'])
def create_short_link():
    """Создание короткой ссылки. Принимает JSON с полями url и custom_id."""
    if not request.data:
        raise InvalidAPIUsage(
            'Отсутствует тело запроса', HTTPStatus.BAD_REQUEST
        )

    data = request.get_json(silent=True)
    if data is None:
        raise InvalidAPIUsage(
            'Отсутствует тело запроса', HTTPStatus.BAD_REQUEST
        )

    if 'url' not in data:
        raise InvalidAPIUsage(
            '"url" является обязательным полем!', HTTPStatus.BAD_REQUEST
        )

    original = data['url']
    custom_id = data.get('custom_id')

    if len(original) > ORIGINAL_MAX_LENGTH:
        raise InvalidAPIUsage(
            f'Длина URL не должна превышать {ORIGINAL_MAX_LENGTH} символов',
            HTTPStatus.BAD_REQUEST,
        )

    if custom_id:
        custom_id = custom_id.strip()
        if not re.match(VALID_SHORT_REGEX, custom_id):
            raise InvalidAPIUsage(
                'Указано недопустимое имя для короткой ссылки',
                HTTPStatus.BAD_REQUEST,
            )
        if (
            len(custom_id) < SHORT_MIN_LENGTH
            or len(custom_id) > SHORT_MAX_LENGTH
        ):
            raise InvalidAPIUsage(
                'Указано недопустимое имя для короткой ссылки',
                HTTPStatus.BAD_REQUEST,
            )

    try:
        url_map = URLMap.create(original, custom_id)
    except ShortLinkCreationError as error:
        raise InvalidAPIUsage(str(error), HTTPStatus.BAD_REQUEST)

    data = url_map.to_dict()
    data['short_link'] = url_for(
        'redirect_to_url', short_id=data['short_link'], _external=True
    )
    return jsonify(data), HTTPStatus.CREATED


@app.route('/api/id/<string:short_id>/', methods=['GET'])
def get_original_link(short_id):
    """Получение оригинальной ссылки по короткому идентификатору."""
    url_map = URLMap.get_by_short(short_id)
    if url_map is None:
        raise InvalidAPIUsage(
            'Указанный id не найден', HTTPStatus.NOT_FOUND
        )
    return jsonify(url_map.to_dict(fields={'url'})), HTTPStatus.OK
