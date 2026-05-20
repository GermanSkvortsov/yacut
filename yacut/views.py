"""Вьюхи приложения YaCut."""

import asyncio

from flask import flash, redirect, render_template

from . import app
from .constants import FILES_SHORT_ID
from .forms import FileForm, URLForm
from .models import ShortLinkCreationError, URLMap
from .yandex_disk import YandexDisk


@app.route('/', methods=['GET', 'POST'])
def index_view():
    """Главная страница: форма создания короткой ссылки."""
    form = URLForm()
    if not form.validate_on_submit():
        return render_template('index.html', form=form)

    original = form.original_link.data
    custom_id = (form.custom_id.data or '').strip() or None

    try:
        url_map = URLMap.create(original, custom_id)
    except ShortLinkCreationError as error:
        flash(str(error))
        return render_template('index.html', form=form)

    short_url = url_map.to_dict(external=True)['short_link']
    return render_template(
        'index.html', form=form, short_url=short_url
    )


@app.route('/' + FILES_SHORT_ID, methods=['GET', 'POST'])
def files_view():
    """Страница загрузки файлов на Яндекс Диск."""
    form = FileForm()
    if not form.validate_on_submit():
        return render_template('files.html', form=form)

    disk = YandexDisk(app.config['DISK_TOKEN'])
    files = form.files.data
    download_urls = asyncio.run(disk.upload_files(files))
    results = []

    for file, download_url in zip(files, download_urls):
        try:
            url_map = URLMap.create(download_url)
        except ShortLinkCreationError:
            continue
        results.append({
            'filename': file.filename,
            'short_url': url_map.to_dict(external=True)['short_link'],
        })

    return render_template('files.html', form=form, results=results)


@app.route('/<string:short_id>')
def redirect_to_url(short_id):
    """Переадресация на оригинальную ссылку по короткому идентификатору."""
    url_map = URLMap.query.filter_by(short=short_id).first_or_404()
    return redirect(url_map.original)
