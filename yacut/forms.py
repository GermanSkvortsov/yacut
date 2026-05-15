"""Формы приложения YaCut."""

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired, MultipleFileField
from wtforms import StringField, SubmitField
from wtforms.validators import URL, DataRequired, Length, Optional


class URLForm(FlaskForm):
    """Форма для создания короткой ссылки."""

    original_link = StringField(
        'Длинная ссылка',
        validators=[DataRequired(message='Обязательное поле'), URL()]
    )
    custom_id = StringField(
        'Ваш вариант короткой ссылки',
        validators=[Length(max=16), Optional()]
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
