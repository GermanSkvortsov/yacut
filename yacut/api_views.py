"""API-вьюхи сервиса YaCut."""

from http import HTTPStatus

from flask import jsonify, request, url_for

from . import app
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

    try:
        url_map = URLMap.create(original, custom_id)
    except ShortLinkCreationError as error:
        raise InvalidAPIUsage(str(error), HTTPStatus.BAD_REQUEST)

    return jsonify({
        'url': url_map.original,
        'short_link': url_for(
            'redirect_to_url', short_id=url_map.short, _external=True
        )
    }), HTTPStatus.CREATED


@app.route('/api/id/<string:short_id>/', methods=['GET'])
def get_original_link(short_id):
    """Получение оригинальной ссылки по короткому идентификатору."""
    url_map = URLMap.get_by_short(short_id)
    if url_map is None:
        raise InvalidAPIUsage(
            'Указанный id не найден', HTTPStatus.NOT_FOUND
        )
    return jsonify({'url': url_map.original}), HTTPStatus.OK
