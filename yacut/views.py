"""Вьюхи приложения YaCut."""
# pyright: reportCallIssue=false

import asyncio

from flask import abort, flash, redirect, render_template, url_for

from . import app, db
from .forms import FileForm, URLForm
from .models import URLMap
from .utils import get_unique_short_id
from .yandex_disk import YandexDisk

FORBIDDEN_SHORT_IDS = ['files']


def _check_custom_id(custom_id):
    """Проверка, что custom_id не занят и не запрещён."""
    if custom_id in FORBIDDEN_SHORT_IDS:
        return False
    if URLMap.query.filter_by(short=custom_id).first():
        return False
    return True


def _save_url_map(original, short):
    """Создание и сохранение URLMap."""
    url_map = URLMap(original=original, short=short)
    db.session.add(url_map)
    db.session.commit()
    return url_map


@app.route('/', methods=['GET', 'POST'])
def index_view():
    """Главная страница: форма создания короткой ссылки."""
    form = URLForm()
    short_url = None

    if form.validate_on_submit():
        original = form.original_link.data
        custom_id = (form.custom_id.data or '').strip()

        if custom_id:
            if not _check_custom_id(custom_id):
                flash(
                    'Предложенный вариант короткой ссылки уже существует.'
                )
                return render_template('index.html', form=form)
            short = custom_id
        else:
            short = get_unique_short_id()

        _save_url_map(original, short)
        short_url = url_for(
            'redirect_to_url', short_id=short, _external=True
        )

    return render_template('index.html', form=form, short_url=short_url)


@app.route('/files', methods=['GET', 'POST'])
def files_view():
    """Страница загрузки файлов на Яндекс Диск."""
    form = FileForm()
    results = []

    if form.validate_on_submit():
        disk = YandexDisk(app.config['DISK_TOKEN'])
        files = form.files.data
        download_urls = asyncio.run(disk.upload_files(files))

        for file, download_url in zip(files, download_urls):
            short_id = get_unique_short_id()
            _save_url_map(download_url, short_id)
            results.append({
                'filename': file.filename,
                'short_url': url_for(
                    'redirect_to_url', short_id=short_id, _external=True
                )
            })

    return render_template('files.html', form=form, results=results)


@app.route('/<string:short_id>')
def redirect_to_url(short_id):
    """Переадресация на оригинальную ссылку по короткому идентификатору."""
    url_map = URLMap.query.filter_by(short=short_id).first()
    if url_map is None:
        abort(404)
    return redirect(url_map.original)
