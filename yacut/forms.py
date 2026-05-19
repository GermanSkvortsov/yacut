"""Формы приложения YaCut."""

import re

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired, MultipleFileField
from wtforms import StringField, SubmitField
from wtforms.validators import (
    URL,
    DataRequired,
    Length,
    Optional,
    ValidationError,
)

from .constants import (
    ORIGINAL_MAX_LENGTH,
    SHORT_MAX_LENGTH,
    SHORT_MIN_LENGTH,
    VALID_SHORT_REGEX,
)


def validate_short_id(form, field):
    """Валидатор: короткий идентификатор — только латиница и цифры."""
    if field.data and not re.match(VALID_SHORT_REGEX, field.data):
        raise ValidationError('Указано недопустимое имя для короткой ссылки')


class URLForm(FlaskForm):
    """Форма для создания короткой ссылки."""

    original_link = StringField(
        'Длинная ссылка',
        validators=[
            DataRequired(message='Обязательное поле'),
            URL(message='Некорректный URL'),
            Length(max=ORIGINAL_MAX_LENGTH, message='Слишком длинная ссылка'),
        ]
    )
    custom_id = StringField(
        'Ваш вариант короткой ссылки',
        validators=[
            Length(
                min=SHORT_MIN_LENGTH,
                max=SHORT_MAX_LENGTH,
                message=f'Допустимая длина от {
                    SHORT_MIN_LENGTH} до {SHORT_MAX_LENGTH} символов'
            ),
            Optional(),
            validate_short_id,
        ]
    )
    submit = SubmitField('Создать')


class FileForm(FlaskForm):
    """Форма для загрузки файлов на Яндекс Диск."""

    files = MultipleFileField(
        'Выберите файлы',
        validators=[
            FileRequired(message='Выберите хотя бы один файл'),
            FileAllowed(
                ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'txt', 'pdf', 'zip'],
                'Недопустимый формат файла'
            )
        ]
    )
    submit = SubmitField('Загрузить')
