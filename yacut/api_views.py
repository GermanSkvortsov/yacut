"""API-вьюхи сервиса YaCut."""

from flask import abort, jsonify, request, url_for

from . import app, db
from .error_handlers import InvalidAPIUsage
from .models import URLMap
from .utils import get_unique_short_id, validate_short_id

FORBIDDEN_SHORT_IDS = ['files']


@app.route('/api/id/', methods=['POST'])
def create_short_link():
    """Создание короткой ссылки. Принимает JSON с полями url и custom_id."""
    if not request.data:
        raise InvalidAPIUsage('Отсутствует тело запроса', 400)

    data = request.get_json(silent=True)
    if data is None:
        raise InvalidAPIUsage('Отсутствует тело запроса', 400)

    if 'url' not in data:
        raise InvalidAPIUsage('"url" является обязательным полем!', 400)

    original = data['url']
    custom_id = data.get('custom_id')

    if custom_id:
        custom_id = custom_id.strip()
        if len(custom_id) > 16:
            raise InvalidAPIUsage(
                'Указано недопустимое имя для короткой ссылки', 400
            )
        if not validate_short_id(custom_id):
            raise InvalidAPIUsage(
                'Указано недопустимое имя для короткой ссылки', 400
            )
        if custom_id in FORBIDDEN_SHORT_IDS:
            raise InvalidAPIUsage(
                'Предложенный вариант короткой ссылки уже существует.', 400
            )
        if URLMap.query.filter_by(short=custom_id).first():
            raise InvalidAPIUsage(
                'Предложенный вариант короткой ссылки уже существует.', 400
            )
        short = custom_id
    else:
        short = get_unique_short_id()

    url_map = URLMap(original=original, short=short)  # type: ignore
    db.session.add(url_map)
    db.session.commit()

    return jsonify({
        'url': original,
        'short_link': url_for(
            'redirect_to_url', short_id=short, _external=True
        )
    }), 201


@app.route('/api/id/<string:short_id>/', methods=['GET'])
def get_original_link(short_id):
    """Получение оригинальной ссылки по короткому идентификатору."""
    url_map = URLMap.query.filter_by(short=short_id).first()
    if url_map is None:
        abort(404)
    return jsonify({'url': url_map.original}), 200
