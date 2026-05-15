"""Обработчики ошибок приложения YaCut."""

from flask import jsonify, render_template, request

from . import app, db


class InvalidAPIUsage(Exception):
    """Кастомное исключение для ошибок API."""

    status_code = 400

    def __init__(self, message, status_code=None):
        """Инициализация исключения с сообщением и статус-кодом."""
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code

    def to_dict(self):
        """Сериализация сообщения об ошибке в словарь."""
        return {'message': self.message}


@app.errorhandler(InvalidAPIUsage)
def invalid_api_usage(error):
    """Обработчик кастомного исключения API. Возвращает JSON."""
    return jsonify(error.to_dict()), error.status_code


@app.errorhandler(404)
def page_not_found(error):
    """Обработчик ошибки 404. Для API — JSON, для сайта — HTML."""
    if request.path.startswith('/api/'):
        return jsonify({'message': 'Указанный id не найден'}), 404
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """Обработчик ошибки 500. Откат БД и HTML-страница."""
    db.session.rollback()
    return render_template('500.html'), 500
